"""
Module:
    hkdf.py

Project:
    KDR-CA-AEAD

Purpose:
    Implements RFC 5869 compliant HKDF using HMAC-SHA256 for secure key derivation.

Author:
    Chintan

Version:
    1.0.0

IEEE Mapping:
    Section IV-A – Key Derivation Subsystem

Standards:
    RFC 5869 – HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
    NIST SP 800-56C Rev. 2 – Recommendation for Key-Derivation Methods

Dependencies:
    hashlib
    hmac
    crypto.constants
    crypto.models.exceptions

Security Classification:
    Critical Cryptographic Primitive
"""

from __future__ import annotations

import hashlib
import hmac
from typing import TypeAlias

from crypto.constants import HKDF_HASH_LENGTH, HKDF_MAX_OUTPUT, HKDF_VERSION
from crypto.models.exceptions import KeyDerivationError

__all__ = ["hkdf", "hkdf_extract", "hkdf_expand", "BytesLike"]

# Type Alias for explicit binary buffer parameters
BytesLike: TypeAlias = bytes | bytearray

# =========================================================
# THREAT MODEL & SECURITY ASSUMPTIONS
# =========================================================
"""
Threat Model & Security Assumptions:
-----------------------------------
1. Security Basis: Assumes HMAC-SHA256 acts as a Cryptographically Secure
   Pseudorandom Function (PRF).
2. Salt Characteristics: Salt is non-secret but must be unique per derivation context
   to guarantee IND-CPA security bounds.
3. Input Entropy: Assumes Input Keying Material (IKM) contains sufficient entropy
   for pseudorandom key extraction.
4. Scope Limitation: HKDF is NOT designed for password storage hashing. Password storage
   hashing in this system is handled by Argon2id in database/db_manager.py.
"""


def hkdf_extract(salt: BytesLike | None, ikm: BytesLike) -> bytes:
    """Extracts a pseudorandom key (PRK) from Input Keying Material (IKM).

    Implementation conforms strictly to RFC 5869 Section 2.2.
    PRK = HMAC-Hash(Salt, IKM)

    Preconditions:
        - ikm must be a non-empty bytes-like object (bytes or bytearray).
        - salt must be a bytes-like object or None.

    Postconditions:
        - Returns exactly HKDF_HASH_LENGTH (32) bytes of uniform PRK.

    Side Effects:
        - None. No state mutation or network/file I/O.

    Args:
        salt: Optional salt value. If None or empty, a string of zeros
          with length equal to HMAC-SHA256 hash length (32 bytes) is substituted.
        ikm: Input keying material (bytes). Must be non-empty.

    Returns:
        32-byte pseudorandom key (PRK).

    Raises:
        KeyDerivationError: If ikm is missing or empty.
        TypeError: If ikm or salt fails type validation.

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
        effective_salt = b"\x00" * HKDF_HASH_LENGTH
    else:
        effective_salt = bytes(salt)

    prk = hmac.new(effective_salt, bytes(ikm), hashlib.sha256).digest()
    return prk


def hkdf_expand(
    prk: BytesLike,
    info: BytesLike | None,
    length: int
) -> bytes:
    """Expands pseudorandom key (PRK) to output keying material (OKM).

    Implementation conforms strictly to RFC 5869 Section 2.3.
    T(0) = empty string (0 length)
    T(1) = HMAC-Hash(PRK, T(0) | info | 0x01)
    T(2) = HMAC-Hash(PRK, T(1) | info | 0x02)
    ...
    OKM = T(1) | T(2) | ... | T(N) truncated to length.

    RFC 5869 limits maximum expansion length to 255 * HashLen (8160 bytes)
    because the counter is encoded in a single octet (0x01 to 0xFF).

    Preconditions:
        - prk must be a bytes-like object of at least HKDF_HASH_LENGTH (32) bytes.
        - info must be a bytes-like object or None.
        - length must be an integer satisfying 1 <= length <= 8160.

    Postconditions:
        - Returns derived keying material OKM of exact length bytes.

    Side Effects:
        - None. No state mutation or network/file I/O.

    Args:
        prk: Pseudorandom key of at least 32 bytes (derived from hkdf_extract).
        info: Optional context/application specific info. Defaults to b"".
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
    if not prk or not isinstance(prk, (bytes, bytearray)) or len(prk) < HKDF_HASH_LENGTH:
        raise KeyDerivationError(
            f"Pseudorandom key (PRK) must be a bytes-like object of at least {HKDF_HASH_LENGTH} bytes."
        )

    if not isinstance(length, int) or length <= 0 or length > HKDF_MAX_OUTPUT:
        raise KeyDerivationError(
            f"Requested length ({length}) out of range (1 to {HKDF_MAX_OUTPUT} bytes)."
        )

    if info is None:
        info_bytes = b""
    elif isinstance(info, (bytes, bytearray)):
        info_bytes = bytes(info)
    else:
        raise TypeError("Info parameter must be a bytes-like object or None.")

    n = (length + HKDF_HASH_LENGTH - 1) // HKDF_HASH_LENGTH
    okm = bytearray()
    t_prev = b""
    prk_bytes = bytes(prk)

    for i in range(1, n + 1):
        ctx = t_prev + info_bytes + bytes([i])
        t_prev = hmac.new(prk_bytes, ctx, hashlib.sha256).digest()
        okm.extend(t_prev)

    return bytes(okm[:length])


def hkdf(
    ikm: BytesLike,
    length: int,
    salt: BytesLike | None = None,
    info: BytesLike = b""
) -> bytes:
    """Convenience function performing complete HKDF (Extract-then-Expand).

    Conforms to RFC 5869 Section 2.

    Preconditions:
        - ikm must be a non-empty bytes-like object.
        - length must satisfy 1 <= length <= 8160.

    Postconditions:
        - Returns derived keying material OKM of exact length bytes.

    Side Effects:
        - None.

    Args:
        ikm: Input keying material.
        length: Desired output length in bytes (1 <= length <= 8160).
        salt: Optional salt value.
        info: Optional info parameter.

    Returns:
        Derived output keying material (OKM) of length bytes.

    Raises:
        KeyDerivationError: If validation fails.
    """
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)
