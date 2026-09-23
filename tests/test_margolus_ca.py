"""
Unit tests for margolus_ca.py module.
Verifies non-shifted 2x2 Margolus CA transformation, rule tables, state ordering,
input validation, and 100% loss-less reversibility.
"""

import random
import unittest
from ca_matrix import MATRIX_ROWS, MATRIX_COLS
from margolus_ca import (
    FORWARD_RULE,
    INVERSE_RULE,
    neighborhood_to_state,
    state_to_neighborhood,
    apply_margolus_forward,
    apply_margolus_inverse,
)


class TestMargolusCA(unittest.TestCase):

    def test_a_rule_table_integrity_and_invertibility(self):
        """TEST A: Rule Table Verification & Self-Inversion Identity INVERSE[FORWARD[x]] == x."""
        expected_forward = [
            0x0E, 0x04, 0x0B, 0x02,
            0x03, 0x08, 0x00, 0x09,
            0x01, 0x0A, 0x07, 0x0F,
            0x06, 0x0C, 0x05, 0x0D
        ]

        expected_inverse = [
            0x06, 0x08, 0x03, 0x04,
            0x01, 0x0E, 0x0C, 0x0A,
            0x05, 0x07, 0x09, 0x02,
            0x0D, 0x0F, 0x00, 0x0B
        ]

        self.assertEqual(FORWARD_RULE, expected_forward)
        self.assertEqual(INVERSE_RULE, expected_inverse)

        # Confirm exact invertibility for all 16 states
        for x in range(16):
            fwd = FORWARD_RULE[x]
            inv = INVERSE_RULE[fwd]
            self.assertEqual(
                inv, x,
                f"Rule inversion failed for state 0x{x:X}: INVERSE[FORWARD[0x{x:X}]] = 0x{inv:X}"
            )

    def test_b_all_zero_matrix(self):
        """TEST B: All-zero 16x16 matrix -> Forward (all 0x0 -> 0xE) -> Inverse -> Exact recovery."""
        zero_matrix = [[0] * 16 for _ in range(16)]

        forward_matrix = apply_margolus_forward(zero_matrix)

        # In zero matrix, every 2x2 neighborhood is 0x0. FORWARD_RULE[0x0] = 0x0E (1110_2).
        for r in range(0, MATRIX_ROWS, 2):
            for c in range(0, MATRIX_COLS, 2):
                st = neighborhood_to_state(forward_matrix, r, c)
                self.assertEqual(st, 0x0E)

        recovered_matrix = apply_margolus_inverse(forward_matrix)
        self.assertEqual(recovered_matrix, zero_matrix)

    def test_c_all_one_matrix(self):
        """TEST C: All-one 16x16 matrix -> Forward (all 0xF -> 0xD) -> Inverse -> Exact recovery."""
        ones_matrix = [[1] * 16 for _ in range(16)]

        forward_matrix = apply_margolus_forward(ones_matrix)

        # In all-one matrix, every 2x2 neighborhood is 0xF. FORWARD_RULE[0xF] = 0x0D (1101_2).
        for r in range(0, MATRIX_ROWS, 2):
            for c in range(0, MATRIX_COLS, 2):
                st = neighborhood_to_state(forward_matrix, r, c)
                self.assertEqual(st, 0x0D)

        recovered_matrix = apply_margolus_inverse(forward_matrix)
        self.assertEqual(recovered_matrix, ones_matrix)

    def test_d_single_neighborhood(self):
        """
        TEST D: Zero matrix with top-left neighborhood set to 0xB (1011_2) ->
        Forward rule produces 0xF (1111_2) at (0, 0) -> Inverse recovers exact original matrix.
        """
        matrix = [[0] * 16 for _ in range(16)]
        # Top-left [1 0 / 1 1] = 1011_2 = 0xB
        matrix[0][0] = 1
        matrix[0][1] = 0
        matrix[1][0] = 1
        matrix[1][1] = 1

        self.assertEqual(neighborhood_to_state(matrix, 0, 0), 0x0B)

        forward_matrix = apply_margolus_forward(matrix)

        # Top-left block must transform 0xB -> FORWARD_RULE[0xB] = 0xF (1111_2 = all 1s)
        self.assertEqual(neighborhood_to_state(forward_matrix, 0, 0), 0x0F)
        self.assertEqual(forward_matrix[0][0], 1)
        self.assertEqual(forward_matrix[0][1], 1)
        self.assertEqual(forward_matrix[1][0], 1)
        self.assertEqual(forward_matrix[1][1], 1)

        # All other 63 neighborhoods were 0x0, so they become 0x0E (1110_2)
        for r in range(0, MATRIX_ROWS, 2):
            for c in range(0, MATRIX_COLS, 2):
                if (r, c) != (0, 0):
                    self.assertEqual(neighborhood_to_state(forward_matrix, r, c), 0x0E)

        recovered_matrix = apply_margolus_inverse(forward_matrix)
        self.assertEqual(recovered_matrix, matrix)

    def test_e_all_16_states_individually(self):
        """TEST E: Test each of the 16 states 0..15 in first neighborhood -> Forward -> Inverse."""
        for state in range(16):
            matrix = [[0] * 16 for _ in range(16)]
            state_to_neighborhood(matrix, 0, 0, state)

            self.assertEqual(
                neighborhood_to_state(matrix, 0, 0), state,
                f"State encoding mismatch for state 0x{state:X}"
            )

            forward_matrix = apply_margolus_forward(matrix)
            fwd_state = neighborhood_to_state(forward_matrix, 0, 0)

            self.assertEqual(
                fwd_state, FORWARD_RULE[state],
                f"Forward transformation failed for state 0x{state:X}: got 0x{fwd_state:X}, expected 0x{FORWARD_RULE[state]:X}"
            )

            recovered_matrix = apply_margolus_inverse(forward_matrix)
            self.assertEqual(
                recovered_matrix, matrix,
                f"Inverse transformation recovery failed for state 0x{state:X}"
            )

    def test_f_random_deterministic_matrices(self):
        """TEST F: Multiple random 16x16 matrices (fixed seed) -> apply_margolus_inverse(apply_margolus_forward(M)) == M."""
        random.seed(20260922)

        for trial in range(20):
            matrix = [
                [random.randint(0, 1) for _ in range(16)]
                for _ in range(16)
            ]

            forward_matrix = apply_margolus_forward(matrix)
            recovered_matrix = apply_margolus_inverse(forward_matrix)

            self.assertEqual(
                recovered_matrix, matrix,
                f"Round-trip failed on random trial {trial}"
            )

    def test_g_dimension_validation(self):
        """TEST G: Reject invalid matrix dimensions with ValueError."""
        # 15x16 matrix
        short_rows = [[0] * 16 for _ in range(15)]
        with self.assertRaises(ValueError):
            apply_margolus_forward(short_rows)

        # 16x15 matrix
        short_cols = [[0] * 16 for _ in range(16)]
        short_cols[3] = [0] * 15
        with self.assertRaises(ValueError):
            apply_margolus_forward(short_cols)

        # 17x16 matrix
        long_rows = [[0] * 16 for _ in range(17)]
        with self.assertRaises(ValueError):
            apply_margolus_forward(long_rows)

    def test_h_binary_validation(self):
        """TEST H: Reject non-binary elements in matrix with ValueError."""
        bad_matrix = [[0] * 16 for _ in range(16)]
        bad_matrix[4][5] = 2

        with self.assertRaises(ValueError):
            apply_margolus_forward(bad_matrix)

        with self.assertRaises(ValueError):
            apply_margolus_inverse(bad_matrix)


if __name__ == "__main__":
    unittest.main()
