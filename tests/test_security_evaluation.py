"""
Module:
    test_security_evaluation.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit and Integration Test Suite for Phase 3.1 Cryptographic Security Evaluation.
    Verifies:
      - Key space cardinality and entropy metrics
      - Classical and post-quantum Grover brute-force security bounds
      - IND-KPA, IND-CPA, IND-CCA2 attack resistance and 100% tamper rejection
      - Replay attack mitigation and CSPRNG 96-bit nonce uniqueness
      - Authentication tag forgery theoretical probability bounds (2^-256)

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import unittest

from crypto.security.evaluation import (
    analyze_key_space,
    evaluate_brute_force_resistance,
    evaluate_tag_forgery_probability,
    run_security_evaluation,
)
from crypto.security.attacks import (
    evaluate_known_plaintext_attack,
    evaluate_chosen_plaintext_attack,
    evaluate_chosen_ciphertext_attack,
    evaluate_replay_attack_resistance,
    evaluate_nonce_uniqueness,
    run_all_attack_evaluations,
)


class TestSecurityEvaluation(unittest.TestCase):
    """Test suite for Phase 3.1 Cryptographic Security Evaluation."""

    def setUp(self):
        self.master_key = b"Nagamrutha_Test_Master_Key_32B!"

    def test_key_space_analysis(self):
        """Verify key length, entropy, search space size, and security margins."""
        res = analyze_key_space(key_size_bits=256)
        self.assertEqual(res["master_key_length_bits"], 256)
        self.assertEqual(res["master_key_length_bytes"], 32)
        self.assertEqual(res["effective_classical_security_bits"], 256)
        self.assertEqual(res["effective_quantum_security_bits"], 128)
        self.assertEqual(res["total_key_entropy_bits"], 256.0)
        self.assertIn("2^256", res["key_space_cardinality"])
        self.assertIn("OPTIMAL", res["compliance_rating"])

    def test_brute_force_resistance(self):
        """Verify classical and Grover quantum brute-force calculations."""
        res = evaluate_brute_force_resistance(key_size_bits=256)
        self.assertEqual(res["key_size_bits"], 256)
        self.assertIn("2^256", res["classical_search_space"])
        self.assertIn("2^128", res["quantum_grover_search_space"])
        self.assertIn("IMPOSSIBLE", res["computational_feasibility"])
        self.assertIn("EXTREMELY INFEASIBLE", res["quantum_feasibility"])

    def test_tag_forgery_probability(self):
        """Verify authentication tag forgery probability metrics."""
        res = evaluate_tag_forgery_probability(tag_length_bits=256)
        self.assertEqual(res["tag_length_bits"], 256)
        self.assertEqual(res["tag_length_bytes"], 32)
        self.assertAlmostEqual(res["single_attempt_forgery_probability_numeric"], 2 ** -256, delta=1e-80)
        self.assertIn("2^-256", res["single_attempt_forgery_probability"])
        self.assertIn("MAXIMUM", res["forgery_resistance_rating"])

    def test_run_security_evaluation(self):
        """Verify security evaluation runner aggregates all sub-evaluations."""
        report = run_security_evaluation()
        self.assertIn("key_space_analysis", report)
        self.assertIn("brute_force_evaluation", report)
        self.assertIn("tag_forgery_evaluation", report)
        self.assertIn("256-bit classical security", report["summary"])

    def test_known_plaintext_attack(self):
        """Verify KPA evaluation detects zero keystream correlation across sessions."""
        res = evaluate_known_plaintext_attack(self.master_key)
        self.assertEqual(res["attack_model"], "Known-Plaintext Attack (KPA)")
        self.assertFalse(res["kpa_forgery_successful"])
        self.assertIn("PASS", res["nonce_isolation"])
        self.assertIn("IMMUNE", res["resistance_rating"])

    def test_chosen_plaintext_attack(self):
        """Verify IND-CPA security against zero, one, and structured plaintexts."""
        res = evaluate_chosen_plaintext_attack(self.master_key)
        self.assertEqual(res["attack_model"], "Chosen-Plaintext Attack (CPA)")
        self.assertTrue(res["ind_cpa_compliant"])
        self.assertFalse(res["structural_leakage_detected"])
        self.assertIn("IND-CPA SECURE", res["resistance_rating"])

    def test_chosen_ciphertext_attack(self):
        """Verify IND-CCA2 compliance and 100% tamper rejection rate."""
        res = evaluate_chosen_ciphertext_attack(self.master_key)
        self.assertEqual(res["attack_model"], "Chosen-Ciphertext Attack (CCA / IND-CCA2)")
        self.assertTrue(res["ind_cca2_compliant"])
        self.assertEqual(res["rejection_rate_percent"], 100.0)
        self.assertIn("IND-CCA2 SECURE", res["resistance_rating"])

    def test_replay_attack_resistance(self):
        """Verify replay attack detection and nonce/salt uniqueness."""
        res = evaluate_replay_attack_resistance(self.master_key)
        self.assertEqual(res["attack_model"], "Replay Attack")
        self.assertTrue(res["distinct_nonces_generated"])
        self.assertTrue(res["distinct_salts_generated"])
        self.assertTrue(res["distinct_ciphertexts_for_identical_plaintext"])
        self.assertTrue(res["modified_replay_rejected"])
        self.assertIn("SECURE", res["resistance_rating"])

    def test_nonce_uniqueness(self):
        """Verify CSPRNG 96-bit nonce generation randomness and collision freedom."""
        res = evaluate_nonce_uniqueness(sample_count=1000)
        self.assertTrue(res["collision_free"])
        self.assertEqual(res["observed_collisions"], 0)
        self.assertIn("OPTIMAL", res["nonce_quality_rating"])

    def test_run_all_attack_evaluations(self):
        """Verify comprehensive attack resistance evaluation runner."""
        report = run_all_attack_evaluations(self.master_key)
        self.assertIn("known_plaintext_attack", report)
        self.assertIn("chosen_plaintext_attack", report)
        self.assertIn("chosen_ciphertext_attack", report)
        self.assertIn("replay_attack", report)
        self.assertIn("nonce_uniqueness", report)
        self.assertIn("total resistance", report["overall_attack_resistance_summary"])


if __name__ == "__main__":
    unittest.main()
