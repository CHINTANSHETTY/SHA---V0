"""
Unit tests for Keyed Dynamic Cellular Automata engine.
"""

import unittest
from crypto.engine.dynamic_ca import apply_keyed_ca_forward, apply_keyed_ca_inverse


class TestDynamicCA(unittest.TestCase):

    def test_ca_transformation_roundtrip(self):
        rule_table = [(i * 37 + 13) % 256 for i in range(32)]
        data = b"Patient EHR Record Payload: ID=P001, Name=Rahul, Age=21, Disease=Fever"

        transformed = apply_keyed_ca_forward(data, rule_table)
        self.assertNotEqual(data, transformed)
        self.assertEqual(len(data), len(transformed))

        recovered = apply_keyed_ca_inverse(transformed, rule_table)
        self.assertEqual(data, recovered)

    def test_different_rule_table_produces_different_output(self):
        data = b"Patient Payload Data"
        table1 = [150] * 32
        table2 = [105] * 32

        out1 = apply_keyed_ca_forward(data, table1)
        out2 = apply_keyed_ca_forward(data, table2)
        self.assertNotEqual(out1, out2)

    def test_empty_data_handling(self):
        table = [30] * 32
        self.assertEqual(apply_keyed_ca_forward(b"", table), b"")
        self.assertEqual(apply_keyed_ca_inverse(b"", table), b"")


if __name__ == "__main__":
    unittest.main()
