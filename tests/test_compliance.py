"""
Module:
    test_compliance.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit & Integration Test Suite for Phase 3.3 Security Compliance Subsystem.
    Verifies NIST SP 800-57/90A/38D/131A compliance, OWASP Top 10 A02:2021 checklist,
    RFC 5116 / 2104 / 5869 AEAD requirements, vulnerability risk matrix, and consolidated master compliance matrix.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import unittest

from crypto.security.compliance import (
    verify_nist_compliance,
    verify_owasp_compliance,
    verify_rfc_aead_compliance,
    generate_vulnerability_assessment,
    generate_consolidated_compliance_matrix,
    run_full_compliance_suite,
)


class TestCompliance(unittest.TestCase):
    """Test suite for Phase 3.3 Security Compliance Subsystem."""

    def test_nist_compliance_checker(self):
        """Verify NIST recommendations mapping and status."""
        res = verify_nist_compliance()
        self.assertEqual(res["overall_nist_compliance"], "COMPLIANT")
        self.assertEqual(res["standards_evaluated_count"], 4)
        std_ids = [s["standard_id"] for s in res["standards"]]
        self.assertIn("NIST-SP-800-57", std_ids)
        self.assertIn("NIST-SP-800-90A", std_ids)
        self.assertIn("NIST-SP-800-38D", std_ids)
        self.assertIn("NIST-SP-800-131A", std_ids)

    def test_owasp_compliance_checker(self):
        """Verify OWASP Cryptographic Storage A02:2021 checklist."""
        res = verify_owasp_compliance()
        self.assertEqual(res["overall_owasp_compliance"], "PASS")
        self.assertEqual(res["controls_evaluated_count"], 6)
        for ctrl in res["checklist"]:
            self.assertEqual(ctrl["status"], "PASS")

    def test_rfc_aead_compliance_checker(self):
        """Verify RFC 5116, 2104, and 5869 compliance."""
        res = verify_rfc_aead_compliance()
        self.assertEqual(res["overall_rfc_compliance"], "COMPLIANT")
        self.assertEqual(res["rfcs_evaluated_count"], 3)
        rfcs = [m["rfc"] for m in res["compliance_matrix"]]
        self.assertIn("RFC 5116", rfcs)
        self.assertIn("RFC 2104", rfcs)
        self.assertIn("RFC 5869", rfcs)

    def test_vulnerability_assessment_generator(self):
        """Verify vulnerability assessment risk matrix generation."""
        res = generate_vulnerability_assessment()
        self.assertEqual(res["vulnerabilities_evaluated_count"], 7)
        self.assertIn("LOW RISK", res["overall_risk_rating"])

    def test_consolidated_compliance_matrix(self):
        """Verify master consolidated security compliance matrix generation."""
        res = generate_consolidated_compliance_matrix()
        self.assertTrue(res["rows_count"] >= 7)
        self.assertIn("FULL COMPLIANCE", res["overall_status"])

    def test_full_compliance_suite_runner(self):
        """Verify full security compliance suite runner execution."""
        res = run_full_compliance_suite()
        self.assertTrue(res["suite_passed"])
        self.assertIn("FULL SECURITY COMPLIANCE VERIFIED", res["overall_compliance_summary"])


if __name__ == "__main__":
    unittest.main()
