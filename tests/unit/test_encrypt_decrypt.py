"""
End-to-End Encryption & Decryption Integration Tests.
"""

import unittest
from crypto.engine.encrypt import encrypt_payload, encrypt_bytes
from crypto.engine.decrypt import decrypt_payload, decrypt_bytes
from crypto.models.package import EncryptedPackage
from crypto.models.exceptions import AuthenticationError, CryptoError


class TestEncryptDecryptIntegration(unittest.TestCase):

    def test_full_encryption_decryption_roundtrip(self):
        plaintext = "Patient Record: ID=P001, Name=Rahul, Disease=Fever, Prescription=Paracetamol"
        password = "hospital_secure_password_123"

        pkg = encrypt_payload(plaintext, password)

        self.assertIsInstance(pkg, EncryptedPackage)
        self.assertEqual(pkg.version, "KDR-CA-AEAD-v1")
        self.assertEqual(len(pkg.salt), 16)
        self.assertEqual(len(pkg.nonce), 12)
        self.assertEqual(len(pkg.tag), 32)
        self.assertEqual(len(pkg.ciphertext), len(plaintext.encode("utf-8")))

        decrypted = decrypt_payload(pkg, password)
        self.assertEqual(plaintext, decrypted)

    def test_bytes_encryption_decryption_roundtrip(self):
        """Test raw binary bytes encryption and decryption."""
        raw_bytes = bytes(range(256)) * 4
        master_key = b"raw_master_key_bytes_123"

        pkg = encrypt_bytes(raw_bytes, master_key)
        self.assertEqual(len(pkg.ciphertext), len(raw_bytes))

        recovered_bytes = decrypt_bytes(pkg, master_key)
        self.assertEqual(raw_bytes, recovered_bytes)

    def test_json_serialization_roundtrip(self):
        plaintext = "EHR Payload: 05|Rahul|21|Male|Fever|Viral Fever|Paracetamol"
        password = "doctor_password"

        pkg = encrypt_payload(plaintext, password)
        json_str = pkg.to_json()

        restored_pkg = EncryptedPackage.from_json(json_str)
        decrypted = decrypt_payload(restored_pkg, password)
        self.assertEqual(plaintext, decrypted)

    def test_wrong_password_fails_authentication(self):
        plaintext = "Confidential Patient Data"
        password = "correct_password"
        wrong_password = "incorrect_password"

        pkg = encrypt_payload(plaintext, password)

        with self.assertRaises(AuthenticationError):
            decrypt_payload(pkg, wrong_password)

    def test_tampered_ciphertext_fails_authentication(self):
        plaintext = "Confidential Patient Data"
        password = "correct_password"

        pkg = encrypt_payload(plaintext, password)

        tampered_bytes = bytearray(pkg.ciphertext)
        tampered_bytes[0] ^= 0x01

        tampered_pkg = EncryptedPackage(
            version=pkg.version,
            salt=pkg.salt,
            nonce=pkg.nonce,
            ciphertext=bytes(tampered_bytes),
            tag=pkg.tag
        )

        with self.assertRaises(AuthenticationError):
            decrypt_payload(tampered_pkg, password)

    def test_tampered_nonce_fails_authentication(self):
        plaintext = "Confidential Patient Data"
        password = "correct_password"

        pkg = encrypt_payload(plaintext, password)

        tampered_nonce = bytearray(pkg.nonce)
        tampered_nonce[0] ^= 0x01

        tampered_pkg = EncryptedPackage(
            version=pkg.version,
            salt=pkg.salt,
            nonce=bytes(tampered_nonce),
            ciphertext=pkg.ciphertext,
            tag=pkg.tag
        )

        with self.assertRaises(AuthenticationError):
            decrypt_payload(tampered_pkg, password)

    def test_empty_plaintext_raises_error(self):
        with self.assertRaises(CryptoError):
            encrypt_payload("", "password")


if __name__ == "__main__":
    unittest.main()
