"""Advanced Key Evolution Engine.

This module provides the `KeyEvolutionEngine` for deterministic, forward-secure master key ratcheting
and context-aware subkey derivation across the KDR-CA-AEAD cryptographic system.

Standard Compliance:
    - RFC 5869 HKDF Extract & Expand primitives re-used directly from `crypto.primitives.hkdf`.
    - Domain separation labels guarantee key isolation across round keys, session keys, epoch keys,
      CA keys, authentication keys, and encryption keys.
"""

from typing import Any, Dict, Optional, Union

from crypto.primitives.hkdf import BytesLike, hkdf_expand, hkdf_extract

# =========================================================
# DOMAIN SEPARATION LABEL CONSTANTS
# =========================================================
VERSION_LABEL: bytes = b"KDR-CA-AEAD|v1.0"
MASTER_EVOLVE_LABEL: bytes = b"KDR-CA-AEAD|v1.0|MasterEvolve"
ROUND_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|RoundKey"
SESSION_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|SessionKey"
EPOCH_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|EpochKey"
CONTEXT_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|ContextKey"
CA_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|CAKey"
AUTH_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|AuthKey"
ENC_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|EncKey"
NONCE_KEY_LABEL: bytes = b"KDR-CA-AEAD|v1.0|NonceKey"
FORWARD_RATCHET_LABEL: bytes = b"KDR-CA-AEAD|v1.0|ForwardRatchet"

MIN_KEY_LENGTH: int = 16
MAX_KEY_LENGTH: int = 8160


# =========================================================
# EXCEPTION HIERARCHY
# =========================================================
class KeyErrorBase(Exception):
    """Base exception for all key subsystem errors."""
    pass


class InvalidKeyLengthError(KeyErrorBase, ValueError):
    """Raised when key length is invalid or out of range."""
    pass


class InvalidContextError(KeyErrorBase, ValueError):
    """Raised when key context, salt, or input key material is invalid."""
    pass


class KeyEvolutionError(KeyErrorBase, RuntimeError):
    """Raised when key evolution or derivation step fails."""
    pass


# =========================================================
# KEY EVOLUTION ENGINE
# =========================================================
class KeyEvolutionEngine:
    """Advanced Key Evolution Engine.

    Manages master key ratcheting (HKDF-Extract) and context-aware subkey derivation (HKDF-Expand)
    using strict domain separation labels.
    """

    def __init__(self, default_key_length: int = 32) -> None:
        """Initialize KeyEvolutionEngine.

        Args:
            default_key_length: Default output length for derived keys in bytes (defaults to 32).
        """
        self.default_key_length: int = self._validate_length(default_key_length)
        self._evolution_step: int = 0
        self._derivation_count: int = 0
        self._prk_cache: Dict[Tuple[bytes, bytes], bytes] = {}

    def _extract_prk(self, salt: bytes, ikm: bytes) -> bytes:
        """Extract PRK with caching for identical (salt, ikm) pairs."""
        cache_key = (salt, ikm)
        if cache_key in self._prk_cache:
            return self._prk_cache[cache_key]

        prk = hkdf_extract(salt=salt, ikm=ikm)
        if len(self._prk_cache) > 256:
            self._prk_cache.clear()
        self._prk_cache[cache_key] = prk
        return prk

    def _validate_master_key(self, master_key: Any) -> bytes:
        """Validate input master key bytes.

        Args:
            master_key: Input master key material.

        Returns:
            bytes: Validated master key bytes.

        Raises:
            InvalidContextError: If master_key is missing or invalid type.
        """
        if not master_key or not isinstance(master_key, (bytes, bytearray)):
            raise InvalidContextError(f"Master key must be a non-empty bytes-like object, got {type(master_key).__name__}")
        if len(master_key) < 16:
            raise InvalidContextError(f"Master key length must be at least 16 bytes, got {len(master_key)}")
        return bytes(master_key)

    def _validate_length(self, length: int) -> int:
        """Validate output key length.

        Args:
            length: Requested output length in bytes.

        Returns:
            int: Validated length.

        Raises:
            InvalidKeyLengthError: If length is out of range [16, 8160].
        """
        if isinstance(length, bool) or not isinstance(length, int):
            raise InvalidKeyLengthError(f"Key length must be an integer, got {type(length).__name__}")
        if not (MIN_KEY_LENGTH <= length <= MAX_KEY_LENGTH):
            raise InvalidKeyLengthError(
                f"Requested key length ({length}) out of range [{MIN_KEY_LENGTH}, {MAX_KEY_LENGTH}]"
            )
        return length

    def evolve(self, master_key: bytes, salt: Optional[bytes] = None) -> bytes:
        """Perform a one-way master key ratchet step using HKDF-Extract.

        K_{i+1} = HKDF-Extract(salt=salt or MASTER_EVOLVE_LABEL, IKM=K_i)

        Args:
            master_key: Current master key bytes.
            salt: Optional custom salt bytes.

        Returns:
            bytes: Evolved next master key (32 bytes).
        """
        key_bytes = self._validate_master_key(master_key)
        effective_salt = salt if salt is not None else MASTER_EVOLVE_LABEL
        self._derivation_count += 1
        return hkdf_extract(salt=effective_salt, ikm=key_bytes)

    def derive_round_key(self, master_key: bytes, round_num: int, key_length: Optional[int] = None) -> bytes:
        """Derive a round key for a specific evolution round.

        Args:
            master_key: Master key material.
            round_num: Non-negative round index.
            key_length: Optional output length override in bytes.

        Returns:
            bytes: Derived round key.
        """
        key_bytes = self._validate_master_key(master_key)
        if isinstance(round_num, bool) or not isinstance(round_num, int) or round_num < 0:
            raise InvalidContextError(f"round_num must be a non-negative integer, got {round_num}")
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = hkdf_extract(salt=ROUND_KEY_LABEL, ikm=key_bytes)
        info = ROUND_KEY_LABEL + b"|" + round_num.to_bytes(4, byteorder="big")
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=info, length=length)

    def derive_session_key(self, master_key: bytes, session_id: str, key_length: Optional[int] = None) -> bytes:
        """Derive a session key for a specific session ID.

        Args:
            master_key: Master key material.
            session_id: Session identifier string.
            key_length: Optional output length override in bytes.

        Returns:
            bytes: Derived session key.
        """
        key_bytes = self._validate_master_key(master_key)
        if not isinstance(session_id, str) or not session_id.strip():
            raise InvalidContextError("session_id must be a non-empty string")
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = hkdf_extract(salt=SESSION_KEY_LABEL, ikm=key_bytes)
        info = SESSION_KEY_LABEL + b"|" + session_id.strip().encode("utf-8")
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=info, length=length)

    def derive_epoch_key(self, master_key: bytes, epoch_num: int, key_length: Optional[int] = None) -> bytes:
        """Derive an epoch key for a specific epoch number.

        Args:
            master_key: Master key material.
            epoch_num: Non-negative epoch index.
            key_length: Optional output length override.

        Returns:
            bytes: Derived epoch key.
        """
        key_bytes = self._validate_master_key(master_key)
        if isinstance(epoch_num, bool) or not isinstance(epoch_num, int) or epoch_num < 0:
            raise InvalidContextError(f"epoch_num must be a non-negative integer, got {epoch_num}")
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = hkdf_extract(salt=EPOCH_KEY_LABEL, ikm=key_bytes)
        info = EPOCH_KEY_LABEL + b"|" + epoch_num.to_bytes(4, byteorder="big")
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=info, length=length)

    def derive_context_key(self, master_key: bytes, context: bytes, key_length: Optional[int] = None) -> bytes:
        """Derive a context key for arbitrary context bytes.

        Args:
            master_key: Master key material.
            context: Custom context bytes.
            key_length: Optional output length override.

        Returns:
            bytes: Derived context key.
        """
        key_bytes = self._validate_master_key(master_key)
        if not isinstance(context, (bytes, bytearray)):
            raise InvalidContextError("context must be a bytes-like object")
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = self._extract_prk(salt=CONTEXT_KEY_LABEL, ikm=key_bytes)
        info = CONTEXT_KEY_LABEL + b"|" + bytes(context)
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=info, length=length)

    def derive_ca_key(self, master_key: bytes, ca_id: Union[int, str], key_length: Optional[int] = None) -> bytes:
        """Derive a Cellular Automata key for a specific rule or CA ID.

        Args:
            master_key: Master key material.
            ca_id: Rule integer (0-255) or string ID.
            key_length: Optional output length override.

        Returns:
            bytes: Derived CA key.
        """
        key_bytes = self._validate_master_key(master_key)
        if isinstance(ca_id, bool) or not isinstance(ca_id, (int, str)):
            raise InvalidContextError("ca_id must be an int or str")
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = self._extract_prk(salt=CA_KEY_LABEL, ikm=key_bytes)
        info = CA_KEY_LABEL + b"|" + str(ca_id).encode("utf-8")
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=info, length=length)

    def derive_auth_key(self, master_key: bytes, key_length: Optional[int] = None) -> bytes:
        """Derive a dedicated authentication key.

        Args:
            master_key: Master key material.
            key_length: Optional output length override.

        Returns:
            bytes: Derived authentication key.
        """
        key_bytes = self._validate_master_key(master_key)
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = self._extract_prk(salt=AUTH_KEY_LABEL, ikm=key_bytes)
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=AUTH_KEY_LABEL, length=length)

    def derive_encryption_key(self, master_key: bytes, key_length: Optional[int] = None) -> bytes:
        """Derive a dedicated payload encryption key.

        Args:
            master_key: Master key material.
            key_length: Optional output length override.

        Returns:
            bytes: Derived encryption key.
        """
        key_bytes = self._validate_master_key(master_key)
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = self._extract_prk(salt=ENC_KEY_LABEL, ikm=key_bytes)
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=ENC_KEY_LABEL, length=length)

    def derive_nonce_key(self, master_key: bytes, key_length: Optional[int] = None) -> bytes:
        """Derive a dedicated nonce derivation key.

        Args:
            master_key: Master key material.
            key_length: Optional output length override.

        Returns:
            bytes: Derived nonce key.
        """
        key_bytes = self._validate_master_key(master_key)
        length = self._validate_length(key_length if key_length is not None else self.default_key_length)

        prk = self._extract_prk(salt=NONCE_KEY_LABEL, ikm=key_bytes)
        self._derivation_count += 1
        return hkdf_expand(prk=prk, info=NONCE_KEY_LABEL, length=length)

    def export_state(self) -> Dict[str, Any]:
        """Export engine state metadata.

        Returns:
            Dict[str, Any]: Engine metadata.
        """
        return {
            "default_key_length": self.default_key_length,
            "derivation_count": self._derivation_count,
            "version": VERSION_LABEL.decode("utf-8"),
        }
