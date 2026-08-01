"""
High-Level KDR-CA-AEAD Decryptor & Authenticator.

IEEE Mapping: Section IV-E (AEAD Decryption & Integrity Subsystem)
"""

import hashlib
import hmac
from crypto.primitives.hmac import verify_hmac
from crypto.engine.key_schedule import KeySchedule
from crypto.engine.dynamic_ca import apply_keyed_ca_inverse
from crypto.models.package import EncryptedPackage
from crypto.models.exceptions import CryptoError, AuthenticationError


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


def decrypt_payload(package: EncryptedPackage, password: str) -> str:
    """Decrypts and authenticates a KDR-CA-AEAD payload package.

    Args:
        package: EncryptedPackage object.
        password: User password string.

    Returns:
        Original plaintext string payload.

    Raises:
        CryptoError: If inputs are invalid.
        AuthenticationError: If HMAC tag verification fails or invalid password.
    """
    if not isinstance(package, EncryptedPackage):
        raise CryptoError("Invalid package type.")

    if not password:
        raise CryptoError("Password cannot be empty.")

    # Step 1: Derive sub-keys
    ks = KeySchedule(password, package.salt, package.nonce)
    rule_table = ks.get_ca_rule_table()
    cipher_key = ks.get_cipher_key()
    mac_key = ks.get_mac_key()

    # Step 2: Constant-Time HMAC-SHA256 Integrity Tag Verification (AEAD Check)
    aad_and_ciphertext = package.nonce + package.salt + package.ciphertext
    if not verify_hmac(mac_key, aad_and_ciphertext, package.tag):
        raise AuthenticationError(
            "Payload integrity verification failed or invalid password."
        )

    # Step 3: Expand keystream via HMAC-SHA256 Counter PRNG
    keystream = _generate_keystream(cipher_key, package.nonce, len(package.ciphertext))

    # Step 4: Reverse Bitwise XOR
    transformed = bytes(a ^ b for a, b in zip(package.ciphertext, keystream))

    # Step 5: Reverse Keyed Dynamic CA transformation
    plaintext_bytes = apply_keyed_ca_inverse(transformed, rule_table)

    try:
        return plaintext_bytes.decode("utf-8")
    except UnicodeDecodeError as err:
        raise AuthenticationError("Corrupted payload text encoding.") from err
