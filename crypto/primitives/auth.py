"""AEAD Canonical Authentication Framing and Constant-Time Tag Verification.

This module provides `AuthenticationTag` for generating and verifying AEAD authentication tags
over canonical versioned frames.

Canonical Versioned Frame Specification:
    `Version (2B) || NonceLen (2B) || Nonce || AADLen (4B) || AAD || CTLen (8B) || Ciphertext`

Security Principles:
    - Constant-Time Comparison: Uses `hmac.compare_digest()` to eliminate timing side-channels.
    - Uniform Exception Handling: Verification failures produce uniform `AEADAuthenticationError`
      to prevent leaking internal state.
"""

import hmac
import hashlib
from typing import Any, Optional, Union

from .nonce import AEADError, InvalidNonceError

# =========================================================
# CONSTANTS & POLICIES
# =========================================================
FRAME_VERSION: bytes = b"\x01\x00"  # Version 1.0
DEFAULT_TAG_LENGTH: int = 16       # 128-bit authentication margin (standard default)
FULL_TAG_LENGTH: int = 32          # 256-bit research/full HMAC-SHA256 tag


# =========================================================
# EXCEPTION CLASSES
# =========================================================
class AEADAuthenticationError(AEADError, ValueError):
    """Uniform exception raised for all AEAD authentication failures."""
    pass


class InvalidTagError(AEADAuthenticationError):
    """Raised when an authentication tag format or length is invalid."""
    pass


# =========================================================
# AUTHENTICATION TAG ENGINE
# =========================================================
class AuthenticationTag:
    """Canonical AEAD Authentication Tag Generator and Verifier."""

    @staticmethod
    def _validate_auth_key(auth_key: Any) -> bytes:
        """Validate authentication key bytes."""
        if not auth_key or not isinstance(auth_key, (bytes, bytearray)):
            raise InvalidTagError("auth_key must be a non-empty bytes-like object")
        if len(auth_key) < 16:
            raise InvalidTagError(f"auth_key length must be at least 16 bytes, got {len(auth_key)}")
        return bytes(auth_key)

    @staticmethod
    def construct_canonical_frame(
        ciphertext: bytes,
        nonce: bytes,
        aad: Optional[bytes] = None,
        version: bytes = FRAME_VERSION,
    ) -> bytes:
        """Construct the canonical framed authentication byte sequence.

        Frame Layout:
            `Version (2B) || NonceLen (2B) || Nonce || AADLen (4B) || AAD || CTLen (8B) || Ciphertext`

        Args:
            ciphertext: Raw ciphertext bytes.
            nonce: Nonce bytes.
            aad: Optional Associated Data bytes.
            version: 2-byte protocol version tag.

        Returns:
            bytes: Canonical binary frame payload.
        """
        ct_bytes = bytes(ciphertext) if ciphertext else b""
        n_bytes = bytes(nonce) if nonce else b""
        aad_bytes = bytes(aad) if aad else b""

        frame = bytearray()
        frame.extend(version[:2])
        frame.extend(len(n_bytes).to_bytes(2, byteorder="big"))
        frame.extend(n_bytes)
        frame.extend(len(aad_bytes).to_bytes(4, byteorder="big"))
        frame.extend(aad_bytes)
        frame.extend(len(ct_bytes).to_bytes(8, byteorder="big"))
        frame.extend(ct_bytes)

        return bytes(frame)

    @classmethod
    def generate(
        cls,
        auth_key: bytes,
        ciphertext: bytes,
        nonce: bytes,
        aad: Optional[bytes] = None,
        tag_length: int = DEFAULT_TAG_LENGTH,
    ) -> bytes:
        """Generate a canonical AEAD authentication tag.

        Args:
            auth_key: Secret authentication key bytes (>= 16 bytes).
            ciphertext: Ciphertext payload bytes.
            nonce: Nonce bytes.
            aad: Optional Associated Data bytes.
            tag_length: Desired tag length in bytes (16 or 32, defaults to 16).

        Returns:
            bytes: HMAC-SHA256 authentication tag truncated to tag_length bytes.

        Raises:
            InvalidTagError: If auth_key or tag_length is invalid.
        """
        key = cls._validate_auth_key(auth_key)
        if tag_length not in (16, 32):
            raise InvalidTagError(f"tag_length must be 16 or 32 bytes, got {tag_length}")

        frame = cls.construct_canonical_frame(ciphertext=ciphertext, nonce=nonce, aad=aad)
        full_hmac = hmac.new(key, frame, hashlib.sha256).digest()
        return full_hmac[:tag_length]

    @classmethod
    def verify(
        cls,
        auth_key: bytes,
        ciphertext: bytes,
        nonce: bytes,
        expected_tag: bytes,
        aad: Optional[bytes] = None,
        raise_on_failure: bool = True,
    ) -> bool:
        """Verify an authentication tag in constant time.

        Args:
            auth_key: Secret authentication key bytes.
            ciphertext: Ciphertext payload bytes.
            nonce: Nonce bytes.
            expected_tag: Expected tag bytes (16 or 32 bytes).
            aad: Optional Associated Data bytes.
            raise_on_failure: If True, raises uniform AEADAuthenticationError on mismatch.

        Returns:
            bool: True if verification succeeds, False otherwise.

        Raises:
            AEADAuthenticationError: If tag verification fails and raise_on_failure=True.
        """
        if not expected_tag or not isinstance(expected_tag, (bytes, bytearray)):
            if raise_on_failure:
                raise AEADAuthenticationError("Authentication verification failed: invalid tag object")
            return False

        exp_tag = bytes(expected_tag)
        tag_len = len(exp_tag)
        if tag_len not in (16, 32):
            if raise_on_failure:
                raise AEADAuthenticationError("Authentication verification failed: tag length must be 16 or 32")
            return False

        try:
            computed_tag = cls.generate(
                auth_key=auth_key,
                ciphertext=ciphertext,
                nonce=nonce,
                aad=aad,
                tag_length=tag_len,
            )
        except Exception:
            if raise_on_failure:
                raise AEADAuthenticationError("Authentication verification failed")
            return False

        is_valid = hmac.compare_digest(computed_tag, exp_tag)
        if not is_valid and raise_on_failure:
            raise AEADAuthenticationError("Authentication verification failed: tag mismatch or payload corrupted")

        return is_valid

    @staticmethod
    def compare(tag1: bytes, tag2: bytes) -> bool:
        """Perform constant-time comparison of two tag byte strings.

        Args:
            tag1: First tag.
            tag2: Second tag.

        Returns:
            bool: True if tags match in constant time.
        """
        if not tag1 or not tag2 or not isinstance(tag1, (bytes, bytearray)) or not isinstance(tag2, (bytes, bytearray)):
            return False
        return hmac.compare_digest(bytes(tag1), bytes(tag2))
