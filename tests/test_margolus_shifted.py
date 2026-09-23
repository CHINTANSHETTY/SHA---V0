"""
Unit tests for margolus_shifted.py module.
Verifies shifted (second partition) 2x2 Margolus CA transformation, periodic boundary
wrap-around modulo 16, non-overlapping partition proof, and 100% loss-less reversibility.
"""

import random
import unittest
from ca_matrix import MATRIX_ROWS, MATRIX_COLS
from margolus_ca import FORWARD_RULE, INVERSE_RULE
from margolus_shifted import (
    SHIFTED_ROWS,
    SHIFTED_COLS,
    shifted_neighborhood_to_state,
    state_to_shifted_neighborhood,
    get_shifted_neighborhood_cells,
    apply_shifted_margolus_forward,
    apply_shifted_margolus_inverse,
)


class TestMargolusShiftedCA(unittest.TestCase):

    def test_a_shifted_neighborhood_count(self):
        """TEST A: Verify shifted coordinate set contains exactly 64 neighborhoods."""
        self.assertEqual(len(SHIFTED_ROWS), 8)
        self.assertEqual(len(SHIFTED_COLS), 8)

        neighborhood_count = len(SHIFTED_ROWS) * len(SHIFTED_COLS)
        self.assertEqual(
            neighborhood_count, 64,
            f"Expected exactly 64 shifted neighborhoods, got {neighborhood_count}."
        )

    def test_b_every_cell_belongs_to_exactly_one_neighborhood(self):
        """
        TEST B: Partition Proof — Verify every cell (r, c) in the 16x16 periodic grid
        belongs to EXACTLY ONE shifted neighborhood.
        """
        coverage_count = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]

        for r in SHIFTED_ROWS:
            for c in SHIFTED_COLS:
                cells = get_shifted_neighborhood_cells(r, c)
                self.assertEqual(len(cells), 4)
                for (cell_r, cell_c) in cells:
                    coverage_count[cell_r][cell_c] += 1

        # Confirm every single cell in the 16x16 matrix has coverage_count == 1
        for r in range(MATRIX_ROWS):
            for c in range(MATRIX_COLS):
                self.assertEqual(
                    coverage_count[r][c], 1,
                    f"Cell ({r}, {c}) covered {coverage_count[r][c]} times instead of exactly 1 time."
                )

    def test_c_boundary_neighborhood_wraparound(self):
        """
        TEST C: Boundary wrap-around check for neighborhood starting at (15, 15).
        Must map to (15, 15), (15, 0), (0, 15), (0, 0).
        """
        cells_15_15 = get_shifted_neighborhood_cells(15, 15)
        expected_cells = [(15, 15), (15, 0), (0, 15), (0, 0)]
        self.assertEqual(cells_15_15, expected_cells)

        matrix = [[0] * 16 for _ in range(16)]
        matrix[15][15] = 1
        matrix[15][0] = 0
        matrix[0][15] = 1
        matrix[0][0] = 1

        state = shifted_neighborhood_to_state(matrix, 15, 15)
        self.assertEqual(state, 0x0B)  # 1011_2 = 0xB

    def test_d_known_state_shifted_transformation(self):
        """TEST D: Place known state 0xB at shifted neighborhood -> Verify forward rule 0xB -> 0xF."""
        matrix = [[0] * 16 for _ in range(16)]
        state_to_shifted_neighborhood(matrix, 3, 5, 0x0B)

        self.assertEqual(shifted_neighborhood_to_state(matrix, 3, 5), 0x0B)

        forward_matrix = apply_shifted_margolus_forward(matrix)
        fwd_state = shifted_neighborhood_to_state(forward_matrix, 3, 5)

        self.assertEqual(fwd_state, FORWARD_RULE[0x0B])  # 0xB -> 0xF
        self.assertEqual(fwd_state, 0x0F)

        recovered_matrix = apply_shifted_margolus_inverse(forward_matrix)
        self.assertEqual(recovered_matrix, matrix)

    def test_e_all_16_states_shifted(self):
        """TEST E: Test all 16 states 0..15 placed at shifted neighborhood (7, 9) -> Forward -> Inverse."""
        for state in range(16):
            matrix = [[0] * 16 for _ in range(16)]
            state_to_shifted_neighborhood(matrix, 7, 9, state)

            self.assertEqual(shifted_neighborhood_to_state(matrix, 7, 9), state)

            forward_matrix = apply_shifted_margolus_forward(matrix)
            fwd_state = shifted_neighborhood_to_state(forward_matrix, 7, 9)

            self.assertEqual(fwd_state, FORWARD_RULE[state])

            recovered_matrix = apply_shifted_margolus_inverse(forward_matrix)
            self.assertEqual(recovered_matrix, matrix)

    def test_f_all_zero_matrix(self):
        """TEST F: All-zero matrix -> apply_shifted_margolus_inverse(apply_shifted_margolus_forward(M)) == M."""
        zero_matrix = [[0] * 16 for _ in range(16)]

        forward_matrix = apply_shifted_margolus_forward(zero_matrix)
        recovered_matrix = apply_shifted_margolus_inverse(forward_matrix)

        self.assertEqual(recovered_matrix, zero_matrix)

    def test_g_all_one_matrix(self):
        """TEST G: All-one matrix -> apply_shifted_margolus_inverse(apply_shifted_margolus_forward(M)) == M."""
        ones_matrix = [[1] * 16 for _ in range(16)]

        forward_matrix = apply_shifted_margolus_forward(ones_matrix)
        recovered_matrix = apply_shifted_margolus_inverse(forward_matrix)

        self.assertEqual(recovered_matrix, ones_matrix)

    def test_h_alternating_matrix(self):
        """TEST H: Alternating 01 matrix -> apply_shifted_margolus_inverse(apply_shifted_margolus_forward(M)) == M."""
        alt_matrix = [[(r + c) % 2 for c in range(16)] for r in range(16)]

        forward_matrix = apply_shifted_margolus_forward(alt_matrix)
        recovered_matrix = apply_shifted_margolus_inverse(forward_matrix)

        self.assertEqual(recovered_matrix, alt_matrix)

    def test_i_random_deterministic_matrices(self):
        """TEST I: 20 random deterministic 16x16 matrices (fixed seed) -> Exact round-trip recovery."""
        random.seed(20260922)

        for trial in range(20):
            matrix = [
                [random.randint(0, 1) for _ in range(16)]
                for _ in range(16)
            ]

            forward_matrix = apply_shifted_margolus_forward(matrix)
            recovered_matrix = apply_shifted_margolus_inverse(forward_matrix)

            self.assertEqual(
                recovered_matrix, matrix,
                f"Shifted round-trip failed on random trial {trial}"
            )

    def test_j_matrix_dimensions_preserved(self):
        """TEST J: Verify that output matrix dimensions remain exactly 16x16."""
        matrix = [[1] * 16 for _ in range(16)]
        forward_matrix = apply_shifted_margolus_forward(matrix)

        self.assertEqual(len(forward_matrix), MATRIX_ROWS)
        self.assertTrue(all(len(row) == MATRIX_COLS for row in forward_matrix))


if __name__ == "__main__":
    unittest.main()
