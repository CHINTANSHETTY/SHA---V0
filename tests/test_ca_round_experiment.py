"""
Unit tests for ca_round_experiment.py module.
Verifies 100% loss-less reversibility across 2, 4, 6, 8, and 10 CA rounds,
invalid round count validation, matrix dimension preservation, and metric calculation functions.
"""

import random
import unittest
from ca_matrix import BLOCK_SIZE, MATRIX_ROWS, MATRIX_COLS, block_to_matrix
from ca_round_experiment import (
    VALID_ROUND_COUNTS,
    apply_ca_rounds,
    apply_ca_rounds_inverse,
    transform_block_with_rounds,
    inverse_transform_block_with_rounds,
    calculate_hamming_distance,
    calculate_bit_avalanche,
    calculate_bit_npcr,
    calculate_bit_uaci,
)


class TestCARoundExperiment(unittest.TestCase):

    def test_reversibility_across_all_valid_round_counts(self):
        """
        Test exact reversibility inverse_transform(transform(B, R), R) == B
        for rounds in (2, 4, 6, 8, 10) across zero, ones, alternating, and deterministic blocks.
        """
        test_blocks = [
            "0" * BLOCK_SIZE,
            "1" * BLOCK_SIZE,
            "01" * (BLOCK_SIZE // 2),
            ("11000011" * 16 + "00111100" * 16)[:BLOCK_SIZE],
        ]

        for rounds in VALID_ROUND_COUNTS:
            for block in test_blocks:
                transformed = transform_block_with_rounds(block, rounds)
                recovered = inverse_transform_block_with_rounds(transformed, rounds)

                self.assertEqual(
                    recovered, block,
                    f"Reversibility failed for rounds={rounds} on block {block[:16]}..."
                )

    def test_100_random_blocks_reversibility(self):
        """
        Test 100 deterministic random 256-bit blocks across ALL round counts in (2, 4, 6, 8, 10).
        """
        random.seed(20260923)

        for rounds in VALID_ROUND_COUNTS:
            for trial in range(100):
                block_bits = [str(random.randint(0, 1)) for _ in range(BLOCK_SIZE)]
                block = "".join(block_bits)

                transformed = transform_block_with_rounds(block, rounds)
                recovered = inverse_transform_block_with_rounds(transformed, rounds)

                self.assertEqual(
                    recovered, block,
                    f"Reversibility failed for rounds={rounds} on trial {trial}"
                )

    def test_invalid_round_counts_rejected(self):
        """Verify that odd or out-of-range round counts raise ValueError."""
        invalid_counts = [-1, 0, 1, 3, 5, 7, 9, 12, 16]
        matrix = [[0] * 16 for _ in range(16)]

        for r in invalid_counts:
            with self.assertRaises(ValueError):
                apply_ca_rounds(matrix, r)

            with self.assertRaises(ValueError):
                apply_ca_rounds_inverse(matrix, r)

            with self.assertRaises(ValueError):
                transform_block_with_rounds("0" * BLOCK_SIZE, r)

            with self.assertRaises(ValueError):
                inverse_transform_block_with_rounds("0" * BLOCK_SIZE, r)

    def test_matrix_dimensions_preserved(self):
        """Verify that all intermediate and output matrices maintain 16x16 dimensions."""
        matrix = [[1] * 16 for _ in range(16)]

        for rounds in VALID_ROUND_COUNTS:
            transformed = apply_ca_rounds(matrix, rounds)
            self.assertEqual(len(transformed), MATRIX_ROWS)
            self.assertTrue(all(len(row) == MATRIX_COLS for row in transformed))

            recovered = apply_ca_rounds_inverse(transformed, rounds)
            self.assertEqual(len(recovered), MATRIX_ROWS)
            self.assertTrue(all(len(row) == MATRIX_COLS for row in recovered))

    def test_metrics_calculation_functions(self):
        """Verify Hamming distance, Bit Avalanche, NPCR, and UACI calculation functions."""
        str_a = "0" * 256
        str_b = ("1" * 128) + ("0" * 128)  # Exactly 128 bits differ

        dist = calculate_hamming_distance(str_a, str_b)
        self.assertEqual(dist, 128)

        av = calculate_bit_avalanche(str_a, str_b)
        self.assertEqual(av, 50.0)

        npcr = calculate_bit_npcr(str_a, str_b)
        self.assertEqual(npcr, 50.0)

        uaci = calculate_bit_uaci(str_a, str_b)
        self.assertEqual(uaci, 50.0)


if __name__ == "__main__":
    unittest.main()
