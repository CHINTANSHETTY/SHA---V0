"""
Module:
    encrypt.py

Project:
    KDR-CA-AEAD

Purpose:
    High-level authenticated encryption subsystem. Integrates KeySchedule sub-key expansion,
    Dynamic Cellular Automata non-linear state permutation, HMAC-SHA256 CTR-PRNG stream cipher,
    and HMAC-SHA256 AEAD tag computation.

Author:
    Chintan (Project Lead, Cryptography Lead, Research Lead)

Version:
    1.0.0 (Frozen Architecture Integration)

IEEE Mapping:
    Section IV-D – AEAD Encryption Subsystem Architecture

Security Classification:
    Authenticated Encryption Core Engine
"""

from __future__ import annotations

import hashlib
import hmac
from typing import TypeAlias

from crypto.engine.dynamic_ca import apply_keyed_ca_forward
from crypto.engine.key_schedule import KeySchedule, PROTOCOL_VERSION
from crypto.models.exceptions import CryptoError
from crypto.models.package import EncryptedPackage
from crypto.primitives.hmac import generate_hmac
from crypto.primitives.random import generate_nonce, generate_salt

__all__ = ["encrypt_payload", "encrypt_bytes", "_generate_keystream", "BytesLike"]

BytesLike: TypeAlias = bytes | bytearray


def _generate_keystream(cipher_key: bytes, nonce: bytes, length: int) -> bytes:
    """Generates arbitrary-length keystream using HMAC-SHA256 Counter Mode (CTR-PRNG).

    Preconditions:
        - cipher_key is a 32-byte key (K_c).
        - nonce is a 12-byte CSPRNG buffer.
        - length is the required keystream length in bytes.

    Returns:
        Keystream bytes of exact requested length.
    """
    hash_len = 32
    n_blocks = (length + hash_len - 1) // hash_len
    keystream = bytearray()

    for counter in range(n_blocks):
        counter_bytes = counter.to_bytes(4, "big")
        block = hmac.new(cipher_key, nonce + counter_bytes, hashlib.sha256).digest()
        keystream.extend(block)

    return bytes(keystream[:length])


def encrypt_bytes(
    data: BytesLike,
    master_key: BytesLike,
    salt: BytesLike | None = None,
    nonce: BytesLike | None = None
) -> EncryptedPackage:
    """Encrypts raw binary data bytes using KDR-CA-AEAD authenticated cipher.

    Args:
        data: Raw binary payload bytes or bytearray.
        master_key: Secret master key or password bytes.
        salt: Optional 16-byte salt override.
        nonce: Optional 12-byte nonce override.

    Returns:
        EncryptedPackage containing salt, nonce, ciphertext, and HMAC AEAD tag.

    Raises:
        CryptoError: If payload data or master_key is empty or invalid.
    """
    if not data or not isinstance(data, (bytes, bytearray)):
        raise CryptoError("Payload data must be a non-empty bytes-like buffer.")

    if not master_key or not isinstance(master_key, (bytes, bytearray)):
        raise CryptoError("Master key must be a non-empty bytes-like buffer.")

    salt_bytes = bytes(salt) if salt is not None else generate_salt(16)
    nonce_bytes = bytes(nonce) if nonce is not None else generate_nonce(12)

    # Step 1: Sub-key expansion via KeySchedule
    ks = KeySchedule.from_master_key(master_key, salt_bytes, nonce_bytes)
    km = ks.export_key_material()

    # Step 2: Apply Keyed Dynamic CA transformation (Candidate A-Chain)
    transformed = apply_keyed_ca_forward(data, km.rule_table)

    # Step 3: Expand keystream via HMAC-SHA256 Counter PRNG
    keystream = _generate_keystream(km.cipher_key, nonce_bytes, len(transformed))

    # Step 4: Bitwise XOR stream encryption
    ciphertext = bytes(a ^ b for a, b in zip(transformed, keystream))

    # Step 5: Generate HMAC-SHA256 AEAD tag over (Nonce || Salt || Ciphertext)
    aad_and_ciphertext = nonce_bytes + salt_bytes + ciphertext
    tag = generate_hmac(km.mac_key, aad_and_ciphertext)

    return EncryptedPackage(
        version=PROTOCOL_VERSION,
        salt=salt_bytes,
        nonce=nonce_bytes,
        ciphertext=ciphertext,
        tag=tag
    )


def encrypt_payload(
    plaintext: str,
    password: str,
    salt: bytes | None = None,
    nonce: bytes | None = None
) -> EncryptedPackage:
    """Encrypts string plaintext payload using KDR-CA-AEAD authenticated cipher.

    Args:
        plaintext: Plaintext payload string to encrypt.
        password: User password string.
        salt: Optional 16-byte salt override.
        nonce: Optional 12-byte nonce override.

    Returns:
        EncryptedPackage containing salt, nonce, ciphertext, and HMAC AEAD tag.

    Raises:
        CryptoError: If plaintext or password string is empty.
    """
    if not plaintext or not isinstance(plaintext, str):
        raise CryptoError("Plaintext payload cannot be empty.")

    if not password or not isinstance(password, str):
        raise CryptoError("Password cannot be empty.")

    plaintext_bytes = plaintext.encode("utf-8")
    master_key_bytes = password.encode("utf-8")

    return encrypt_bytes(plaintext_bytes, master_key_bytes, salt=salt, nonce=nonce)
