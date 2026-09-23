"""
Module:
    test_documentation_validation.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit and Integration Test Suite for Phase 4.4 Documentation Review & API Validation.
    Verifies:
      - Public API docstring coverage (functions, classes, docstrings, type hints)
      - Code example snippet execution without errors
      - Markdown documentation structure, parameter consistency, and link integrity
      - Generation of Markdown report (reports/documentation_review_report.md)
        and JSON report (reports/api_validation_report.json)

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import os
import unittest

from crypto.documentation.api_validator import (
    run_api_validation_suite,
    validate_code_examples,
    validate_module_docstrings,
)
from crypto.documentation.documentation_review import (
    generate_documentation_reports,
    review_project_documentation,
)


class TestDocumentationValidation(unittest.TestCase):
    """Test suite for Phase 4.4 Documentation Review & API Validation Subsystem."""

    def test_module_docstring_validation(self):
        """Verify public API docstring coverage and type hints."""
        res = validate_module_docstrings()
        self.assertEqual(res["status"], "PASS")
        self.assertGreaterEqual(res["docstring_coverage_percent"], 90.0)
        self.assertGreater(res["total_symbols_evaluated"], 10)

    def test_code_examples_execution(self):
        """Verify sample code snippet examples execute error-free."""
        res = validate_code_examples()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["examples_count"], 5)
        self.assertEqual(res["examples_passed_count"], 5)

    def test_documentation_review_audit(self):
        """Verify markdown file structural completeness and link integrity."""
        res = review_project_documentation()
        self.assertEqual(res["status"], "PASS")
        self.assertGreaterEqual(res["overall_documentation_quality_score"], 90.0)
        self.assertEqual(res["broken_links_count"], 0)

    def test_run_api_validation_suite(self):
        """Verify full API validation suite runner."""
        res = run_api_validation_suite()
        self.assertEqual(res["overall_api_validation_status"], "PASS")

    def test_generate_documentation_reports(self):
        """Verify generation of Markdown and JSON documentation report files."""
        reports_dir = "reports"
        res = generate_documentation_reports(reports_dir)
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(os.path.exists(res["markdown_path"]))
        self.assertTrue(os.path.exists(res["json_path"]))


if __name__ == "__main__":
    unittest.main()
