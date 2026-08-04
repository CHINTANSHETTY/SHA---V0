"""
Phase 4.2 Evaluation Reports Tests (`tests/test_evaluation_reports.py`).

Verifies ReportGenerator, directory structure creation, Markdown generation,
IEEE double-column LaTeX table formatting, CSV/JSON file exports, and reproducibility manifest.
"""

import json
import os
import tempfile
import pytest

from crypto.evaluation import FrameworkEvaluator, ReportGenerator


class TestReportGenerator:
    """Tests for ReportGenerator output hierarchy and multi-format report exports."""

    def test_report_generator_directory_structure(self) -> None:
        """Verify structured output directory creation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_base = os.path.join(tmp_dir, "eval_results")
            reporter = ReportGenerator(base_output_dir=out_base)

            for key, path in reporter.subdirs.items():
                assert os.path.exists(path), f"Subdirectory for '{key}' does not exist: {path}"

    def test_export_all_reports(self) -> None:
        """Verify export of Markdown, LaTeX, JSON, CSV, and metadata files."""
        evaluator = FrameworkEvaluator()
        eval_data = evaluator.run_comprehensive_evaluation(quick=True)

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_base = os.path.join(tmp_dir, "eval_results")
            reporter = ReportGenerator(base_output_dir=out_base)

            exports = reporter.export_all_reports(eval_data)

            assert os.path.exists(exports["markdown_report"])
            assert os.path.exists(exports["latex_table"])
            assert os.path.exists(exports["json_summary"])
            assert os.path.exists(exports["csv_metrics"])
            assert os.path.exists(exports["reproducibility_manifest"])

            # Check content sizes
            assert os.path.getsize(exports["markdown_report"]) > 100
            assert os.path.getsize(exports["latex_table"]) > 50

            # Verify JSON structure
            with open(exports["json_summary"], "r", encoding="utf-8") as f:
                loaded = json.load(f)
            assert "reproducibility" in loaded
            assert "benchmarks" in loaded

            # Verify LaTeX table syntax
            with open(exports["latex_table"], "r", encoding="utf-8") as f:
                tex_code = f.read()
            assert r"\begin{table*}" in tex_code
            assert r"\end{table*}" in tex_code
