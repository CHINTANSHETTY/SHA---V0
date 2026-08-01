"""HMAC-based Extract-and-Expand Key Derivation Function (HKDF).

Standard: RFC 5869 / NIST SP 800-56C using HMAC-SHA256.
IEEE Mapping: Section IV-A (Key Derivation Subsystem)
"""

import hashlib
import hmac
from crypto.models.exceptions import KeyDerivationError

# =========================================================
# MODULE CONSTANTS
# =========================================================
HASH_ALGORITHM = hashlib.sha256
HASH_LEN: int = 32  # Output length of SHA-256 in bytes
MAX_EXPANSION_LEN: int = 255 * HASH_LEN  # 8160 bytes per RFC 5869


def hkdf_extract(salt: bytes | bytearray | None, ikm: bytes | bytearray) -> bytes:
    """Extracts a pseudorandom key (PRK) from Input Keying Material (IKM).

    Implementation conforms strictly to RFC 5869 Section 2.2.
    PRK = HMAC-Hash(Salt, IKM)

    Args:
        salt: Optional salt value (bytes). If None or empty, a string of zeros
          with length equal to HMAC-SHA256 hash length (32 bytes) is substituted.
        ikm: Input keying material (bytes). Must be non-empty.

    Returns:
        32-byte pseudorandom key (PRK).

    Raises:
        KeyDerivationError: If ikm is missing, empty, or not a bytes-like object.
        TypeError: If salt is provided but is not a bytes-like object.

    Security Notes:
        - The extract step concentrates the entropy of ikm into a 32-byte PRK.
        - NEVER log or expose ikm, salt, or returned PRK.
    """
    if not ikm or not isinstance(ikm, (bytes, bytearray)):
        raise KeyDerivationError(
            "Input keying material (IKM) must be a non-empty bytes-like object."
        )

    if salt is not None and not isinstance(salt, (bytes, bytearray)):
        raise TypeError("Salt must be a bytes-like object or None.")

    if not salt:
        salt = b"\x00" * HASH_LEN

    prk = hmac.new(bytes(salt), bytes(ikm), HASH_ALGORITHM).digest()
    return prk


def hkdf_expand(
    prk: bytes | bytearray,
    info: bytes | bytearray | None,
    length: int
) -> bytes:
    """Expands pseudorandom key (PRK) to output keying material (OKM).

    Implementation conforms strictly to RFC 5869 Section 2.3.
    T(0) = empty string (0 length)
    T(1) = HMAC-Hash(PRK, T(0) | info | 0x01)
    T(2) = HMAC-Hash(PRK, T(1) | info | 0x02)
    ...
    OKM = T(1) | T(2) | ... | T(N) truncated to length.

    Args:
        prk: Pseudorandom key of at least 32 bytes (derived from hkdf_extract).
        info: Optional context/application specific info (bytes). Defaults to b"".
        length: Desired output length in bytes (1 <= length <= 8160).

    Returns:
        Derived keying material (OKM) of exact length bytes.

    Raises:
        KeyDerivationError: If prk is invalid or length is out of range.
        TypeError: If inputs fail type validation.

    Security Notes:
        - Output key material OKM must be handled securely in memory.
        - HMAC-SHA256 iterations prevent sub-key dependency vulnerabilities.
    """
    if not prk or not isinstance(prk, (bytes, bytearray)) or len(prk) < HASH_LEN:
        raise KeyDerivationError(
            f"Pseudorandom key (PRK) must be a bytes-like object of at least {HASH_LEN} bytes."
        )

    if not isinstance(length, int) or length <= 0 or length > MAX_EXPANSION_LEN:
        raise KeyDerivationError(
            f"Requested length ({length}) out of range (1 to {MAX_EXPANSION_LEN} bytes)."
        )

    if info is None:
        info_bytes = b""
    elif isinstance(info, (bytes, bytearray)):
        info_bytes = bytes(info)
    else:
        raise TypeError("Info parameter must be a bytes-like object or None.")

    n = (length + HASH_LEN - 1) // HASH_LEN
    okm = bytearray()
    t_prev = b""
    prk_bytes = bytes(prk)

    for i in range(1, n + 1):
        ctx = t_prev + info_bytes + bytes([i])
        t_prev = hmac.new(prk_bytes, ctx, HASH_ALGORITHM).digest()
        okm.extend(t_prev)

    return bytes(okm[:length])


def hkdf(
    ikm: bytes | bytearray,
    length: int,
    salt: bytes | bytearray | None = None,
    info: bytes | bytearray = b""
) -> bytes:
    """Convenience function performing complete HKDF (Extract-then-Expand).

    Conforms to RFC 5869 Section 2.

    Args:
        ikm: Input keying material (bytes).
        length: Desired output length in bytes (1 <= length <= 8160).
        salt: Optional salt value (bytes).
        info: Optional info parameter (bytes).

    Returns:
        Derived output keying material (OKM) of length bytes.

    Raises:
        KeyDerivationError: If validation fails.
    """
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)
