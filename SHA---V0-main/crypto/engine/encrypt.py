"""
High-Level KDR-CA-AEAD Encryptor.

IEEE Mapping: Section IV-D (AEAD Encryption Subsystem)
"""

import hashlib
import hmac
from crypto.primitives.random import generate_salt, generate_nonce
from crypto.primitives.hmac import generate_hmac
from crypto.engine.key_schedule import KeySchedule
from crypto.engine.dynamic_ca import apply_keyed_ca_forward
from crypto.models.package import EncryptedPackage
from crypto.models.exceptions import CryptoError


def _generate_keystream(cipher_key: bytes, nonce: bytes, length: int) -> bytes:
    """Generates arbitrary-length keystream using HMAC-SHA256 Counter Mode (CTR-PRNG)."""
    hash_len = 32
    n_blocks = (length + hash_len - 1) // hash_len
    keystream = bytearray()

    for counter in range(n_blocks):
        counter_bytes = counter.to_bytes(4, "big")
        block = hmac.new(cipher_key, nonce + counter_bytes, hashlib.sha256).digest()
        keystream.extend(block)

    return bytes(keystream[:length])


def encrypt_payload(
    plaintext: str,
    password: str,
    salt: bytes | None = None,
    nonce: bytes | None = None
) -> EncryptedPackage:
    """Encrypts plaintext payload using KDR-CA-AEAD authenticated cipher.

    Args:
        plaintext: Plaintext payload string to encrypt.
        password: User password string.
        salt: Optional 16-byte salt override (for testing).
        nonce: Optional 12-byte nonce override (for testing).

    Returns:
        EncryptedPackage containing salt, nonce, ciphertext, and HMAC tag.

    Raises:
        CryptoError: If plaintext or password is empty.
    """
    if not plaintext:
        raise CryptoError("Plaintext payload cannot be empty.")

    if not password:
        raise CryptoError("Password cannot be empty.")

    if salt is None:
        salt = generate_salt(16)

    if nonce is None:
        nonce = generate_nonce(12)

    # Step 1: Derive sub-keys
    ks = KeySchedule(password, salt, nonce)
    rule_table = ks.get_ca_rule_table()
    cipher_key = ks.get_cipher_key()
    mac_key = ks.get_mac_key()

    plaintext_bytes = plaintext.encode("utf-8")

    # Step 2: Apply Keyed Dynamic CA transformation
    transformed = apply_keyed_ca_forward(plaintext_bytes, rule_table)

    # Step 3: Expand keystream via HMAC-SHA256 Counter PRNG
    keystream = _generate_keystream(cipher_key, nonce, len(transformed))

    # Step 4: Bitwise XOR stream encryption
    ciphertext = bytes(a ^ b for a, b in zip(transformed, keystream))

    # Step 5: Generate HMAC-SHA256 AEAD tag over (Nonce || Salt || Ciphertext)
    aad_and_ciphertext = nonce + salt + ciphertext
    tag = generate_hmac(mac_key, aad_and_ciphertext)

    return EncryptedPackage(
        version="KDR-CA-AEAD-v1",
        salt=salt,
        nonce=nonce,
        ciphertext=ciphertext,
        tag=tag
    )
