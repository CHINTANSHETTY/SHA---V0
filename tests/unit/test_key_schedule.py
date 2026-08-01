"""
Unit tests for KeySchedule dynamic sub-key expansion.
"""

import unittest
from crypto.engine.key_schedule import KeySchedule
from crypto.models.exceptions import KeyDerivationError


class TestKeySchedule(unittest.TestCase):

    def test_key_schedule_derivation(self):
        password = "hospital123_doctor01"
        salt = b"\x01" * 16
        nonce = b"\x02" * 12

        ks = KeySchedule(password, salt, nonce)

        rule_table = ks.get_ca_rule_table()
        cipher_key = ks.get_cipher_key()
        mac_key = ks.get_mac_key()

        self.assertEqual(len(rule_table), 32)
        self.assertEqual(len(cipher_key), 32)
        self.assertEqual(len(mac_key), 32)

        # Ensure sub-keys are mutually distinct
        self.assertNotEqual(bytes(rule_table), cipher_key)
        self.assertNotEqual(cipher_key, mac_key)
        self.assertNotEqual(bytes(rule_table), mac_key)

    def test_different_salt_nonce_produces_different_subkeys(self):
        password = "hospital123_doctor01"
        ks1 = KeySchedule(password, b"\x01" * 16, b"\x02" * 12)
        ks2 = KeySchedule(password, b"\x02" * 16, b"\x02" * 12)

        self.assertNotEqual(ks1.get_cipher_key(), ks2.get_cipher_key())
        self.assertNotEqual(ks1.get_ca_rule_table(), ks2.get_ca_rule_table())

    def test_invalid_parameters_raise_error(self):
        with self.assertRaises(KeyDerivationError):
            KeySchedule("", b"\x01" * 16, b"\x02" * 12)
        with self.assertRaises(KeyDerivationError):
            KeySchedule("pass", b"\x01" * 15, b"\x02" * 12)
        with self.assertRaises(KeyDerivationError):
            KeySchedule("pass", b"\x01" * 16, b"\x02" * 11)


if __name__ == "__main__":
    unittest.main()
