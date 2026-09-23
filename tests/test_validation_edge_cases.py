"""
Module:
    test_validation_edge_cases.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Edge-Case, Boundary Condition, Stress, and Fuzzing Test Suite for Phase 4.1.
    Verifies robust input rejection, exception consistency, large payload handling (1MB+),
    Unicode/binary data integrity, and malformed payload schema handling.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import os
import random
import unittest

from crypto.engine.decrypt import decrypt_bytes, decrypt_payload
from crypto.engine.encrypt import encrypt_bytes, encrypt_payload
from crypto.models.exceptions import AuthenticationError, CorruptedPayloadError, CryptoError
from crypto.models.package import EncryptedPackage
from crypto.validation.advanced_validation import validate_master_key, validate_payload_data


class TestValidationEdgeCases(unittest.TestCase):
    """Edge-case and boundary condition test suite for KDR-CA-AEAD cipher."""

    def setUp(self):
        self.master_key = b"Nagamrutha_EdgeCase_Test_Key_32B!"

    def test_null_and_empty_inputs(self):
        """Verify null/None and empty buffers raise CryptoError."""
        # Advanced validation functions reject empty buffers
        with self.assertRaises(CryptoError):
            validate_payload_data(b"")

        with self.assertRaises(CryptoError):
            validate_master_key(b"")

        # Engine validation checks
        with self.assertRaises(CryptoError):
            encrypt_bytes(b"data", b"")

        with self.assertRaises(CryptoError):
            encrypt_bytes(None, self.master_key)  # type: ignore

        with self.assertRaises(CryptoError):
            encrypt_bytes(b"data", None)  # type: ignore

        with self.assertRaises(CryptoError):
            encrypt_payload("", "password")

        with self.assertRaises(CryptoError):
            encrypt_payload("plaintext", "")

    def test_invalid_types_input(self):
        """Verify passing incorrect data types (int, float, list) raises CryptoError."""
        with self.assertRaises(CryptoError):
            encrypt_bytes(12345, self.master_key)  # type: ignore

        with self.assertRaises(CryptoError):
            encrypt_bytes(b"data", 12345)  # type: ignore

        with self.assertRaises(CryptoError):
            decrypt_bytes(None, self.master_key)  # type: ignore

        with self.assertRaises(CryptoError):
            decrypt_bytes("not_a_package", self.master_key)  # type: ignore

    def test_corrupted_package_deserialization(self):
        """Verify deserializing corrupted JSON or missing hex fields raises CorruptedPayloadError."""
        with self.assertRaises(CorruptedPayloadError):
            EncryptedPackage.from_json("invalid_json_string")

        with self.assertRaises(CorruptedPayloadError):
            EncryptedPackage.from_dict({"version": "1.0.0", "salt": "1234"})  # Missing fields

        with self.assertRaises(CorruptedPayloadError):
            EncryptedPackage.from_dict({
                "version": "1.0.0",
                "salt": "not_hex!",
                "nonce": "1234",
                "ciphertext": "abcd",
                "tag": "ef00"
            })

    def test_tampered_tag_and_ciphertext_decryption(self):
        """Verify decrypting tampered packages raises AuthenticationError."""
        pkg = encrypt_bytes(b"Sensitive payload", self.master_key)

        # 1. Tampered tag
        bad_tag_pkg = EncryptedPackage(pkg.version, pkg.salt, pkg.nonce, pkg.ciphertext, b"\x00" * 32)
        with self.assertRaises(AuthenticationError):
            decrypt_bytes(bad_tag_pkg, self.master_key)

        # 2. Corrupted ciphertext
        bad_ct_pkg = EncryptedPackage(pkg.version, pkg.salt, pkg.nonce, bytes([pkg.ciphertext[0] ^ 0xFF]) + pkg.ciphertext[1:], pkg.tag)
        with self.assertRaises(AuthenticationError):
            decrypt_bytes(bad_ct_pkg, self.master_key)

    def test_unicode_multibyte_and_binary_null_bytes(self):
        """Verify encryption and decryption of multi-byte UTF-8, emojis, and binary null-byte buffers."""
        test_strings = [
            "Simple ASCII text",
            "Kannada text: ನಮಸ್ಕಾರ ನಾಗಾಮೃತ ಮೇಸ್ಥ!",
            "Hindi text: नमस्ते cryptography validation!",
            "Emoji payload: 🔒🔑🛡️ Binary security check 🚀",
            "Multi-lingual: Japanese=こんにちは, Chinese=你好, Russian=Привет",
        ]

        for s in test_strings:
            pkg = encrypt_payload(s, "Password_123!")
            decrypted = decrypt_payload(pkg, "Password_123!")
            self.assertEqual(decrypted, s)

        # Binary buffer with embedded null bytes \x00
        binary_data = b"\x00\x00\xFF\xFE\x00\x01\x02\x03\x00" * 128
        bin_pkg = encrypt_bytes(binary_data, self.master_key)
        bin_decrypted = decrypt_bytes(bin_pkg, self.master_key)
        self.assertEqual(bin_decrypted, binary_data)

    def test_large_payload_stress(self):
        """Verify round-trip encryption/decryption of a 1MB large binary payload."""
        large_payload = os.urandom(1024 * 1024)  # 1MB random bytes
        pkg = encrypt_bytes(large_payload, self.master_key)
        decrypted = decrypt_bytes(pkg, self.master_key)
        self.assertEqual(decrypted, large_payload)
        self.assertEqual(len(pkg.ciphertext), len(large_payload))

    def test_randomized_fuzzing_inputs(self):
        """Fuzz testing with 20 randomized payload and key lengths."""
        rng = random.Random(2026)
        for _ in range(20):
            pt_len = rng.randint(1, 10000)
            key_len = rng.randint(8, 64)
            pt = rng.randbytes(pt_len)
            key = rng.randbytes(key_len)

            pkg = encrypt_bytes(pt, key)
            decrypted = decrypt_bytes(pkg, key)
            self.assertEqual(decrypted, pt)


if __name__ == "__main__":
    unittest.main()
