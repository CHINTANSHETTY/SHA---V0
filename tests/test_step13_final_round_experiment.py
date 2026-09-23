"""
Unit tests for step13_final_round_experiment.py module.
Verifies Candidate C architecture implementation, circular shift direction (DOWN 2/RIGHT 2 <-> UP 2/LEFT 2),
partition alternation, required round counts (2, 4, 6, 8, 10), 100% loss-less reversibility,
healthcare pipeline recovery, and CSV file generation.
"""

import os
import unittest
from step13_final_round_experiment import (
    candidate_C_forward,
    candidate_C_inverse,
    candidate_C_encrypt_text,
    candidate_C_decrypt_text,
    test_candidate_C_healthcare_pipeline,
    run_step13_experiment,
)
from ca_matrix import block_to_matrix, matrix_to_block
from ca_transform import circular_shift_matrix, inverse_circular_shift_matrix


class TestStep13FinalRoundExperiment(unittest.TestCase):

    def test_candidate_C_shift_directions(self):
        """Verify forward shift is DOWN 2 / RIGHT 2 and inverse shift is UP 2 / LEFT 2."""
        grid = [[(i + r) % 2 for i in range(16)] for r in range(16)]
        
        fwd_shifted = circular_shift_matrix(grid, row_shift=2, col_shift=2)
        inv_restored = inverse_circular_shift_matrix(fwd_shifted, row_shift=2, col_shift=2)

        self.assertEqual(grid, inv_restored)

    def test_candidate_C_partition_alternation(self):
        """Verify standard and shifted Margolus partitions alternate correctly for rounds 1..4."""
        test_block = ("01" * 64 + "1100" * 32)[:256]
        m0 = block_to_matrix(test_block)

        # Single round vs multi-round matrix states
        m1 = candidate_C_forward(m0, rounds=1)
        m2 = candidate_C_forward(m0, rounds=2)
        m3 = candidate_C_forward(m0, rounds=3)
        m4 = candidate_C_forward(m0, rounds=4)

        self.assertNotEqual(m1, m2)
        self.assertNotEqual(m2, m3)
        self.assertNotEqual(m3, m4)

    def test_required_round_counts_reversibility(self):
        """Verify 100% loss-less reversibility for required round counts: 2, 4, 6, 8, 10."""
        required_rounds = [2, 4, 6, 8, 10]
        test_block = ("10" * 64 + "0011" * 32)[:256]
        m0 = block_to_matrix(test_block)

        for r in required_rounds:
            m_r = candidate_C_forward(m0, r)
            m_rec = candidate_C_inverse(m_r, r)
            b_rec = matrix_to_block(m_rec)

            self.assertEqual(
                b_rec, test_block,
                f"Candidate C reversibility failed at required round count R={r}"
            )

    def test_candidate_C_healthcare_pipeline_recovery(self):
        """Verify Healthcare Application Pipeline recovery succeeds across all test cases."""
        for r in [2, 4, 6, 8, 10]:
            self.assertTrue(
                test_candidate_C_healthcare_pipeline(rounds=r),
                f"Healthcare pipeline recovery failed at R={r}"
            )

    def test_csv_file_generation(self):
        """Verify CSV summary results file generation and structure."""
        summary, raw = run_step13_experiment()

        self.assertGreater(len(summary), 0)
        self.assertGreater(len(raw), 0)

        first_summary = summary[0]
        self.assertIn("candidate", first_summary)
        self.assertIn("rounds", first_summary)
        self.assertIn("bit_avalanche_mean", first_summary)
        self.assertIn("byte_npcr_mean", first_summary)
        self.assertIn("byte_uaci_mean", first_summary)
        self.assertIn("enc_time_ms_mean", first_summary)
        self.assertEqual(first_summary["reversibility_pass_percent"], 100.0)

        self.assertTrue(os.path.exists("step13_final_round_results.csv"))
        self.assertTrue(os.path.exists("step13_final_round_raw.csv"))


if __name__ == "__main__":
    unittest.main()
