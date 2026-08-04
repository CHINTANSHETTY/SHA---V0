"""
Module:
    test_security_audit.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit and Integration Test Suite for Phase 4.2 Security Audit Subsystem.
    Verifies:
      - Static security code scanning (hardcoded secrets, CSPRNG usage, unsafe functions)
      - Cryptographic primitive compliance (HKDF RFC 5869, HMAC RFC 2104, parameter sizes)
      - Threat mitigation audits (Replay, CCA, Brute-Force, Timing attacks)
      - 8-domain Security Checklist scoring
      - Invalid authentication tags, modified ciphertext, invalid nonces/keys, tampered metadata
      - Audit report generation (reports/security_audit_report.md & reports/security_findings.json)

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import os
import unittest

from crypto.engine.decrypt import decrypt_bytes
from crypto.engine.encrypt import encrypt_bytes
from crypto.models.exceptions import AuthenticationError, CorruptedPayloadError, CryptoError
from crypto.models.package import EncryptedPackage
from crypto.security.audit_report import generate_audit_report
from crypto.security.security_audit import (
    audit_cryptographic_primitives,
    audit_security_checklist,
    audit_static_code_security,
    audit_threat_mitigations,
    run_full_security_audit,
)


class TestSecurityAudit(unittest.TestCase):
    """Test suite for Phase 4.2 Security Audit Subsystem."""

    def setUp(self):
        self.master_key = b"Nagamrutha_SecurityAudit_TestKey32"

    def test_static_code_security_audit(self):
        """Verify static security code scanner executes cleanly."""
        res = audit_static_code_security()
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(res["checks_count"] >= 3)
        for check in res["checks"]:
            self.assertTrue(check["passed"])

    def test_cryptographic_primitives_audit(self):
        """Verify cryptographic primitive review (HKDF, HMAC, sizes, order)."""
        res = audit_cryptographic_primitives()
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(res["primitives_reviewed_count"] >= 4)
        for review in res["reviews"]:
            self.assertTrue(review["passed"])

    def test_threat_mitigations_audit(self):
        """Verify threat mitigation audit asserts all 5 threat categories mitigated."""
        res = audit_threat_mitigations()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["threats_evaluated_count"], 5)
        for threat in res["threats"]:
            self.assertTrue(threat["mitigated"])

    def test_security_checklist_audit(self):
        """Verify 8-domain security checklist scoring."""
        res = audit_security_checklist()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["categories_evaluated_count"], 8)
        self.assertGreaterEqual(res["overall_checklist_score"], 95.0)

    def test_tampered_metadata_and_invalid_lengths(self):
        """Verify security defenses against invalid tags, modified ciphertext, invalid nonces, invalid key lengths, corrupted packages, and tampered metadata."""
        pkg = encrypt_bytes(b"Secret payload for audit test", self.master_key)

        # 1. Invalid authentication tag
        bad_tag_pkg = EncryptedPackage(pkg.version, pkg.salt, pkg.nonce, pkg.ciphertext, b"\xFF" * 32)
        with self.assertRaises(AuthenticationError):
            decrypt_bytes(bad_tag_pkg, self.master_key)

        # 2. Modified ciphertext bit
        mod_ct = bytes([pkg.ciphertext[0] ^ 0x01]) + pkg.ciphertext[1:]
        mod_ct_pkg = EncryptedPackage(pkg.version, pkg.salt, pkg.nonce, mod_ct, pkg.tag)
        with self.assertRaises(AuthenticationError):
            decrypt_bytes(mod_ct_pkg, self.master_key)

        # 3. Invalid key length (empty key)
        with self.assertRaises(CryptoError):
            encrypt_bytes(b"data", b"")

        # 4. Tampered salt/nonce metadata
        mod_salt_pkg = EncryptedPackage(pkg.version, bytes([pkg.salt[0] ^ 0xFF]) + pkg.salt[1:], pkg.nonce, pkg.ciphertext, pkg.tag)
        with self.assertRaises(AuthenticationError):
            decrypt_bytes(mod_salt_pkg, self.master_key)

        # 5. Tampered version string deserialization
        with self.assertRaises(CorruptedPayloadError):
            EncryptedPackage.from_dict({"version": "1.0.0"})  # Missing required fields

    def test_full_security_audit_runner(self):
        """Verify full security audit runner aggregates all phases."""
        res = run_full_security_audit()
        self.assertEqual(res["overall_audit_status"], "PASS")
        self.assertGreaterEqual(res["overall_security_score"], 95.0)
        self.assertIn("SECURITY AUDIT PASSED", res["summary"])

    def test_audit_report_generation(self):
        """Verify audit report generation outputs markdown and JSON artifacts."""
        reports_dir = "reports"
        res = generate_audit_report(reports_dir)
        self.assertGreaterEqual(res["overall_security_score"], 95.0)
        self.assertEqual(res["overall_audit_status"], "PASS")

        json_path = res["json_findings_path"]
        md_path = res["markdown_report_path"]

        self.assertTrue(os.path.exists(json_path))
        self.assertTrue(os.path.exists(md_path))


if __name__ == "__main__":
    unittest.main()
