"""
Unit tests for ca_matrix.py module.
Verifies exact 256-bit binary block <-> 16x16 matrix conversion and round-trip identity.
"""

import unittest
from ca_matrix import (
    block_to_matrix,
    matrix_to_block,
    validate_block,
    validate_matrix,
    BLOCK_SIZE,
    MATRIX_ROWS,
    MATRIX_COLS,
)


class TestCAMatrixConversion(unittest.TestCase):

    def test_a_all_zeros_block(self):
        """TEST A: All-zero 256-bit block -> 16x16 zero matrix -> round-trip."""
        zero_block = "0" * BLOCK_SIZE
        matrix = block_to_matrix(zero_block)

        # Confirm 16x16 matrix of only zeros
        self.assertEqual(len(matrix), MATRIX_ROWS)
        self.assertTrue(all(len(row) == MATRIX_COLS for row in matrix))
        self.assertTrue(all(val == 0 for row in matrix for val in row))

        # Round-trip verification
        reconstructed = matrix_to_block(matrix)
        self.assertEqual(reconstructed, zero_block)

    def test_b_all_ones_block(self):
        """TEST B: All-one 256-bit block -> 16x16 ones matrix -> round-trip."""
        ones_block = "1" * BLOCK_SIZE
        matrix = block_to_matrix(ones_block)

        # Confirm 16x16 matrix of only ones
        self.assertEqual(len(matrix), MATRIX_ROWS)
        self.assertTrue(all(len(row) == MATRIX_COLS for row in matrix))
        self.assertTrue(all(val == 1 for row in matrix for val in row))

        # Round-trip verification
        reconstructed = matrix_to_block(matrix)
        self.assertEqual(reconstructed, ones_block)

    def test_c_sequential_bit_pattern(self):
        """TEST C: Sequential 16-bit block pattern -> round-trip."""
        seq_block = ("0" * 16 + "1" * 16) * 8
        self.assertEqual(len(seq_block), BLOCK_SIZE)

        matrix = block_to_matrix(seq_block)

        # Row 0 must be 16 zeros, Row 1 must be 16 ones, etc.
        for r in range(MATRIX_ROWS):
            expected_val = 0 if (r % 2 == 0) else 1
            self.assertTrue(all(v == expected_val for v in matrix[r]))

        reconstructed = matrix_to_block(matrix)
        self.assertEqual(reconstructed, seq_block)

    def test_d_alternating_bit_pattern(self):
        """TEST D: Alternating '01' 256-bit pattern -> round-trip."""
        alt_block = "01" * (BLOCK_SIZE // 2)
        self.assertEqual(len(alt_block), BLOCK_SIZE)

        matrix = block_to_matrix(alt_block)

        # Each row must alternate [0, 1, 0, 1, ...]
        for r in range(MATRIX_ROWS):
            self.assertEqual(matrix[r], [0, 1] * 8)

        reconstructed = matrix_to_block(matrix)
        self.assertEqual(reconstructed, alt_block)

    def test_e_invalid_length(self):
        """TEST E: Invalid block length (255 and 257 bits) raises ValueError."""
        short_block = "0" * 255
        long_block = "0" * 257

        with self.assertRaises(ValueError) as ctx_short:
            block_to_matrix(short_block)
        self.assertIn("Invalid block length 255", str(ctx_short.exception))

        with self.assertRaises(ValueError) as ctx_long:
            block_to_matrix(long_block)
        self.assertIn("Invalid block length 257", str(ctx_long.exception))

    def test_f_invalid_characters(self):
        """TEST F: Invalid characters in block string raise ValueError."""
        bad_char_block_1 = ("0" * 255) + "2"
        bad_char_block_2 = ("1" * 100) + "x" + ("0" * 155)

        with self.assertRaises(ValueError) as ctx_1:
            block_to_matrix(bad_char_block_1)
        self.assertIn("Invalid character '2'", str(ctx_1.exception))

        with self.assertRaises(ValueError) as ctx_2:
            block_to_matrix(bad_char_block_2)
        self.assertIn("Invalid character 'x'", str(ctx_2.exception))

    def test_g_invalid_matrix_dimensions_and_elements(self):
        """TEST G: Invalid matrix structures raise ValueError in matrix_to_block."""
        # 15 rows instead of 16
        bad_rows_matrix = [[0] * 16 for _ in range(15)]
        with self.assertRaises(ValueError) as ctx_rows:
            matrix_to_block(bad_rows_matrix)
        self.assertIn("Invalid matrix row count 15", str(ctx_rows.exception))

        # Row with 15 columns instead of 16
        bad_cols_matrix = [[0] * 16 for _ in range(16)]
        bad_cols_matrix[5] = [0] * 15
        with self.assertRaises(ValueError) as ctx_cols:
            matrix_to_block(bad_cols_matrix)
        self.assertIn("Invalid column count 15", str(ctx_cols.exception))

        # Element value 2 instead of 0 or 1
        bad_val_matrix = [[0] * 16 for _ in range(16)]
        bad_val_matrix[2][3] = 2
        with self.assertRaises(ValueError) as ctx_val:
            matrix_to_block(bad_val_matrix)
        self.assertIn("Invalid element '2'", str(ctx_val.exception))

    def test_h_matrix_to_block_to_matrix_identity(self):
        """TEST H: Dual identity block_to_matrix(matrix_to_block(M)) == M."""
        original_matrix = [
            [(r + c) % 2 for c in range(MATRIX_COLS)]
            for r in range(MATRIX_ROWS)
        ]

        block = matrix_to_block(original_matrix)
        reconstructed_matrix = block_to_matrix(block)

        self.assertEqual(reconstructed_matrix, original_matrix)


if __name__ == "__main__":
    unittest.main()
