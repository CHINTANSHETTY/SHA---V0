"""
Unit tests for HMAC-SHA256 implementation.
Includes RFC 4231 test vectors.
"""

import unittest
from crypto.primitives.hmac import generate_hmac, verify_hmac


class TestHMAC(unittest.TestCase):

    def test_rfc4231_test_case_1(self):
        """RFC 4231 Test Case 1."""
        key = bytes.fromhex("0b" * 20)
        data = b"Hi There"
        expected_tag = bytes.fromhex(
            "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
        )

        tag = generate_hmac(key, data)
        self.assertEqual(tag, expected_tag)

        self.assertTrue(verify_hmac(key, data, expected_tag))

    def test_invalid_tag_fails_verification(self):
        key = b"secret_key_12345"
        data = b"Patient Payload Data"
        valid_tag = generate_hmac(key, data)

        # Alter single bit in tag
        corrupted_tag = bytearray(valid_tag)
        corrupted_tag[0] ^= 0x01

        self.assertFalse(verify_hmac(key, data, bytes(corrupted_tag)))

    def test_tampered_data_fails_verification(self):
        key = b"secret_key_12345"
        data = b"Patient Payload Data"
        valid_tag = generate_hmac(key, data)

        tampered_data = b"Patient Payload Data!"
        self.assertFalse(verify_hmac(key, tampered_data, valid_tag))

    def test_empty_key_raises(self):
        with self.assertRaises(ValueError):
            generate_hmac(b"", b"data")


if __name__ == "__main__":
    unittest.main()
