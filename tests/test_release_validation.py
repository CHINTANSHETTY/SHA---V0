"""
Phase 4.4 Final Release Validation Tests (`tests/test_release_validation.py`).

Verifies master release audit, security review, checksum integrity, metadata consistency,
and final certification status via `scripts/verify_release.py`.
"""

import json
import os
import pytest

from scripts.verify_release import (
    audit_checksums_and_manifest,
    audit_metadata_consistency,
    audit_release_structure,
    audit_security_and_cleanliness,
    run_full_release_verification,
)

RELEASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "release")


class TestReleaseValidation:
    """Tests for master release verification engine."""

    def test_audit_release_structure(self) -> None:
        """Verify release directory hierarchy audit passes."""
        ok, issues = audit_release_structure()
        assert ok, f"Release structure audit failed with issues: {issues}"
        assert len(issues) == 0

    def test_audit_security_and_cleanliness(self) -> None:
        """Verify security scan finds zero hardcoded secrets or uncollected temp files."""
        ok, issues = audit_security_and_cleanliness()
        assert ok, f"Security & cleanliness audit failed with issues: {issues}"
        assert len(issues) == 0

    def test_audit_checksums_and_manifest(self) -> None:
        """Verify checksum integrity audit passes for release files."""
        ok, issues = audit_checksums_and_manifest()
        assert ok, f"Checksum audit failed with issues: {issues}"
        assert len(issues) == 0

    def test_audit_metadata_consistency(self) -> None:
        """Verify project metadata consistency across README, CHANGELOG, and CITATION.cff."""
        ok, issues = audit_metadata_consistency()
        assert ok, f"Metadata consistency audit failed with issues: {issues}"
        assert len(issues) == 0

    def test_run_full_release_verification(self) -> None:
        """Verify complete release verification workflow and final certification generation."""
        report = run_full_release_verification()

        assert report["overall_status"] == "PASS"
        assert report["certification_passed"] is True
        assert report["total_issues_found"] == 0

        cert_path = os.path.join(RELEASE_DIR, "metadata", "final_release_certification.json")
        assert os.path.exists(cert_path)

        with open(cert_path, "r", encoding="utf-8") as f:
            cert = json.load(f)

        assert cert["certified_project"] == "KDR-CA-AEAD"
        assert cert["version"] == "1.0.0"
        assert cert["verification_passed"] is True
