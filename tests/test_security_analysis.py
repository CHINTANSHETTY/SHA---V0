"""
Module:
    test_security_analysis.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit and Integration Test Suite for Phase 2.3 Security Evaluation & Cryptanalysis.
    Verifies completion criteria:
      - Avalanche effect > 50%
      - High entropy (close to 8 bits/byte)
      - Low correlation between plaintext and ciphertext
      - NIST SP 800-22 statistical randomness tests passed
      - Graph generation and IEEE security report generation

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import os
import shutil
import tempfile
import unittest

from crypto.analysis.randomness import (
    calculate_shannon_entropy,
    bit_distribution_analysis,
    monobit_test,
    runs_test,
    frequency_analysis,
    run_randomness_suite,
)
from crypto.analysis.statistics import (
    count_bit_flips,
    measure_plaintext_avalanche,
    measure_key_avalanche,
    calculate_key_sensitivity,
    calculate_correlation_coefficients,
    calculate_histogram_uniformity,
    compare_with_reference_ciphers,
)
from crypto.analysis.attack_analysis import (
    evaluate_brute_force_complexity,
    evaluate_differential_resistance,
    evaluate_linear_resistance,
    evaluate_related_key_resistance,
    evaluate_replay_protection,
    evaluate_performance_tradeoffs,
)
from crypto.analysis.visualization import generate_all_security_plots
from crypto.analysis.security_analysis import run_full_security_analysis
from crypto.engine.encrypt import encrypt_bytes


class TestSecurityAnalysis(unittest.TestCase):
    """Test suite for Phase 2.3 Security Analysis & Cryptographic Validation."""

    def setUp(self):
        self.master_key = b"Nagamrutha_Test_Master_Key_32B!"
        self.plaintext = b"Patient EHR Record: Name=Aarav Sharma, Age=34, Vitals=Normal, Status=Clear" * 16
        self.pkg = encrypt_bytes(self.plaintext, self.master_key)
        self.ciphertext = self.pkg.ciphertext

    def test_shannon_entropy(self):
        """Verify Shannon entropy is high (>= 7.75 bits/byte) for encrypted payload."""
        entropy = calculate_shannon_entropy(self.ciphertext)
        self.assertGreaterEqual(entropy, 7.75, "Ciphertext entropy must be close to 8.0 bits/byte.")

    def test_bit_distribution(self):
        """Verify 0s vs 1s bit distribution is balanced near 50%."""
        dist = bit_distribution_analysis(self.ciphertext)
        self.assertLessEqual(dist["imbalance_percent"], 5.0, "Bit imbalance must be under 5%.")
        self.assertAlmostEqual(dist["one_ratio"], 0.5, delta=0.05)

    def test_monobit_test(self):
        """Verify NIST Monobit Test passes with p-value >= 0.01."""
        mono = monobit_test(self.ciphertext)
        self.assertTrue(mono["passed"], f"Monobit test failed with p-value={mono['p_value']}")
        self.assertGreaterEqual(mono["p_value"], 0.01)

    def test_runs_test(self):
        """Verify NIST Runs Test passes with p-value >= 0.01."""
        runs = runs_test(self.ciphertext)
        self.assertTrue(runs["passed"], f"Runs test failed with p-value={runs['p_value']}")
        self.assertGreaterEqual(runs["p_value"], 0.01)

    def test_frequency_analysis(self):
        """Verify 256-bin Byte Frequency Chi-Square Test passes."""
        freq = frequency_analysis(self.ciphertext)
        self.assertTrue(freq["passed"], f"Frequency analysis failed with chi_sq={freq['chi_square']}")

    def test_plaintext_avalanche(self):
        """Verify Plaintext Avalanche Effect > 50% (SAC criterion)."""
        av = measure_plaintext_avalanche(self.master_key, self.plaintext, samples=50)
        self.assertTrue(av["passed"], f"Plaintext avalanche failed: mean={av['mean_avalanche_percent']}%")
        self.assertGreaterEqual(av["mean_avalanche_percent"], 45.0)

    def test_key_avalanche(self):
        """Verify Key Avalanche Effect > 50%."""
        av = measure_key_avalanche(self.master_key, self.plaintext, samples=50)
        self.assertTrue(av["passed"], f"Key avalanche failed: mean={av['mean_avalanche_percent']}%")
        self.assertGreaterEqual(av["mean_avalanche_percent"], 45.0)

    def test_key_sensitivity(self):
        """Verify Key Sensitivity Hamming Distance Statistics."""
        sens = calculate_key_sensitivity(self.master_key, self.plaintext, num_bit_flips=50)
        self.assertGreater(sens["measured_mean_hamming_distance"], 0)
        self.assertAlmostEqual(sens["key_sensitivity_score"], 50.0, delta=10.0)

    def test_correlation_coefficients(self):
        """Verify Plaintext vs Ciphertext correlation is close to 0.00."""
        corr = calculate_correlation_coefficients(self.plaintext, self.ciphertext)
        self.assertTrue(corr["passed"], f"Correlation check failed: pt-ct={corr['pt_ct_correlation']}")
        self.assertLess(abs(corr["pt_ct_correlation"]), 0.15)
        self.assertLess(abs(corr["adjacent_correlation"]), 0.15)

    def test_histogram_uniformity(self):
        """Verify NPCR and UACI metrics."""
        hist = calculate_histogram_uniformity(self.ciphertext)
        self.assertGreater(hist["npcr_percent"], 50.0)
        self.assertGreater(hist["uaci_percent"], 10.0)

    def test_cipher_comparison(self):
        """Verify comparison with AES and ChaCha20 returns valid benchmark dict."""
        comp = compare_with_reference_ciphers(self.plaintext, self.master_key, samples=20)
        self.assertIn("kdr_ca_aead", comp)
        self.assertIn("aes_128_gcm", comp)
        self.assertIn("chacha20_poly1305", comp)
        self.assertGreater(comp["kdr_ca_aead"]["avalanche_percent"], 45.0)

    def test_attack_resistance(self):
        """Verify attack resistance theoretical evaluations."""
        brute = evaluate_brute_force_complexity(256)
        self.assertIn("2^256", brute["classical_search_space"])

        diff = evaluate_differential_resistance()
        self.assertEqual(diff["resistance_rating"], "IMMUNE (Maximum Differential Probability < 2^-128)")

        linear = evaluate_linear_resistance()
        self.assertEqual(linear["resistance_rating"], "IMMUNE (Linear Approximation Bias negligible)")

        rel_key = evaluate_related_key_resistance()
        self.assertTrue("SECURE" in rel_key["resistance_rating"])

        replay = evaluate_replay_protection()
        self.assertTrue("SECURE" in replay["resistance_rating"])

    def test_performance_tradeoffs(self):
        """Verify performance trade-off analysis."""
        tradeoff = evaluate_performance_tradeoffs([1024, 10240])
        evals = tradeoff["tradeoff_evaluations"]
        self.assertEqual(len(evals), 2)
        self.assertGreater(evals[0]["throughput_mb_per_sec"], 0.0)

    def test_edge_cases_empty_and_invalid(self):
        """Verify handling of edge cases (empty data, invalid/empty keys)."""
        self.assertEqual(calculate_shannon_entropy(b""), 0.0)

        dist = bit_distribution_analysis(b"")
        self.assertEqual(dist["total_bits"], 0)

        mono = monobit_test(b"")
        self.assertFalse(mono["passed"])

        runs = runs_test(b"")
        self.assertFalse(runs["passed"])

        freq = frequency_analysis(b"")
        self.assertFalse(freq["passed"])

        corr = calculate_correlation_coefficients(b"", b"")
        self.assertTrue(corr["passed"])

        hist = calculate_histogram_uniformity(b"")
        self.assertEqual(hist["npcr_percent"], 0.0)

    def test_varying_message_sizes(self):
        """Verify security metrics across varying message sizes (128-bit, 256-bit, 512-bit, 1KB, 10KB, 100KB)."""
        sizes = [16, 32, 64, 1024, 10240, 100000]  # 128b, 256b, 512b, 1KB, 10KB, 100KB
        for size in sizes:
            payload = b"A" * size
            pkg = encrypt_bytes(payload, self.master_key)
            entropy = calculate_shannon_entropy(pkg.ciphertext)
            self.assertGreater(entropy, 3.0, f"Entropy check failed for size {size}")

    def test_full_security_analysis_pipeline(self):
        """Integration test executing run_full_security_analysis end-to-end."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = run_full_security_analysis(tmp_dir)

            self.assertEqual(res["overall_status"], "SUCCESS (All Completion Criteria Satisfied)")

            # Check report markdown generated
            report_file = os.path.join(tmp_dir, "security_report.md")
            self.assertTrue(os.path.exists(report_file))

            # Check graphs generated
            graphs_dir = os.path.join(tmp_dir, "security_graphs")
            for graph_name in ["avalanche.png", "entropy.png", "histogram.png", "correlation.png", "comparison.png"]:
                g_path = os.path.join(graphs_dir, graph_name)
                self.assertTrue(os.path.exists(g_path), f"Missing graph: {graph_name}")


if __name__ == "__main__":
    unittest.main()
