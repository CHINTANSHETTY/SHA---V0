"""
Unit tests for CSPRNG random generation.
"""

import unittest
from crypto.primitives.random import generate_salt, generate_nonce


class TestCSPRNG(unittest.TestCase):

    def test_salt_generation(self):
        salt1 = generate_salt(16)
        salt2 = generate_salt(16)
        self.assertEqual(len(salt1), 16)
        self.assertEqual(len(salt2), 16)
        self.assertNotEqual(salt1, salt2)

    def test_nonce_generation(self):
        nonce1 = generate_nonce(12)
        nonce2 = generate_nonce(12)
        self.assertEqual(len(nonce1), 12)
        self.assertEqual(len(nonce2), 12)
        self.assertNotEqual(nonce1, nonce2)

    def test_invalid_length_raises(self):
        with self.assertRaises(ValueError):
            generate_salt(0)
        with self.assertRaises(ValueError):
            generate_nonce(-1)


if __name__ == "__main__":
    unittest.main()
