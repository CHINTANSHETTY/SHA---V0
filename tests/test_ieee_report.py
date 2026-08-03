"""Unit tests for IEEEReportGenerator (research/report.py)."""

import os
import tempfile
import pytest
from research.report import IEEEReportGenerator


class TestIEEEReportGenerator:
    """Tests for IEEEReportGenerator Markdown, LaTeX, CSV, and JSON generation."""

    def test_generate_markdown_and_latex(self):
        """Verify Markdown and LaTeX manuscript generation."""
        generator = IEEEReportGenerator()
        experiment_data = {
            "benchmark": {
                "metadata": {"algorithm": "KDR-CA-AEAD", "python_version": "3.13.14"},
                "scalability": [
                    {
                        "message_size_bytes": 1024,
                        "throughput_mbps": {"mean": 45.0},
                        "latency_ms": {"mean": 0.5, "confidence_interval_95": (0.48, 0.52)},
                    }
                ],
            },
            "comparison": {
                "kdr": {
                    "cipher_name": "KDR-CA-AEAD",
                    "implementation_type": "Pure Python",
                    "throughput_mbps": 45.0,
                    "latency_ms": 0.5,
                    "avalanche_percent": 50.0,
                    "shannon_entropy": 7.99,
                    "randomness_passed": True,
                }
            },
        }

        md = generator.generate_markdown(experiment_data)
        assert "# KDR-CA-AEAD" in md
        assert "Abstract" in md
        assert "Comparative Evaluation" in md

        tex = generator.generate_latex(experiment_data)
        assert r"\documentclass[conference]{IEEEtran}" in tex
        assert r"\begin{document}" in tex

    def test_export_all_reports(self):
        """Verify export_all_reports creates Markdown, LaTeX, and JSON files."""
        generator = IEEEReportGenerator()
        experiment_data = {"benchmark": {}, "comparison": {}}

        with tempfile.TemporaryDirectory() as tmp_dir:
            res = generator.export_all_reports(experiment_data, tmp_dir)

            assert os.path.exists(res["markdown"])
            assert os.path.exists(res["latex"])
            assert os.path.exists(res["json"])
            assert os.path.getsize(res["markdown"]) > 50
