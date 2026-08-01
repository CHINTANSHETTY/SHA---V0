"""
HMAC-based Extract-and-Expand Key Derivation Function (HKDF).
Standard: RFC 5869 / NIST SP 800-56C using HMAC-SHA256.

IEEE Mapping: Section IV-A (Key Derivation Subsystem)
"""

import hmac
import hashlib


def hkdf_extract(salt: bytes | None, ikm: bytes) -> bytes:
    """Extracts a pseudorandom key (PRK) from Input Keying Material (IKM).

    Args:
        salt: Optional salt value (bytes). If None or empty, a string of zeros
          with length equal to HMAC-SHA256 hash length (32 bytes) is used.
        ikm: Input keying material (bytes).

    Returns:
        32-byte pseudorandom key (PRK).

    Raises:
        ValueError: If ikm is not provided or empty.
    """
    if not ikm:
        raise ValueError("Input keying material (IKM) cannot be empty.")

    hash_len = hashlib.sha256().digest_size  # 32 bytes

    if not salt:
        salt = b"\x00" * hash_len

    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    return prk


def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    """Expands pseudorandom key (PRK) to output keying material (OKM) of length bytes.

    Args:
        prk: Pseudorandom key of at least 32 bytes (from hkdf_extract).
        info: Optional context and application specific information (bytes).
        length: Desired output length in bytes (max 255 * 32 = 8160 bytes).

    Returns:
        Derived keying material of specified byte length.

    Raises:
        ValueError: If length <= 0 or length > 255 * 32 bytes.
        ValueError: If prk is invalid.
    """
    hash_len = hashlib.sha256().digest_size

    if not prk or len(prk) < hash_len:
        raise ValueError(f"PRK must be at least {hash_len} bytes.")

    if length <= 0 or length > 255 * hash_len:
        raise ValueError(f"Requested length ({length}) out of range (1 - {255 * hash_len}).")

    if info is None:
        info = b""

    n = (length + hash_len - 1) // hash_len
    okm = b""
    t_prev = b""

    for i in range(1, n + 1):
        ctx = t_prev + info + bytes([i])
        t_prev = hmac.new(prk, ctx, hashlib.sha256).digest()
        okm += t_prev

    return okm[:length]


def hkdf(ikm: bytes, length: int, salt: bytes | None = None, info: bytes = b"") -> bytes:
    """Convenience function performing full HKDF (Extract-then-Expand).

    Args:
        ikm: Input keying material.
        length: Desired output length in bytes.
        salt: Optional salt value.
        info: Optional info parameter.

    Returns:
        Derived pseudorandom key of specified byte length.
    """
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)
