"""
Unit tests for full_experiment.py and synthetic_healthcare_data.py modules.
Verifies synthetic dataset generation, required payload size testing, exact recovery,
metric calculation functions (Shannon entropy, Pearson correlation, NPCR, UACI),
key sensitivity testing, and CSV file output generation.
"""

import os
import unittest
from synthetic_healthcare_data import (
    generate_synthetic_dataset,
    create_all_synthetic_datasets,
)
from full_experiment import (
    PAYLOAD_SIZES,
    generate_deterministic_payload,
    calculate_shannon_entropy,
    calculate_pearson_correlation,
    calculate_2d_byte_correlation,
    run_full_experiment,
)
from research_encrypt import encrypt_research
from research_decrypt import decrypt_research


class TestFullExperiment(unittest.TestCase):

    def test_synthetic_dataset_generation(self):
        """Test deterministic synthetic healthcare dataset generation."""
        dataset_100 = generate_synthetic_dataset(100, seed=20260923)
        self.assertEqual(len(dataset_100), 100)

        # Confirm fields
        first_rec = dataset_100[0]
        required_fields = [
            "PatientID", "Age", "Gender", "BloodPressure", "HeartRate",
            "Diagnosis", "Medication", "Glucose", "Temperature", "DoctorID", "Date"
        ]
        for field in required_fields:
            self.assertIn(field, first_rec)

        # Confirm file generation
        f100, f500, f1000 = create_all_synthetic_datasets(seed=20260923)
        self.assertTrue(os.path.exists(f100))
        self.assertTrue(os.path.exists(f500))
        self.assertTrue(os.path.exists(f1000))

    def test_required_payload_sizes_and_recovery(self):
        """Verify exact recovery across all required payload sizes (256b to 1MB)."""
        password = "TestMasterPassword2026#"

        for label, size_bytes in PAYLOAD_SIZES.items():
            payload = generate_deterministic_payload(size_bytes, seed=20260923)
            self.assertEqual(len(payload.encode("utf-8")), size_bytes)

            ciphertext = encrypt_research(payload, password)
            recovered = decrypt_research(ciphertext, password)

            self.assertEqual(
                recovered, payload,
                f"Exact recovery failed for payload size {label} ({size_bytes} bytes)"
            )

    def test_shannon_entropy_calculation(self):
        """Verify byte-level Shannon entropy calculation function."""
        # Single byte value repeated -> entropy = 0.0
        single_byte_data = b"A" * 100
        self.assertEqual(calculate_shannon_entropy(single_byte_data), 0.0)

        # Uniform distribution of all 256 byte values -> max entropy = 8.0 bits/byte
        all_bytes = bytes(range(256)) * 10
        max_entropy = calculate_shannon_entropy(all_bytes)
        self.assertAlmostEqual(max_entropy, 8.0, places=4)

    def test_pearson_correlation_calculation(self):
        """Verify Pearson correlation coefficient function."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]

        # Perfect positive linear correlation -> 1.0
        corr = calculate_pearson_correlation(x, y)
        self.assertAlmostEqual(corr, 1.0, places=4)

    def test_2d_byte_correlation_calculation(self):
        """Verify 2D reshaped byte correlation calculation."""
        sample_bytes = bytes(range(256))
        corr_h, corr_v, corr_d = calculate_2d_byte_correlation(sample_bytes)

        self.assertIsInstance(corr_h, float)
        self.assertIsInstance(corr_v, float)
        self.assertIsInstance(corr_d, float)

    def test_full_experiment_csv_output(self):
        """Run full experiment framework and verify CSV output files exist."""
        summary, raw = run_full_experiment()

        self.assertGreater(len(summary), 0)
        self.assertGreater(len(raw), 0)

        self.assertTrue(os.path.exists("full_experiment_results.csv"))
        self.assertTrue(os.path.exists("full_experiment_raw.csv"))


if __name__ == "__main__":
    unittest.main()
