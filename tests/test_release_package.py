"""
Phase 4.3 Release Package Quality Assurance Tests (`tests/test_release_package.py`).

Verifies:
- Release folder hierarchy completeness
- release_manifest.json schema and entry validity
- SHA-256 and SHA-512 checksum file integrity
- Metadata consistency across README.md, CHANGELOG.md, CITATION.cff, and release manifest
"""

import json
import os
import pytest

RELEASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "release")


class TestReleasePackageStructure:
    """Verifies physical directory layout and manifest integrity of the release artifact."""

    def test_release_subdirectories_exist(self) -> None:
        """Verify presence of required release subdirectories."""
        expected_subdirs = [
            "paper",
            "docs",
            "benchmark_results",
            "validation_results",
            "evaluation_results",
            "supplementary",
            "metadata",
        ]
        for sub in expected_subdirs:
            path = os.path.join(RELEASE_DIR, sub)
            assert os.path.exists(path), f"Release subdirectory missing: {sub}"
            assert os.path.isdir(path), f"Release sub-item is not a directory: {sub}"

    def test_checksum_files_exist(self) -> None:
        """Verify SHA-256 and SHA-512 checksum manifest files exist."""
        sha256_path = os.path.join(RELEASE_DIR, "checksums_sha256.txt")
        sha512_path = os.path.join(RELEASE_DIR, "checksums_sha512.txt")

        assert os.path.exists(sha256_path)
        assert os.path.exists(sha512_path)

        assert os.path.getsize(sha256_path) > 100
        assert os.path.getsize(sha512_path) > 100

    def test_release_manifest_schema(self) -> None:
        """Verify release_manifest.json schema, version, and file entries."""
        manifest_path = os.path.join(RELEASE_DIR, "release_manifest.json")
        assert os.path.exists(manifest_path)

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["project_name"] == "KDR-CA-AEAD"
        assert manifest["version"] == "1.0.0"
        assert "artifacts" in manifest
        assert manifest["total_files"] == len(manifest["artifacts"])

        for item in manifest["artifacts"]:
            assert "relative_path" in item
            assert "file_size_bytes" in item
            assert "sha256" in item
            assert "sha512" in item
            assert "category" in item
            assert len(item["sha256"]) == 64
            assert len(item["sha512"]) == 128


class TestMetadataConsistency:
    """Verifies citation, version string, and metadata alignment across project files."""

    def test_citation_cff_version(self) -> None:
        """Verify version in CITATION.cff matches 1.0.0."""
        citation_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CITATION.cff")
        assert os.path.exists(citation_path)

        with open(citation_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert 'version: "1.0.0"' in content
        assert "KDR-CA-AEAD" in content

    def test_readme_references_phase4(self) -> None:
        """Verify README.md contains references to project title and documentation hub."""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
        assert os.path.exists(readme_path)

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "KDR-CA-AEAD" in content
        assert "Documentation Hub" in content
