"""
Unit tests for ca_transform.py module.
Verifies complete two-round 2x2 Margolus CA transformation pipeline with 2D circular matrix shift,
input validation, dimension preservation, and 100% loss-less reversibility.
"""

import random
import unittest
from ca_matrix import BLOCK_SIZE, MATRIX_ROWS, MATRIX_COLS, block_to_matrix
from margolus_ca import FORWARD_RULE, INVERSE_RULE
from margolus_shifted import state_to_shifted_neighborhood, shifted_neighborhood_to_state
from ca_transform import (
    circular_shift_matrix,
    inverse_circular_shift_matrix,
    transform_block_forward,
    transform_block_inverse,
)


class TestCATransform(unittest.TestCase):

    def test_a_all_zero_block_roundtrip(self):
        """TEST A: All-zero 256-bit block -> Forward -> Inverse -> Exact recovery."""
        zero_block = "0" * BLOCK_SIZE
        transformed = transform_block_forward(zero_block)
        recovered = transform_block_inverse(transformed)

        self.assertEqual(recovered, zero_block)

    def test_b_all_one_block_roundtrip(self):
        """TEST B: All-one 256-bit block -> Forward -> Inverse -> Exact recovery."""
        ones_block = "1" * BLOCK_SIZE
        transformed = transform_block_forward(ones_block)
        recovered = transform_block_inverse(transformed)

        self.assertEqual(recovered, ones_block)

    def test_c_alternating_block_roundtrip(self):
        """TEST C: 256-bit alternating '01' block -> Forward -> Inverse -> Exact recovery."""
        alt_block = "01" * (BLOCK_SIZE // 2)
        transformed = transform_block_forward(alt_block)
        recovered = transform_block_inverse(transformed)

        self.assertEqual(recovered, alt_block)

    def test_d_deterministic_pattern_roundtrip(self):
        """TEST D: Custom deterministic 256-bit block -> Forward -> Inverse -> Exact recovery."""
        det_block = ("11000011" * 8 + "00111100" * 8 + "10101010" * 8 + "01010101" * 8)[:256]
        self.assertEqual(len(det_block), BLOCK_SIZE)

        transformed = transform_block_forward(det_block)
        recovered = transform_block_inverse(transformed)

        self.assertEqual(recovered, det_block)

    def test_e_all_16_local_states_roundtrip(self):
        """TEST E: Representative blocks containing each of the 16 4-bit states -> Forward -> Inverse."""
        for state in range(16):
            matrix = [[0] * 16 for _ in range(16)]
            state_to_shifted_neighborhood(matrix, 0, 0, state)

            # Convert matrix to 256-bit block string
            block = "".join("".join(str(val) for val in row) for row in matrix)
            self.assertEqual(len(block), BLOCK_SIZE)

            transformed = transform_block_forward(block)
            recovered = transform_block_inverse(transformed)

            self.assertEqual(
                recovered, block,
                f"Block transform round-trip failed for local state 0x{state:X}"
            )

    def test_f_100_random_blocks_roundtrip(self):
        """TEST F: 100 deterministic random 256-bit blocks (fixed seed) -> 100% loss-less recovery."""
        random.seed(20260922)

        for trial in range(100):
            block_bits = [str(random.randint(0, 1)) for _ in range(256)]
            block = "".join(block_bits)

            transformed = transform_block_forward(block)
            recovered = transform_block_inverse(transformed)

            self.assertEqual(
                recovered, block,
                f"Block transform round-trip failed on random trial {trial}"
            )

    def test_g_length_validation(self):
        """TEST G: Reject 255-bit and 257-bit input strings with ValueError."""
        short_block = "0" * 255
        long_block = "0" * 257

        with self.assertRaises(ValueError):
            transform_block_forward(short_block)

        with self.assertRaises(ValueError):
            transform_block_inverse(short_block)

        with self.assertRaises(ValueError):
            transform_block_forward(long_block)

        with self.assertRaises(ValueError):
            transform_block_inverse(long_block)

    def test_h_invalid_character_validation(self):
        """TEST H: Reject 256-char string containing non-binary characters with ValueError."""
        invalid_block = ("0" * 200) + "A" + ("1" * 55)

        with self.assertRaises(ValueError):
            transform_block_forward(invalid_block)

        with self.assertRaises(ValueError):
            transform_block_inverse(invalid_block)

    def test_i_shift_roundtrip_identity(self):
        """TEST I: Verify inverse_circular_shift_matrix(circular_shift_matrix(M)) == M."""
        random.seed(20260922)

        for trial in range(20):
            matrix = [
                [random.randint(0, 1) for _ in range(16)]
                for _ in range(16)
            ]

            shifted = circular_shift_matrix(matrix, row_shift=1, col_shift=1)
            restored = inverse_circular_shift_matrix(shifted, row_shift=1, col_shift=1)

            self.assertEqual(
                restored, matrix,
                f"2D circular shift round-trip failed on trial {trial}"
            )

    def test_j_matrix_dimensions_preserved(self):
        """TEST J: Verify all intermediate and final matrix representations remain 16x16."""
        block = "10" * 128
        matrix_0 = block_to_matrix(block)
        self.assertEqual(len(matrix_0), MATRIX_ROWS)
        self.assertTrue(all(len(row) == MATRIX_COLS for row in matrix_0))

        shifted = circular_shift_matrix(matrix_0, 1, 1)
        self.assertEqual(len(shifted), MATRIX_ROWS)
        self.assertTrue(all(len(row) == MATRIX_COLS for row in shifted))

        restored = inverse_circular_shift_matrix(shifted, 1, 1)
        self.assertEqual(len(restored), MATRIX_ROWS)
        self.assertTrue(all(len(row) == MATRIX_COLS for row in restored))


if __name__ == "__main__":
    unittest.main()
