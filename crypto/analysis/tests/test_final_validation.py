"""
Module:
    test_final_validation.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit and Integration Test Suite for Phase 2.5 Final Experimental Validation & Reproducibility Package.
    Verifies end-to-end pipeline verification, consolidated CSV tables, 300 DPI figures,
    JSON config schema, reproducibility guide, and full validation pipeline.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from crypto.analysis.final_validation import (
    verify_end_to_end_pipeline,
    generate_consolidated_tables,
    generate_publication_figures,
    generate_experiment_configuration,
    generate_reproducibility_markdown,
    generate_final_evaluation_report,
    run_final_validation_pipeline,
)
from crypto.analysis.security_analysis import run_full_security_analysis
from crypto.analysis.benchmark_runner import run_full_benchmark_suite


class TestFinalValidation(unittest.TestCase):
    """Test suite for Phase 2.5 final validation and reproducibility package."""

    def test_verify_end_to_end_pipeline(self) -> None:
        """Verify pipeline correctness, determinism, freshness, and tamper rejection."""
        res = verify_end_to_end_pipeline()
        self.assertTrue(res["end_to_end_correctness"])
        self.assertTrue(res["determinism_verified"])
        self.assertTrue(res["freshness_verified"])
        self.assertTrue(res["tamper_forgery_rejected"])

    def test_generate_consolidated_tables(self) -> None:
        """Verify consolidated CSV tables generation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            sec_res = run_full_security_analysis(tmp_dir)
            bm_res = run_full_benchmark_suite(payload_sizes=[128, 1024], runs=2)
            master_res = {"security": sec_res, "benchmark": bm_res}

            tables = generate_consolidated_tables(master_res, tmp_dir)
            for t_name, t_path in tables.items():
                self.assertTrue(os.path.exists(t_path), f"Missing CSV table: {t_name}")

            with open(tables["master_table"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Shannon_Entropy", content)
                self.assertIn("PASS", content)

    def test_generate_publication_figures(self) -> None:
        """Verify generation of 6 standardized 300 DPI publication figures."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            sec_res = run_full_security_analysis(tmp_dir)
            bm_res = run_full_benchmark_suite(payload_sizes=[128, 1024], runs=2)
            master_res = {"security": sec_res, "benchmark": bm_res}

            figures = generate_publication_figures(master_res, tmp_dir)
            self.assertEqual(len(figures), 6)
            for fig_name, fig_path in figures.items():
                self.assertTrue(os.path.exists(fig_path), f"Missing figure: {fig_name}")

    def test_generate_experiment_configuration(self) -> None:
        """Verify experiment_configuration.json metadata and structure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = os.path.join(tmp_dir, "experiment_configuration.json")
            res_path = generate_experiment_configuration(out_file)
            self.assertTrue(os.path.exists(res_path))

            with open(res_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertIn("system_metadata", data)
                self.assertEqual(data["crypto_parameters"]["key_size_bits"], 256)

    def test_generate_reproducibility_markdown(self) -> None:
        """Verify reproducibility.md generation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = os.path.join(tmp_dir, "reproducibility.md")
            res_path = generate_reproducibility_markdown(out_file)
            self.assertTrue(os.path.exists(res_path))

            with open(res_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Phase 2 IEEE Reproducibility Guide", content)

    def test_run_final_validation_pipeline(self) -> None:
        """Integration test running full final validation pipeline end-to-end."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = run_final_validation_pipeline(tmp_dir)
            self.assertEqual(res["overall_status"], "SUCCESS (Phase 2 Fully Validated & IEEE Package Exported)")
            self.assertTrue(os.path.exists(res["config_json"]))
            self.assertTrue(os.path.exists(res["reproducibility_md"]))
            self.assertTrue(os.path.exists(res["evaluation_report_md"]))

            for t_path in res["tables"].values():
                self.assertTrue(os.path.exists(t_path))

            for f_path in res["figures"].values():
                self.assertTrue(os.path.exists(f_path))


if __name__ == "__main__":
    unittest.main()
