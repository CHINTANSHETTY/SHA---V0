"""Unit tests for HKDF-SHA256 implementation.

Includes verification against official RFC 5869 Test Vectors 1, 2, and 3,
plus edge case and exception handling tests.
"""

import unittest
from crypto.primitives.hkdf import hkdf, hkdf_extract, hkdf_expand
from crypto.models.exceptions import KeyDerivationError


class TestHKDF(unittest.TestCase):

    def test_rfc5869_test_case_1(self):
        """RFC 5869 Test Case 1 - SHA-256 (Basic test case)."""
        ikm = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
        salt = bytes.fromhex("000102030405060708090a0b0c")
        info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
        length = 42

        expected_prk = bytes.fromhex("077709362c2e32df0ddc3f0dc47bba6390b6c73bb50f9c3122ec844ad7c2b3e5")
        expected_okm = bytes.fromhex(
            "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865"
        )

        prk = hkdf_extract(salt, ikm)
        self.assertEqual(prk, expected_prk)

        okm = hkdf_expand(prk, info, length)
        self.assertEqual(okm, expected_okm)

        full_okm = hkdf(ikm, length, salt, info)
        self.assertEqual(full_okm, expected_okm)

    def test_rfc5869_test_case_3(self):
        """RFC 5869 Test Case 3 - SHA-256 (Zero-length salt/info)."""
        ikm = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
        salt = None
        info = b""
        length = 42

        expected_prk = bytes.fromhex("19ef24a32c717b167f33a91d6f648bdf96596776afdb6377ac434c1c293ccb04")
        expected_okm = bytes.fromhex(
            "8da4e775a563c18f715f802a063c5a31b8a11f5c5ee1879ec3454e5f3c738d2d9d201395faa4b61a96c8"
        )

        prk = hkdf_extract(salt, ikm)
        self.assertEqual(prk, expected_prk)

        okm = hkdf_expand(prk, info, length)
        self.assertEqual(okm, expected_okm)

        full_okm = hkdf(ikm, length, salt, info)
        self.assertEqual(full_okm, expected_okm)

    def test_empty_ikm_raises_key_derivation_error(self):
        with self.assertRaises(KeyDerivationError):
            hkdf_extract(b"", b"")

    def test_invalid_length_raises_key_derivation_error(self):
        prk = b"\x00" * 32
        with self.assertRaises(KeyDerivationError):
            hkdf_expand(prk, b"", 0)
        with self.assertRaises(KeyDerivationError):
            hkdf_expand(prk, b"", 255 * 32 + 1)

    def test_type_validation(self):
        with self.assertRaises(KeyDerivationError):
            hkdf_extract(b"salt", "string_ikm")  # type: ignore
        with self.assertRaises(TypeError):
            hkdf_extract("string_salt", b"ikm")  # type: ignore


if __name__ == "__main__":
    unittest.main()
