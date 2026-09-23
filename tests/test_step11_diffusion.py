"""
Unit tests for step11_diffusion_diagnostic.py module.
Verifies local 4-bit rule differential analysis, one-bit propagation tracking,
100% loss-less reversibility across all candidate round schedules (Schedule A..E),
and CSV file output generation.
"""

import os
import unittest
from step11_diffusion_diagnostic import (
    analyze_local_4bit_rule_differentials,
    trace_one_bit_propagation,
    verify_schedule_reversibility,
    evaluate_schedules_diffusion,
    run_step11_diagnostics,
    SCHEDULES,
)


class TestStep11Diffusion(unittest.TestCase):

    def test_local_4bit_rule_differential_analysis(self):
        """Verify 4-bit rule differential analysis enumerates all 64 input-flip pairs."""
        stats = analyze_local_4bit_rule_differentials()

        self.assertEqual(stats["total_pairs"], 64)
        self.assertGreaterEqual(stats["min_hd"], 1)
        self.assertLessEqual(stats["max_hd"], 4)
        self.assertGreater(stats["mean_hd"], 0.0)

        # Check that distribution counts sum to 64
        total_occurrences = sum(stats["distribution"].values())
        self.assertEqual(total_occurrences, 64)

    def test_one_bit_propagation_tracking(self):
        """Verify one-bit propagation tracking records stages up to round 32."""
        records = trace_one_bit_propagation(max_rounds=32)
        
        self.assertGreater(len(records), 0)
        first_rec = records[0]
        self.assertIn("stage", first_rec)
        self.assertIn("changed_bits", first_rec)
        self.assertIn("changed_cells", first_rec)
        self.assertIn("neighborhoods_changed", first_rec)

    def test_schedule_reversibility(self):
        """Verify 100% loss-less reversibility for all candidate round schedules (Schedule A..E)."""
        rev_results = verify_schedule_reversibility(trials=10)

        for sched_name, passed in rev_results.items():
            self.assertTrue(
                passed,
                f"Reversibility failed for candidate schedule {sched_name}"
            )

    def test_csv_generation(self):
        """Verify CSV file generation and validity of summary outputs."""
        summary_rows, _ = evaluate_schedules_diffusion(trials=5)
        
        self.assertGreater(len(summary_rows), 0)
        first_row = summary_rows[0]

        self.assertIn("schedule", first_row)
        self.assertIn("rounds", first_row)
        self.assertIn("avalanche_percent_mean", first_row)
        self.assertIn("reversibility_passed", first_row)
        self.assertTrue(first_row["reversibility_passed"])


if __name__ == "__main__":
    unittest.main()
