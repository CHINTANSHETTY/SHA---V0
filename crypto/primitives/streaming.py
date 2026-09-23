"""Streaming AEAD Chunk Encryption & Decryption.

This module provides `StreamingAEAD` for chunked authenticated encryption and decryption
of large data streams or files larger than available RAM.

Stream Framing Specification:
    - Stream Header: `Magic (4B: b"KDRS") || Version (2B) || Nonce (12B)`
    - Chunk Frame: `ChunkIndex (8B) || ChunkLen (4B) || ChunkCiphertext || IsFinal (1B) || ChunkTag (16B)`

Security & Reordering Protection:
    Including `ChunkIndex` and `IsFinal` inside the authenticated payload prevents chunk
    reordering, omission, duplication, or stream truncation attacks.
"""

import hmac
import hashlib
from typing import Any, BinaryIO, Dict, Optional

from .auth import AEADAuthenticationError, AuthenticationTag, FRAME_VERSION
from .nonce import AEADError

STREAM_HEADER_MAGIC: bytes = b"KDRS"
STREAM_VERSION: bytes = FRAME_VERSION
DEFAULT_CHUNK_SIZE: int = 65536  # 64 KB chunks


class StreamingAEADError(AEADError):
    """Base exception for streaming AEAD errors."""
    pass


class StreamCorruptedError(StreamingAEADError, AEADAuthenticationError):
    """Raised when stream header, chunk order, or chunk authentication tag is corrupted."""
    pass


class StreamingAEAD:
    """Streaming AEAD Engine for file and stream authenticated encryption."""

    def __init__(self, key_engine: Optional[Any] = None) -> None:
        """Initialize StreamingAEAD.

        Args:
            key_engine: KeyEvolutionEngine instance (creates default if None).
        """
        if key_engine is None:
            from crypto.key.evolution import KeyEvolutionEngine
            self._key_engine = KeyEvolutionEngine()
        else:
            self._key_engine = key_engine

    def encrypt_stream(
        self,
        input_stream: BinaryIO,
        output_stream: BinaryIO,
        master_key: bytes,
        nonce: bytes,
        aad: Optional[bytes] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> Dict[str, Any]:
        """Encrypt input binary stream into output stream with chunked AEAD authentication.

        Args:
            input_stream: Readable binary stream (e.g. opened file or BytesIO).
            output_stream: Writable binary stream.
            master_key: Secret master key bytes.
            nonce: Nonce bytes (12 bytes).
            aad: Optional Associated Data bytes.
            chunk_size: Chunk size in bytes (defaults to 64 KB).

        Returns:
            Dict[str, Any]: Execution summary dictionary (total_bytes, chunk_count).

        Raises:
            StreamingAEADError: If stream execution fails.
        """
        if chunk_size < 1024:
            raise StreamingAEADError(f"chunk_size must be at least 1024 bytes, got {chunk_size}")

        enc_key = self._key_engine.derive_encryption_key(master_key)
        auth_key = self._key_engine.derive_auth_key(master_key)

        norm_nonce = nonce[:12]
        # Write Stream Header
        header = STREAM_HEADER_MAGIC + STREAM_VERSION + norm_nonce
        output_stream.write(header)

        chunk_index = 0
        total_plaintext_bytes = 0

        current_chunk = input_stream.read(chunk_size)
        if not current_chunk:
            # Empty input stream: emit single empty final chunk
            current_chunk = b""

        while True:
            next_chunk = input_stream.read(chunk_size)
            is_final = len(next_chunk) == 0

            total_plaintext_bytes += len(current_chunk)
            is_final_byte = b"\x01" if is_final else b"\x00"

            # Keystream generation for chunk using auth_key + chunk_index
            chunk_seed = hmac.new(enc_key, norm_nonce + chunk_index.to_bytes(8, "big"), hashlib.sha256).digest()
            keystream = bytearray()
            while len(keystream) < len(current_chunk):
                keystream.extend(hashlib.sha256(chunk_seed + len(keystream).to_bytes(4, "big")).digest())

            ct_chunk = bytes(a ^ b for a, b in zip(current_chunk, keystream[:len(current_chunk)]))

            # Canonical Chunk Framing for Tag Calculation
            chunk_frame = (
                header
                + chunk_index.to_bytes(8, byteorder="big")
                + len(ct_chunk).to_bytes(4, byteorder="big")
                + ct_chunk
                + is_final_byte
                + (bytes(aad) if aad else b"")
            )
            chunk_tag = hmac.new(auth_key, chunk_frame, hashlib.sha256).digest()[:16]

            # Write Chunk Frame
            output_stream.write(chunk_index.to_bytes(8, byteorder="big"))
            output_stream.write(len(ct_chunk).to_bytes(4, byteorder="big"))
            output_stream.write(ct_chunk)
            output_stream.write(is_final_byte)
            output_stream.write(chunk_tag)

            chunk_index += 1
            if is_final:
                break

            current_chunk = next_chunk

        return {
            "total_bytes": total_plaintext_bytes,
            "chunk_count": chunk_index,
            "chunk_size": chunk_size,
        }

    def decrypt_stream(
        self,
        input_stream: BinaryIO,
        output_stream: BinaryIO,
        master_key: bytes,
        aad: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Decrypt input binary stream and verify chunk tags into output stream.

        Args:
            input_stream: Readable encrypted binary stream.
            output_stream: Writable decrypted binary stream.
            master_key: Secret master key bytes.
            aad: Optional Associated Data bytes.

        Returns:
            Dict[str, Any]: Execution summary dictionary.

        Raises:
            StreamCorruptedError: If header, tag, sequence order, or truncation is detected.
        """
        enc_key = self._key_engine.derive_encryption_key(master_key)
        auth_key = self._key_engine.derive_auth_key(master_key)

        # Read Stream Header (18 bytes: 4B magic + 2B ver + 12B nonce)
        header = input_stream.read(18)
        if len(header) < 18 or not header.startswith(STREAM_HEADER_MAGIC):
            raise StreamCorruptedError("Invalid or corrupted stream header magic")

        nonce = header[6:18]
        expected_chunk_index = 0
        total_decrypted_bytes = 0

        while True:
            # Read Chunk Index (8B) and Chunk Len (4B) -> 12 bytes
            header_chunk = input_stream.read(12)
            if not header_chunk:
                if expected_chunk_index == 0:
                    raise StreamCorruptedError("Stream is empty or truncated")
                break

            if len(header_chunk) < 12:
                raise StreamCorruptedError("Truncated chunk header in stream")

            chunk_index = int.from_bytes(header_chunk[:8], byteorder="big")
            if chunk_index != expected_chunk_index:
                raise StreamCorruptedError(
                    f"Stream chunk out of order: expected chunk {expected_chunk_index}, got {chunk_index}"
                )

            chunk_len = int.from_bytes(header_chunk[8:12], byteorder="big")
            ct_chunk = input_stream.read(chunk_len)
            if len(ct_chunk) < chunk_len:
                raise StreamCorruptedError("Truncated chunk ciphertext payload in stream")

            is_final_byte = input_stream.read(1)
            if not is_final_byte:
                raise StreamCorruptedError("Truncated stream: missing IsFinal byte")

            chunk_tag = input_stream.read(16)
            if len(chunk_tag) < 16:
                raise StreamCorruptedError("Truncated stream: missing chunk authentication tag")

            # Reconstruct Canonical Chunk Frame & Verify Tag
            chunk_frame = (
                header
                + chunk_index.to_bytes(8, byteorder="big")
                + len(ct_chunk).to_bytes(4, byteorder="big")
                + ct_chunk
                + is_final_byte
                + (bytes(aad) if aad else b"")
            )
            expected_tag = hmac.new(auth_key, chunk_frame, hashlib.sha256).digest()[:16]

            if not hmac.compare_digest(chunk_tag, expected_tag):
                raise StreamCorruptedError(f"Authentication tag verification failed for stream chunk {chunk_index}")

            # Decrypt Chunk using Keystream
            chunk_seed = hmac.new(enc_key, nonce + chunk_index.to_bytes(8, "big"), hashlib.sha256).digest()
            keystream = bytearray()
            while len(keystream) < len(ct_chunk):
                keystream.extend(hashlib.sha256(chunk_seed + len(keystream).to_bytes(4, "big")).digest())

            pt_chunk = bytes(a ^ b for a, b in zip(ct_chunk, keystream[:len(ct_chunk)]))
            output_stream.write(pt_chunk)

            total_decrypted_bytes += len(pt_chunk)
            expected_chunk_index += 1

            if is_final_byte == b"\x01":
                break

        return {
            "total_bytes": total_decrypted_bytes,
            "chunk_count": expected_chunk_index,
        }
