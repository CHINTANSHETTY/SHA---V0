"""Nonce Management, Validation, and Reuse Prevention.

This module provides `NonceManager` for generating, validating, and registering AEAD nonces.

Bounded Memory Protection:
    Uses an internal Bounded LRU Cache (max_capacity=10,000) for active nonces to detect
    nonce reuse attacks while preventing unbounded memory consumption in long-running processes.
"""

import hashlib
import secrets
from collections import OrderedDict
from typing import Any, Dict, Optional, Set, Union

MIN_NONCE_LENGTH: int = 8
DEFAULT_NONCE_LENGTH: int = 12
MAX_NONCE_LENGTH: int = 64
DEFAULT_MAX_CAPACITY: int = 10000


# =========================================================
# EXCEPTION HIERARCHY
# =========================================================
class AEADError(Exception):
    """Base exception for all AEAD subsystem errors."""
    pass


class InvalidNonceError(AEADError, ValueError):
    """Raised when a nonce format, type, or length is invalid."""
    pass


class NonceReuseError(AEADError, RuntimeError):
    """Raised when nonce reuse is detected under active session/context."""
    pass


# =========================================================
# NONCE MANAGER
# =========================================================
class NonceManager:
    """AEAD Nonce Management & Reuse Detection.

    Supports automatic CSPRNG random nonces, deterministic counter nonces, and
    external nonce registration with a bounded LRU cache for reuse protection.
    """

    def __init__(self, default_length: int = DEFAULT_NONCE_LENGTH, max_capacity: int = DEFAULT_MAX_CAPACITY) -> None:
        """Initialize NonceManager.

        Args:
            default_length: Default nonce length in bytes (defaults to 12 bytes = 96 bits).
            max_capacity: Maximum LRU cache size for nonce reuse tracking (defaults to 10,000).
        """
        self.default_length: int = self._validate_length(default_length)
        self.max_capacity: int = max(max_capacity, 100)
        self._lru_cache: OrderedDict[bytes, bool] = OrderedDict()
        self._total_generated: int = 0

    def _validate_length(self, length: int) -> int:
        """Validate nonce length.

        Args:
            length: Nonce length in bytes.

        Returns:
            int: Validated length.

        Raises:
            InvalidNonceError: If length is out of range [8, 64].
        """
        if isinstance(length, bool) or not isinstance(length, int):
            raise InvalidNonceError(f"Nonce length must be an integer, got {type(length).__name__}")
        if not (MIN_NONCE_LENGTH <= length <= MAX_NONCE_LENGTH):
            raise InvalidNonceError(
                f"Nonce length ({length}) out of range [{MIN_NONCE_LENGTH}, {MAX_NONCE_LENGTH}]"
            )
        return length

    def validate(self, nonce: Any, min_length: int = MIN_NONCE_LENGTH, max_length: int = MAX_NONCE_LENGTH) -> bytes:
        """Validate nonce input type and byte length.

        Args:
            nonce: Nonce input object.
            min_length: Minimum allowed length in bytes.
            max_length: Maximum allowed length in bytes.

        Returns:
            bytes: Validated nonce bytes.

        Raises:
            InvalidNonceError: If nonce is invalid.
        """
        if not nonce or not isinstance(nonce, (bytes, bytearray)):
            raise InvalidNonceError(f"Nonce must be a non-empty bytes-like object, got {type(nonce).__name__}")
        
        n_bytes = bytes(nonce)
        if not (min_length <= len(n_bytes) <= max_length):
            raise InvalidNonceError(
                f"Nonce length ({len(n_bytes)}) out of range [{min_length}, {max_length}]"
            )
        return n_bytes

    def register(self, nonce: bytes) -> bool:
        """Register a nonce and check for reuse.

        Args:
            nonce: Nonce bytes to register.

        Returns:
            bool: True if registration succeeded.

        Raises:
            NonceReuseError: If nonce was already registered in the active LRU cache.
        """
        valid_nonce = self.validate(nonce)

        if valid_nonce in self._lru_cache:
            raise NonceReuseError(f"Nonce reuse detected: nonce '{valid_nonce.hex()}' was already used")

        # Evict oldest entry if capacity reached
        if len(self._lru_cache) >= self.max_capacity:
            self._lru_cache.popitem(last=False)

        self._lru_cache[valid_nonce] = True
        return True

    def generate(self, length: Optional[int] = None, check_reuse: bool = True) -> bytes:
        """Generate a cryptographically secure random nonce via CSPRNG.

        Args:
            length: Optional nonce length override.
            check_reuse: If True, registers the nonce and ensures no reuse.

        Returns:
            bytes: Generated random nonce bytes.
        """
        len_val = self._validate_length(length if length is not None else self.default_length)
        
        for _ in range(100):  # Retry loop in rare case of collision
            nonce = secrets.token_bytes(len_val)
            if check_reuse and nonce in self._lru_cache:
                continue
            if check_reuse:
                self.register(nonce)
            self._total_generated += 1
            return nonce

        raise AEADError("Failed to generate unique random nonce")

    def generate_deterministic(self, seed: bytes, counter: int, length: Optional[int] = None) -> bytes:
        """Generate a deterministic nonce from seed bytes and counter index.

        Args:
            seed: Seed bytes (e.g. derived nonce_key).
            counter: Non-negative integer step index.
            length: Optional nonce length override.

        Returns:
            bytes: Deterministic nonce bytes.
        """
        if not seed or not isinstance(seed, (bytes, bytearray)):
            raise InvalidNonceError("Seed must be a non-empty bytes-like object")
        if isinstance(counter, bool) or not isinstance(counter, int) or counter < 0:
            raise InvalidNonceError("Counter must be a non-negative integer")
        len_val = self._validate_length(length if length is not None else self.default_length)

        inp = bytes(seed) + counter.to_bytes(8, byteorder="big")
        digest = hashlib.sha256(inp).digest()
        nonce = digest[:len_val]

        self.register(nonce)
        self._total_generated += 1
        return nonce

    def reset(self) -> None:
        """Clear all registered nonces from the LRU cache."""
        self._lru_cache.clear()

    def export_state(self) -> Dict[str, Any]:
        """Export nonce manager metadata state.

        Returns:
            Dict[str, Any]: Metadata dictionary.
        """
        return {
            "default_length": self.default_length,
            "max_capacity": self.max_capacity,
            "active_nonces_count": len(self._lru_cache),
            "total_generated": self._total_generated,
        }
