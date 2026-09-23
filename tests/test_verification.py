"""
Module:
    test_verification.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit & Integration Test Suite for Phase 3.2 Formal Security Verification Subsystem.
    Verifies formal proofs and empirical validation of Confidentiality (IND-CPA),
    Integrity (INT-CTXT), Authenticity, Replay Protection, and Forward Secrecy assessment.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import unittest

from crypto.security.verification import (
    verify_confidentiality_properties,
    verify_integrity_properties,
    verify_authenticity_properties,
    verify_replay_protection_properties,
    assess_forward_secrecy,
    run_formal_verification_suite,
)


class TestVerification(unittest.TestCase):
    """Test suite for Phase 3.2 Formal Verification Subsystem."""

    def setUp(self):
        self.master_key = b"Nagamrutha_Verification_Test_Key32!"

    def test_confidentiality_verification(self):
        """Verify IND-CPA confidentiality formal verification."""
        res = verify_confidentiality_properties(self.master_key)
        self.assertEqual(res["property_id"], "FORMAL-PROP-01")
        self.assertTrue(res["distinct_ciphertexts_for_identical_plaintext"])
        self.assertTrue(res["distinct_nonces_generated"])
        self.assertTrue(res["verification_passed"])
        self.assertIn("VERIFIED", res["status"])

    def test_integrity_verification(self):
        """Verify INT-CTXT ciphertext integrity formal verification."""
        res = verify_integrity_properties(self.master_key)
        self.assertEqual(res["property_id"], "FORMAL-PROP-02")
        self.assertEqual(res["rejection_rate_percent"], 100.0)
        self.assertTrue(res["verification_passed"])
        self.assertIn("VERIFIED", res["status"])

    def test_authenticity_verification(self):
        """Verify message origin authenticity and tag unforgeability bound."""
        res = verify_authenticity_properties(self.master_key)
        self.assertEqual(res["property_id"], "FORMAL-PROP-03")
        self.assertTrue(res["wrong_key_authentication_failed"])
        self.assertTrue(res["verification_passed"])
        self.assertIn("2^-256", res["theoretical_forgery_probability"])
        self.assertIn("VERIFIED", res["status"])

    def test_replay_protection_verification(self):
        """Verify replay protection and nonce freshness verification."""
        res = verify_replay_protection_properties(self.master_key)
        self.assertEqual(res["property_id"], "FORMAL-PROP-04")
        self.assertEqual(res["nonce_collisions"], 0)
        self.assertTrue(res["modified_replay_rejected"])
        self.assertTrue(res["verification_passed"])
        self.assertIn("VERIFIED", res["status"])

    def test_forward_secrecy_assessment(self):
        """Verify forward secrecy formal assessment."""
        res = assess_forward_secrecy()
        self.assertEqual(res["property_id"], "FORMAL-PROP-05")
        self.assertFalse(res["forward_secrecy_applicable"])
        self.assertIn("Static Symmetric-Key", res["architecture_type"])
        self.assertIn("ECDHE", res["mitigation_recommendation"])

    def test_full_verification_suite_runner(self):
        """Verify formal verification suite runner aggregates all theorems."""
        report = run_formal_verification_suite()
        self.assertTrue(report["suite_passed"])
        self.assertIn("FORMAL VERIFICATION PASSED", report["overall_verification_summary"])


if __name__ == "__main__":
    unittest.main()
