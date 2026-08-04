"""
Module:
    test_advanced_validation.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit Test Suite for Phase 4.1 Advanced Validation Functions & Reporting.
    Verifies input validation for keys, salts, nonces, payloads, packages, CA rule tables,
    HMAC tags, HKDF parameters, and validation summary JSON reporting.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import os
import unittest

from crypto.models.exceptions import CorruptedPayloadError, CryptoError, KeyDerivationError
from crypto.models.package import EncryptedPackage
from crypto.validation.advanced_validation import (
    validate_master_key,
    validate_salt,
    validate_nonce,
    validate_payload_data,
    validate_encrypted_package,
    validate_ca_rule_table,
    validate_hmac_tag,
    validate_hkdf_parameters,
    run_comprehensive_system_validation,
)
from crypto.validation.validation_report import generate_validation_report, ValidationReportBuilder


class TestAdvancedValidation(unittest.TestCase):
    """Test suite for Phase 4.1 Advanced Validation Subsystem."""

    def test_master_key_validation_valid(self):
        """Verify valid master keys (bytes, bytearray, str) are accepted."""
        self.assertEqual(validate_master_key(b"secret_key_256_bits"), b"secret_key_256_bits")
        self.assertEqual(validate_master_key(bytearray(b"secret_key")), b"secret_key")
        self.assertEqual(validate_master_key("SecretPassword123!"), b"SecretPassword123!")

    def test_master_key_validation_invalid(self):
        """Verify invalid master keys raise CryptoError."""
        with self.assertRaises(CryptoError):
            validate_master_key(None)
        with self.assertRaises(CryptoError):
            validate_master_key(b"")
        with self.assertRaises(CryptoError):
            validate_master_key("   ")
        with self.assertRaises(CryptoError):
            validate_master_key(12345)

    def test_salt_and_nonce_validation_valid(self):
        """Verify 16-byte salt and 12-byte nonce are accepted."""
        self.assertEqual(len(validate_salt(b"\x00" * 16)), 16)
        self.assertEqual(len(validate_nonce(b"\x01" * 12)), 12)

    def test_salt_and_nonce_validation_invalid(self):
        """Verify invalid salt and nonce sizes/types raise CryptoError."""
        with self.assertRaises(CryptoError):
            validate_salt(b"\x00" * 8)
        with self.assertRaises(CryptoError):
            validate_salt(None)
        with self.assertRaises(CryptoError):
            validate_nonce(b"\x00" * 16)
        with self.assertRaises(CryptoError):
            validate_nonce(123)

    def test_payload_validation_valid(self):
        """Verify payload data buffers are accepted."""
        self.assertEqual(validate_payload_data(b"payload_bytes"), b"payload_bytes")
        self.assertEqual(validate_payload_data("payload_string"), b"payload_string")

    def test_payload_validation_invalid(self):
        """Verify empty or None payloads raise CryptoError."""
        with self.assertRaises(CryptoError):
            validate_payload_data(None)
        with self.assertRaises(CryptoError):
            validate_payload_data(b"")
        with self.assertRaises(CryptoError):
            validate_payload_data("")

    def test_package_validation_valid(self):
        """Verify valid EncryptedPackage instances are accepted."""
        pkg = EncryptedPackage("1.0.0", b"\x10" * 16, b"\x20" * 12, b"ciphertext", b"\x30" * 32)
        validated = validate_encrypted_package(pkg)
        self.assertEqual(validated.version, "1.0.0")

    def test_package_validation_invalid(self):
        """Verify malformed packages raise CorruptedPayloadError."""
        with self.assertRaises(CorruptedPayloadError):
            validate_encrypted_package(None)
        with self.assertRaises(CorruptedPayloadError):
            validate_encrypted_package("not_a_package")

        bad_salt_pkg = EncryptedPackage("1.0.0", b"\x10" * 8, b"\x20" * 12, b"ciphertext", b"\x30" * 32)
        with self.assertRaises(CryptoError):
            validate_encrypted_package(bad_salt_pkg)

    def test_ca_rule_table_validation_valid(self):
        """Verify valid 256-rule table is accepted."""
        rules = list(range(256))
        self.assertEqual(len(validate_ca_rule_table(rules)), 256)

    def test_ca_rule_table_validation_invalid(self):
        """Verify invalid rule table lengths or values raise CryptoError."""
        with self.assertRaises(CryptoError):
            validate_ca_rule_table(None)
        with self.assertRaises(CryptoError):
            validate_ca_rule_table([1, 2, 3])  # Too short
        with self.assertRaises(CryptoError):
            validate_ca_rule_table([256] * 256)  # Value out of range

    def test_hkdf_parameters_validation(self):
        """Verify HKDF parameters validation and RFC 5869 limits."""
        res = validate_hkdf_parameters(b"ikm_bytes", b"salt", b"info", 32)
        self.assertEqual(res["requested_length"], 32)

        with self.assertRaises(KeyDerivationError):
            validate_hkdf_parameters(b"", b"salt", b"info", 32)
        with self.assertRaises(KeyDerivationError):
            validate_hkdf_parameters(b"ikm", b"salt", b"info", 9000)  # Exceeds max output limit

    def test_validation_report_generator(self):
        """Verify validation report generation and JSON file export."""
        report_path = "reports/test_validation_summary.json"
        rep = generate_validation_report(report_path)
        self.assertEqual(rep["status"], "PASS")
        self.assertTrue(rep["total_checks"] >= 10)
        self.assertTrue(os.path.exists(report_path))
        if os.path.exists(report_path):
            os.remove(report_path)

    def test_run_comprehensive_system_validation(self):
        """Verify comprehensive system validation runner."""
        res = run_comprehensive_system_validation()
        self.assertEqual(res["overall_status"], "PASS")
        self.assertEqual(res["failed"], 0)


if __name__ == "__main__":
    unittest.main()
