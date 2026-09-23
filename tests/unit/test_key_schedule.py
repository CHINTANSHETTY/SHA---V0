"""Unit tests for KeySchedule module.

Tests domain separation, key independence, KeyMaterial export, and invalid parameters.
"""

import unittest
from crypto.engine.key_schedule import KeySchedule, KeyMaterial
from crypto.models.exceptions import KeyDerivationError


class TestKeySchedule(unittest.TestCase):

    def setUp(self):
        self.master_key = b"super_secret_master_key_123"
        self.salt = b"\x01" * 16
        self.nonce = b"\x02" * 12

    def test_key_schedule_derivation(self):
        ks = KeySchedule(self.master_key, self.salt, self.nonce)
        km = ks.export_key_material()

        self.assertIsInstance(km, KeyMaterial)
        self.assertEqual(len(km.rule_seed), 32)
        self.assertEqual(km.rule_key, km.rule_seed)
        self.assertEqual(len(km.cipher_key), 32)
        self.assertEqual(len(km.mac_key), 32)
        self.assertEqual(len(km.rule_table), 32)
        self.assertEqual(km.algorithm_id, "KDR-CA-AEAD-v1")

        self.assertIsInstance(km.rule_table, tuple)
        for rule in km.rule_table:
            self.assertIsInstance(rule, int)
            self.assertTrue(0 <= rule <= 255)

    def test_key_domain_separation(self):
        """Verify K_r, K_c, and K_a are mutually independent."""
        ks = KeySchedule(self.master_key, self.salt, self.nonce)
        self.assertNotEqual(ks.get_cipher_key(), ks.get_mac_key())
        self.assertNotEqual(ks.get_cipher_key(), ks.export_key_material().rule_key)
        self.assertNotEqual(ks.get_mac_key(), ks.export_key_material().rule_key)

    def test_deterministic_output(self):
        """Same parameters must yield identical KeyMaterial."""
        ks1 = KeySchedule(self.master_key, self.salt, self.nonce)
        ks2 = KeySchedule(self.master_key, self.salt, self.nonce)
        self.assertEqual(ks1.export_key_material(), ks2.export_key_material())

    def test_factory_method(self):
        """Test from_master_key factory method."""
        ks = KeySchedule.from_master_key(self.master_key, self.salt, self.nonce)
        self.assertEqual(len(ks.get_cipher_key()), 32)

    def test_invalid_parameters_raise_exception(self):
        with self.assertRaises(KeyDerivationError):
            KeySchedule(b"", self.salt, self.nonce)
        with self.assertRaises(KeyDerivationError):
            KeySchedule(self.master_key, b"short_salt", self.nonce)
        with self.assertRaises(KeyDerivationError):
            KeySchedule(self.master_key, self.salt, b"short_nonce")


if __name__ == "__main__":
    unittest.main()
