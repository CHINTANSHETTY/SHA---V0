"""
Unit tests for step12_architecture_validation.py module.
Verifies Candidates A..D forward/inverse transformations, Candidate C circular shift,
Candidate D schedule sequence, 100% loss-less reversibility, Healthcare Pipeline recovery,
and CSV file generation.
"""

import os
import unittest
from step12_architecture_validation import (
    verify_candidate_C_circular_shift,
    get_candidate_D_schedule_sequence,
    simulate_pipeline_encrypt,
    simulate_pipeline_decrypt,
    test_healthcare_pipeline_recovery,
    run_step12_validation,
    CANDIDATES,
)
from ca_matrix import block_to_matrix, matrix_to_block


class TestStep12ArchitectureValidation(unittest.TestCase):

    def test_candidate_C_circular_shift_verification(self):
        """Verify Candidate C 2D circular matrix shift (DOWN 2/RIGHT 2 <-> UP 2/LEFT 2)."""
        self.assertTrue(verify_candidate_C_circular_shift())

    def test_candidate_D_schedule_sequence(self):
        """Verify Candidate D sequence formatting for 4 rounds."""
        seq = get_candidate_D_schedule_sequence(rounds=4)
        self.assertEqual(len(seq), 6)  # 4 rounds + 2 post-pair shifts
        self.assertIn("Standard Margolus", seq[0])
        self.assertIn("Shifted Margolus", seq[1])
        self.assertIn("Post-Round 2", seq[2])

    def test_all_candidates_reversibility(self):
        """Verify 100% loss-less reversibility across all candidate architectures and round counts."""
        test_block = ("01" * 64 + "1100" * 32)[:256]
        m0 = block_to_matrix(test_block)

        for cand_name, (fwd_fn, inv_fn, _) in CANDIDATES.items():
            for r in [2, 4, 6, 8, 10, 16]:
                m_r = fwd_fn(m0, r)
                m_rec = inv_fn(m_r, r)
                b_rec = matrix_to_block(m_rec)

                self.assertEqual(
                    b_rec, test_block,
                    f"Reversibility failed for {cand_name} at R={r}"
                )

    def test_healthcare_pipeline_simulation(self):
        """Verify Healthcare Application Pipeline recovery across Candidates A..D at R=2 and R=10."""
        password = "TestMasterPassword2026#"
        plaintext = "PatientID=P999;Age=30;Diagnosis=Healthy;Note=Simulated Pipeline Test"

        for cand_name, (fwd_fn, inv_fn, _) in CANDIDATES.items():
            for r in [2, 10]:
                c_text = simulate_pipeline_encrypt(plaintext, password, fwd_fn, r)
                rec_text = simulate_pipeline_decrypt(c_text, password, inv_fn, r)

                self.assertEqual(
                    rec_text, plaintext,
                    f"Healthcare pipeline recovery failed for {cand_name} at R={r}"
                )

    def test_csv_output(self):
        """Verify CSV results generation and validity of summary dictionary structure."""
        summary, _ = run_step12_validation()

        self.assertGreater(len(summary), 0)
        first_row = summary[0]

        self.assertIn("candidate", first_row)
        self.assertIn("rounds", first_row)
        self.assertIn("bit_avalanche_mean", first_row)
        self.assertTrue(first_row["reversibility_pass"])
        self.assertTrue(first_row["healthcare_recovery_pass"])
        self.assertTrue(os.path.exists("step12_architecture_results.csv"))


if __name__ == "__main__":
    unittest.main()
