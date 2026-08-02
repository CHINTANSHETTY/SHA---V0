"""
Module:
    decrypt.py

Project:
    KDR-CA-AEAD

Purpose:
    High-level authenticated decryption & integrity verification subsystem.
    Verifies Encrypt-then-MAC authentication tag, expands CTR keystream, decrypts XOR stream,
    and applies inverse Keyed Dynamic Cellular Automata transformation.

Author:
    Chintan (Project Lead, Cryptography Lead, Research Lead)

Version:
    1.0.0 (Frozen Architecture Integration)

IEEE Mapping:
    Section IV-E – AEAD Decryption & Integrity Subsystem Architecture

Security Classification:
    Authenticated Decryption Core Engine
"""

from __future__ import annotations

from typing import TypeAlias

from crypto.engine.dynamic_ca import apply_keyed_ca_inverse
from crypto.engine.encrypt import _generate_keystream
from crypto.engine.key_schedule import KeySchedule
from crypto.models.exceptions import AuthenticationError, CryptoError
from crypto.models.package import EncryptedPackage
from crypto.primitives.hmac import verify_hmac

__all__ = ["decrypt_payload", "decrypt_bytes", "BytesLike"]

BytesLike: TypeAlias = bytes | bytearray


def decrypt_bytes(package: EncryptedPackage, master_key: BytesLike) -> bytes:
    """Decrypts and authenticates an EncryptedPackage returning raw payload bytes.

    Args:
        package: EncryptedPackage object.
        master_key: Master key or password bytes.

    Returns:
        Original plaintext raw bytes.

    Raises:
        CryptoError: If package or master_key is invalid.
        AuthenticationError: If HMAC AEAD tag verification fails or wrong password.
    """
    if not isinstance(package, EncryptedPackage):
        raise CryptoError("Invalid package type.")

    if not master_key or not isinstance(master_key, (bytes, bytearray)):
        raise CryptoError("Master key must be a non-empty bytes-like buffer.")

    # Step 1: Sub-key expansion via KeySchedule
    ks = KeySchedule.from_master_key(master_key, package.salt, package.nonce)
    km = ks.export_key_material()

    # Step 2: Constant-Time HMAC-SHA256 Integrity Tag Verification (AEAD Check)
    aad_and_ciphertext = package.nonce + package.salt + package.ciphertext
    if not verify_hmac(km.mac_key, aad_and_ciphertext, package.tag):
        raise AuthenticationError(
            "Payload integrity verification failed or invalid password."
        )

    # Step 3: Expand keystream via HMAC-SHA256 Counter PRNG
    keystream = _generate_keystream(km.cipher_key, package.nonce, len(package.ciphertext))

    # Step 4: Reverse Bitwise XOR
    transformed = bytes(a ^ b for a, b in zip(package.ciphertext, keystream))

    # Step 5: Reverse Keyed Dynamic CA transformation
    return apply_keyed_ca_inverse(transformed, km.rule_table)


def decrypt_payload(package: EncryptedPackage, password: str) -> str:
    """Decrypts and authenticates a KDR-CA-AEAD package returning string payload.

    Args:
        package: EncryptedPackage object.
        password: User password string.

    Returns:
        Original plaintext string payload.

    Raises:
        CryptoError: If inputs are invalid.
        AuthenticationError: If HMAC tag verification fails or invalid password.
    """
    if not password or not isinstance(password, str):
        raise CryptoError("Password cannot be empty.")

    master_key_bytes = password.encode("utf-8")
    plaintext_bytes = decrypt_bytes(package, master_key_bytes)

    try:
        return plaintext_bytes.decode("utf-8")
    except UnicodeDecodeError as err:
        raise AuthenticationError("Corrupted payload text encoding.") from err
