"""
Unit tests for EncryptedPackage dataclass & serialization.
"""

import unittest
from crypto.models.package import EncryptedPackage
from crypto.models.exceptions import CorruptedPayloadError


class TestEncryptedPackage(unittest.TestCase):

    def test_package_serialization_roundtrip(self):
        pkg = EncryptedPackage(
            version="KDR-CA-AEAD-v1",
            salt=b"\x01" * 16,
            nonce=b"\x02" * 12,
            ciphertext=b"encrypted_data_bytes",
            tag=b"\x03" * 32,
        )

        json_str = pkg.to_json()
        self.assertIn("KDR-CA-AEAD-v1", json_str)

        restored_pkg = EncryptedPackage.from_json(json_str)
        self.assertEqual(pkg, restored_pkg)

    def test_invalid_json_raises_corrupted_payload_error(self):
        with self.assertRaises(CorruptedPayloadError):
            EncryptedPackage.from_json("invalid json string")

    def test_missing_fields_raises_corrupted_payload_error(self):
        invalid_dict = {"version": "v1", "salt": "010203"}
        with self.assertRaises(CorruptedPayloadError):
            EncryptedPackage.from_dict(invalid_dict)


if __name__ == "__main__":
    unittest.main()
