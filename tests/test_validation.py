"""Unit tests for ValidationRunner and ValidationReport (crypto/validation/)."""

import json
import os
import tempfile
import pytest
from crypto.validation import ValidationReport, ValidationRunner


class TestValidationRunner:
    """Tests for ValidationRunner unified security validation pipeline and report generation."""

    def test_run_full_validation(self):
        """Verify full validation pipeline returns complete security metrics."""
        runner = ValidationRunner()
        res = runner.run_full_validation(trials=10, seed=42)

        assert "reproducibility" in res
        assert "avalanche" in res
        assert "sac" in res
        assert "bic" in res
        assert "entropy" in res
        assert "correlation" in res

        av = res["avalanche"]["key_avalanche"]
        assert av["mean_percent"] > 40.0

        sac = res["sac"]
        assert "mean_sac_probability" in sac or "mean_probability" in sac

        corr = res["correlation"]
        assert "pearson_correlation" in corr
        assert "spearman_correlation" in corr

    def test_export_validation_reports(self):
        """Verify ValidationReport exports Markdown, LaTeX, and JSON files."""
        runner = ValidationRunner()
        data = runner.run_full_validation(trials=5, seed=123)
        reporter = ValidationReport()

        with tempfile.TemporaryDirectory() as tmp_dir:
            reports = reporter.export_all(data, tmp_dir)

            assert os.path.exists(reports["markdown"])
            assert os.path.exists(reports["latex"])
            assert os.path.exists(reports["json"])

            assert os.path.getsize(reports["markdown"]) > 100
            assert os.path.getsize(reports["latex"]) > 100

            with open(reports["json"], "r", encoding="utf-8") as f:
                loaded = json.load(f)
            assert "reproducibility" in loaded
