"""Enhanced AEAD Engine (Authenticated Encryption with Associated Data).

This module implements `AEADEngine`, providing modular, deterministic, research-grade AEAD authenticated
encryption and decryption combining Cellular Automata (CA) keystream encryption, Phase 2.2 Key Evolution
key separation, bounded nonce management, and constant-time canonical authentication tags.

Architecture & Pipeline:
                               Master Key
                                   │
                                   ▼
                           KeyEvolutionEngine
                                   │
             ┌─────────────────────┼─────────────────────┬─────────────────────┐
             ▼                     ▼                     ▼                     ▼
       Encryption Key          Auth Key               CA Key               Nonce Key
             │                     │                     │                     │
             └─────────────┬───────┴─────────────────────┘                     │
                           ▼                                                   │
                  Dynamic CA Keystream ◄───────────────────────────────────────┘
                           │
                           ▼
                  Plaintext XOR Keystream
                           │
                           ▼
                       Ciphertext
                           │
                           ▼
                   AuthenticationTag
        (Canonical Frame: Version || NonceLen || Nonce || AADLen || AAD || CTLen || CT)
"""

import hmac
import hashlib
from typing import Any, BinaryIO, Dict, Optional, Union

from crypto.ca.dynamic_rules import DynamicRuleEngine
from crypto.ca.evolution import DynamicEvolutionEngine, BOUNDARY_PERIODIC
from crypto.ca.optimizer import OptimizedCAEngine
from .auth import AEADAuthenticationError, AuthenticationTag, DEFAULT_TAG_LENGTH
from .nonce import AEADError, InvalidNonceError, NonceManager
from .streaming import StreamingAEAD, StreamCorruptedError

BytesLike = Union[bytes, bytearray, memoryview]


class AEADEngine:
    """Enhanced AEAD (Authenticated Encryption with Associated Data) Engine."""

    def __init__(
        self,
        key_engine: Optional[Any] = None,
        ca_engine: Optional[OptimizedCAEngine] = None,
        nonce_manager: Optional[NonceManager] = None,
    ) -> None:
        """Initialize AEADEngine.

        Args:
            key_engine: KeyEvolutionEngine instance (creates default if None).
            ca_engine: OptimizedCAEngine instance (creates default if None).
            nonce_manager: NonceManager instance (creates default if None).
        """
        if key_engine is None:
            from crypto.key.evolution import KeyEvolutionEngine
            self.key_engine: Any = KeyEvolutionEngine()
        else:
            self.key_engine = key_engine
        self.ca_engine: OptimizedCAEngine = ca_engine if ca_engine is not None else OptimizedCAEngine()
        self.nonce_manager: NonceManager = nonce_manager if nonce_manager is not None else NonceManager()
        self.streaming_engine: StreamingAEAD = StreamingAEAD(key_engine=self.key_engine)
        self.dyn_ca_engine: DynamicEvolutionEngine = DynamicEvolutionEngine()
        self._encryption_count: int = 0

    def _normalize_bytes(self, data: Optional[BytesLike], name: str = "Data") -> bytes:
        """Normalize BytesLike input (bytes, bytearray, memoryview) into bytes.

        Args:
            data: Input data buffer.
            name: Parameter name for error messages.

        Returns:
            bytes: Binary bytes object.

        Raises:
            AEADError: If input is not bytes-like.
        """
        if data is None:
            return b""
        if isinstance(data, memoryview):
            return data.tobytes()
        if isinstance(data, (bytes, bytearray)):
            return bytes(data)
        raise AEADError(f"{name} must be a bytes-like object (bytes, bytearray, memoryview), got {type(data).__name__}")

    def _generate_keystream(self, master_key: bytes, nonce: bytes, length: int) -> bytes:
        """Generate pseudo-random CA keystream bytes of specified length.

        Derives `encryption_key`, `ca_key`, and `nonce_key` from master_key, then
        combines them to seed CA state vector evolution.

        Args:
            master_key: Master key bytes.
            nonce: Nonce bytes.
            length: Number of keystream bytes to generate.

        Returns:
            bytes: Pseudo-random keystream bytes.
        """
        enc_key = self.key_engine.derive_encryption_key(master_key)
        ca_key = self.key_engine.derive_ca_key(master_key, ca_id=30)
        nonce_key = self.key_engine.derive_nonce_key(master_key)

        # Seed PRK combining subkeys + nonce
        prk_seed = hmac.new(enc_key, nonce + ca_key + nonce_key, hashlib.sha256).digest()

        # Generates keystream block-by-block using CA-seeded pseudorandom expansion
        keystream = bytearray()
        block_counter = 0
        while len(keystream) < length:
            block_info = prk_seed + block_counter.to_bytes(8, byteorder="big")
            block_seed = hashlib.sha256(block_info).digest()
            # Fast CA step evolution over 32-byte (256-bit) state vector
            ca_state = [ (block_seed[i // 8] >> (7 - (i % 8))) & 1 for i in range(256) ]
            evolved = self.ca_engine.evolve_fast(ca_state, rule=30, generations=5, boundary=BOUNDARY_PERIODIC)
            # Pack evolved bits back to 32 bytes
            block_bytes = bytearray(32)
            for i, bit in enumerate(evolved):
                if bit:
                    block_bytes[i // 8] |= (1 << (7 - (i % 8)))
            keystream.extend(block_bytes)
            block_counter += 1

        return bytes(keystream[:length])

    def encrypt(
        self,
        plaintext: BytesLike,
        master_key: bytes,
        aad: Optional[BytesLike] = None,
        nonce: Optional[bytes] = None,
        tag_length: int = DEFAULT_TAG_LENGTH,
        check_nonce_reuse: bool = True,
    ) -> Dict[str, bytes]:
        """Perform authenticated encryption with Associated Data (AAD).

        Args:
            plaintext: Plaintext buffer (bytes, bytearray, memoryview).
            master_key: Secret master key bytes (>= 16 bytes).
            aad: Optional Associated Data buffer.
            nonce: Optional explicit nonce bytes (12 bytes). Generated automatically if None.
            tag_length: Desired tag length in bytes (16 or 32, defaults to 16).
            check_nonce_reuse: If True, checks and registers nonce in NonceManager to prevent reuse.

        Returns:
            Dict[str, bytes]: Dictionary containing `{"ciphertext": bytes, "tag": bytes, "nonce": bytes}`.

        Raises:
            AEADError: If inputs, keys, or nonces are invalid or reused.
        """
        pt_bytes = self._normalize_bytes(plaintext, "Plaintext")
        aad_bytes = self._normalize_bytes(aad, "AAD")
        m_key = self.key_engine._validate_master_key(master_key)

        if nonce is None:
            n_bytes = self.nonce_manager.generate(length=12, check_reuse=check_nonce_reuse)
        else:
            n_bytes = self.nonce_manager.validate(nonce)
            if check_nonce_reuse:
                self.nonce_manager.register(n_bytes)

        auth_key = self.key_engine.derive_auth_key(m_key)

        # Generate CA keystream and compute Ciphertext = Plaintext XOR Keystream
        keystream = self._generate_keystream(m_key, n_bytes, len(pt_bytes))
        ct_bytes = bytes(p ^ k for p, k in zip(pt_bytes, keystream))

        # Generate Canonical Authentication Tag
        tag_bytes = AuthenticationTag.generate(
            auth_key=auth_key,
            ciphertext=ct_bytes,
            nonce=n_bytes,
            aad=aad_bytes,
            tag_length=tag_length,
        )

        self._encryption_count += 1
        return {
            "ciphertext": ct_bytes,
            "tag": tag_bytes,
            "nonce": n_bytes,
        }

    def decrypt(
        self,
        ciphertext: BytesLike,
        tag: bytes,
        master_key: bytes,
        nonce: bytes,
        aad: Optional[BytesLike] = None,
    ) -> bytes:
        """Perform authenticated decryption and constant-time tag verification.

        Args:
            ciphertext: Ciphertext buffer (bytes, bytearray, memoryview).
            tag: Authentication tag bytes (16 or 32 bytes).
            master_key: Secret master key bytes.
            nonce: Nonce bytes.
            aad: Optional Associated Data buffer.

        Returns:
            bytes: Decrypted plaintext bytes.

        Raises:
            AEADAuthenticationError: Uniform exception raised if tag verification fails or payload is corrupted.
        """
        ct_bytes = self._normalize_bytes(ciphertext, "Ciphertext")
        aad_bytes = self._normalize_bytes(aad, "AAD")
        
        try:
            m_key = self.key_engine._validate_master_key(master_key)
            n_bytes = self.nonce_manager.validate(nonce)
        except Exception as err:
            raise AEADAuthenticationError(f"AEAD authentication failed: invalid parameters: {err}") from err

        auth_key = self.key_engine.derive_auth_key(m_key)

        # Constant-time tag verification
        is_valid = AuthenticationTag.verify(
            auth_key=auth_key,
            ciphertext=ct_bytes,
            nonce=n_bytes,
            expected_tag=tag,
            aad=aad_bytes,
            raise_on_failure=False,
        )

        if not is_valid:
            raise AEADAuthenticationError("AEAD authentication failed: corrupted ciphertext, bad AAD, or invalid tag")

        # Generate CA keystream and compute Plaintext = Ciphertext XOR Keystream
        keystream = self._generate_keystream(m_key, n_bytes, len(ct_bytes))
        pt_bytes = bytes(c ^ k for c, k in zip(ct_bytes, keystream))

        return pt_bytes

    def encrypt_stream(
        self,
        input_stream: BinaryIO,
        output_stream: BinaryIO,
        master_key: bytes,
        nonce: Optional[bytes] = None,
        aad: Optional[bytes] = None,
        chunk_size: int = 65536,
    ) -> Dict[str, Any]:
        """Perform streaming AEAD encryption for large files/streams.

        Args:
            input_stream: Readable binary stream.
            output_stream: Writable binary stream.
            master_key: Master key bytes.
            nonce: Optional nonce bytes (generated if None).
            aad: Optional Associated Data bytes.
            chunk_size: Chunk size in bytes (defaults to 64 KB).

        Returns:
            Dict[str, Any]: Execution summary dictionary.
        """
        n_bytes = nonce if nonce is not None else self.nonce_manager.generate(length=12)
        return self.streaming_engine.encrypt_stream(
            input_stream=input_stream,
            output_stream=output_stream,
            master_key=master_key,
            nonce=n_bytes,
            aad=aad,
            chunk_size=chunk_size,
        )

    def decrypt_stream(
        self,
        input_stream: BinaryIO,
        output_stream: BinaryIO,
        master_key: bytes,
        aad: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Perform streaming AEAD decryption and tag verification for large files/streams.

        Args:
            input_stream: Readable binary stream.
            output_stream: Writable binary stream.
            master_key: Master key bytes.
            aad: Optional Associated Data bytes.

        Returns:
            Dict[str, Any]: Execution summary dictionary.
        """
        return self.streaming_engine.decrypt_stream(
            input_stream=input_stream,
            output_stream=output_stream,
            master_key=master_key,
            aad=aad,
        )

    def generate_tag(
        self,
        auth_key: bytes,
        ciphertext: bytes,
        nonce: bytes,
        aad: Optional[bytes] = None,
        tag_length: int = DEFAULT_TAG_LENGTH,
    ) -> bytes:
        """Generate a canonical AEAD authentication tag directly.

        Args:
            auth_key: Authentication key bytes.
            ciphertext: Ciphertext bytes.
            nonce: Nonce bytes.
            aad: Optional Associated Data bytes.
            tag_length: Tag length (16 or 32 bytes).

        Returns:
            bytes: Generated authentication tag.
        """
        return AuthenticationTag.generate(auth_key, ciphertext, nonce, aad, tag_length)

    def verify_tag(
        self,
        auth_key: bytes,
        ciphertext: bytes,
        nonce: bytes,
        expected_tag: bytes,
        aad: Optional[bytes] = None,
    ) -> bool:
        """Verify an AEAD authentication tag in constant time.

        Args:
            auth_key: Authentication key bytes.
            ciphertext: Ciphertext bytes.
            nonce: Nonce bytes.
            expected_tag: Expected tag bytes.
            aad: Optional Associated Data bytes.

        Returns:
            bool: True if valid.
        """
        return AuthenticationTag.verify(auth_key, ciphertext, nonce, expected_tag, aad, raise_on_failure=False)

    def export_state(self) -> Dict[str, Any]:
        """Export engine state metadata.

        Returns:
            Dict[str, Any]: Engine state dictionary.
        """
        return {
            "encryption_count": self._encryption_count,
            "nonce_manager": self.nonce_manager.export_state(),
            "key_engine": self.key_engine.export_state(),
        }
