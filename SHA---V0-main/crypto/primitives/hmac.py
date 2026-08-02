"""
HMAC-SHA256 Authenticated Messaging Primitive.
Standard: FIPS 198-1 / RFC 2104 using SHA-256.

IEEE Mapping: Section IV-B (Authentication Subsystem)
"""

import hmac
import hashlib


def generate_hmac(key: bytes, data: bytes) -> bytes:
    """Generates a 32-byte HMAC-SHA256 authentication tag.

    Args:
        key: Secret authentication key (bytes). Must be non-empty.
        data: Payload bytes to authenticate.

    Returns:
        32-byte HMAC-SHA256 binary tag.

    Raises:
        ValueError: If key is not provided or empty.
    """
    if not key:
        raise ValueError("HMAC authentication key cannot be empty.")

    if data is None:
        data = b""

    return hmac.new(key, data, hashlib.sha256).digest()


def verify_hmac(key: bytes, data: bytes, expected_tag: bytes) -> bool:
    """Verifies HMAC-SHA256 tag in constant time.

    Args:
        key: Secret authentication key (bytes).
        data: Payload bytes to verify.
        expected_tag: 32-byte expected HMAC tag.

    Returns:
        True if tag matches expected tag in constant time, False otherwise.
    """
    if not key or not expected_tag:
        return False

    computed_tag = generate_hmac(key, data)
    return hmac.compare_digest(computed_tag, expected_tag)
