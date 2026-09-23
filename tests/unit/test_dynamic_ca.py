"""Unit tests for Keyed Dynamic Cellular Automata (K-DCA) engine.

Tests bijectivity roundtrip, KeyMaterial factory, DynamicCAEngine class,
boundary rule tables, avalanche propagation, and exception handling.
"""

import unittest
from crypto.engine.key_schedule import KeySchedule
from crypto.engine.dynamic_ca import (
    DynamicCAEngine,
    apply_keyed_ca_forward,
    apply_keyed_ca_inverse,
)


class TestDynamicCA(unittest.TestCase):

    def setUp(self):
        self.master_key = b"test_master_key_1234567890_abc"
        self.salt = b"\x01" * 16
        self.nonce = b"\x02" * 12
        self.ks = KeySchedule(self.master_key, self.salt, self.nonce)
        self.key_material = self.ks.export_key_material()
        self.rule_table = self.key_material.rule_table

    def test_ca_transformation_roundtrip(self):
        """Verify 100% loss-free bijectivity across various payload sizes."""
        test_payloads = [
            b"A",
            b"Hello World!",
            b"Patient EHR Record Payload: ID=P001, Name=Rahul, Age=21, Disease=Fever",
            b"\x00" * 256,
            bytes(range(256)) * 4,
        ]

        for payload in test_payloads:
            transformed = apply_keyed_ca_forward(payload, self.rule_table)
            self.assertEqual(len(payload), len(transformed))
            if len(payload) > 1:
                self.assertNotEqual(payload, transformed)

            recovered = apply_keyed_ca_inverse(transformed, self.rule_table)
            self.assertEqual(payload, recovered)

    def test_engine_class_interface(self):
        """Test DynamicCAEngine class constructor and KeyMaterial factory."""
        engine1 = DynamicCAEngine(self.rule_table)
        engine2 = DynamicCAEngine.from_key_material(self.key_material)

        self.assertEqual(engine1.rule_table, self.rule_table)
        self.assertEqual(engine2.rule_table, self.rule_table)

        payload = b"Testing Class vs Functional Equivalence Payload."
        t1 = engine1.transform_forward(payload)
        t2 = apply_keyed_ca_forward(payload, self.rule_table)
        self.assertEqual(t1, t2)

        r1 = engine2.transform_inverse(t1)
        self.assertEqual(r1, payload)

    def test_different_rule_tables_produce_different_outputs(self):
        """Verify key dependency of transformation outputs."""
        payload = b"Sensitive Medical Record Payload Data"
        table1 = tuple([150] * 32)
        table2 = tuple([105] * 32)

        out1 = apply_keyed_ca_forward(payload, table1)
        out2 = apply_keyed_ca_forward(payload, table2)
        self.assertNotEqual(out1, out2)

    def test_boundary_rule_tables(self):
        """Test with all-zero and all-255 boundary rule tables."""
        zero_table = tuple([0] * 32)
        max_table = tuple([255] * 32)
        payload = b"Boundary Rule Test Data"

        t_zero = apply_keyed_ca_forward(payload, zero_table)
        r_zero = apply_keyed_ca_inverse(t_zero, zero_table)
        self.assertEqual(payload, r_zero)

        t_max = apply_keyed_ca_forward(payload, max_table)
        r_max = apply_keyed_ca_inverse(t_max, max_table)
        self.assertEqual(payload, r_max)

    def test_empty_data_handling(self):
        """Verify empty byte buffer handling."""
        self.assertEqual(apply_keyed_ca_forward(b"", self.rule_table), b"")
        self.assertEqual(apply_keyed_ca_inverse(b"", self.rule_table), b"")

        engine = DynamicCAEngine(self.rule_table)
        self.assertEqual(engine.transform_forward(b""), b"")
        self.assertEqual(engine.transform_inverse(b""), b"")

    def test_invalid_parameters_raise_exceptions(self):
        """Verify input type and boundary validations."""
        with self.assertRaises(TypeError):
            apply_keyed_ca_forward("string_payload", self.rule_table)  # type: ignore

        with self.assertRaises(TypeError):
            apply_keyed_ca_forward(b"data", "invalid_table")  # type: ignore

        with self.assertRaises(ValueError):
            apply_keyed_ca_forward(b"data", (1, 2, 3))  # Short rule table

        with self.assertRaises(ValueError):
            apply_keyed_ca_forward(b"data", tuple([256] * 32))  # Out of uint8 range

    def test_avalanche_propagation(self):
        """Verify bit flip propagation across downstream bytes."""
        payload = b"Patient Payload: ID=P001, Name=Rahul Kumar, Disease=Fever"
        mod_payload = bytearray(payload)
        mod_payload[0] ^= 0x01  # Flip 1 bit in 1st byte

        t_orig = apply_keyed_ca_forward(payload, self.rule_table)
        t_mod = apply_keyed_ca_forward(bytes(mod_payload), self.rule_table)

        # Inter-byte state chaining should alter multiple downstream bytes
        differing_bytes = sum(1 for a, b in zip(t_orig, t_mod) if a != b)
        self.assertGreater(differing_bytes, len(payload) * 0.3)


if __name__ == "__main__":
    unittest.main()
