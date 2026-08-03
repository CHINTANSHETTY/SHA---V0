"""
Module:
    test_benchmark.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit and Integration Test Suite for Phase 2.4 Performance Benchmarking Subsystem.
    Verifies benchmark utilities, stats calculations, memory tracking, exporter validity,
    visualizations, and pipeline execution.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

from crypto.analysis.benchmark_utils import (
    get_system_metadata,
    compute_statistics,
    PrecisionTimer,
    MemoryTracker,
)
from crypto.analysis.benchmark import (
    benchmark_function,
    run_algorithm_benchmark,
)
from crypto.analysis.benchmark_runner import (
    run_full_benchmark_suite,
    run_benchmark_pipeline,
)
from crypto.analysis.benchmark_export import (
    export_results_to_json,
    export_results_to_csv,
)
from crypto.analysis.visualization import generate_all_benchmark_plots
from crypto.engine.encrypt import encrypt_bytes
from crypto.engine.decrypt import decrypt_bytes


class TestBenchmarkSubsystem(unittest.TestCase):
    """Test suite for Phase 2.4 Benchmarking framework and utilities."""

    def setUp(self) -> None:
        self.master_key = b"Nagamrutha_Test_Bench_Key32B!"
        self.payload = b"Sample EHR telemetry data buffer for unit testing performance metrics" * 4

    def test_get_system_metadata(self) -> None:
        """Verify discovery of hardware, OS, and Python metadata."""
        info = get_system_metadata()
        self.assertIn("os_name", info)
        self.assertIn("python_version", info)
        self.assertGreaterEqual(info["cpu_count"], 1)

    def test_compute_statistics(self) -> None:
        """Verify statistical calculations (mean, std dev, 95% CI, min, max)."""
        data = [10.0, 12.0, 14.0, 16.0, 18.0]
        stats = compute_statistics(data)
        self.assertEqual(stats["mean"], 14.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 18.0)
        self.assertEqual(stats["median"], 14.0)
        self.assertGreater(stats["std_dev"], 0.0)
        self.assertGreater(stats["ci_95_margin"], 0.0)

        # Empty data handling
        empty_stats = compute_statistics([])
        self.assertEqual(empty_stats["mean"], 0.0)

    def test_precision_timer(self) -> None:
        """Verify PrecisionTimer context manager records elapsed time."""
        with PrecisionTimer() as timer:
            _ = sum(i * i for i in range(1000))
        self.assertGreater(timer.elapsed_ms, 0.0)
        self.assertGreater(timer.elapsed_ns, 0)

    def test_memory_tracker(self) -> None:
        """Verify MemoryTracker context manager tracks peak memory allocation."""
        with MemoryTracker() as mem:
            _ = bytearray(100 * 1024)  # Allocate 100 KB
        self.assertGreater(mem.peak_kb, 0.0)

    def test_benchmark_function(self) -> None:
        """Verify benchmark_function timing and memory measurement."""
        def dummy():
            return sum(x for x in range(100))

        res = benchmark_function(dummy, runs=5, warmup_runs=1)
        self.assertIn("mean", res)
        self.assertIn("peak_memory_kb", res)

    def test_run_algorithm_benchmark(self) -> None:
        """Verify algorithm benchmark execution for KDR-CA-AEAD."""
        enc = lambda p: encrypt_bytes(p, self.master_key)
        dec = lambda pkg: decrypt_bytes(pkg, self.master_key)

        res = run_algorithm_benchmark("KDR-CA-AEAD-Test", enc, dec, self.payload, runs=5)
        self.assertEqual(res["algorithm"], "KDR-CA-AEAD-Test")
        self.assertIn("encryption", res)
        self.assertIn("decryption", res)
        self.assertGreater(res["encryption"]["throughput_mb_per_sec"], 0.0)

    def test_run_full_benchmark_suite(self) -> None:
        """Verify benchmark suite runner across subset of payload sizes."""
        sizes = [128, 1024]
        master_res = run_full_benchmark_suite(payload_sizes=sizes, runs=3)
        self.assertIn("ciphers", master_res)
        self.assertIn("kdr_ca_aead", master_res["ciphers"])
        self.assertEqual(len(master_res["ciphers"]["kdr_ca_aead"]), 2)

    def test_export_results_json_and_csv(self) -> None:
        """Verify JSON and CSV export routines."""
        sizes = [128, 1024]
        master_res = run_full_benchmark_suite(payload_sizes=sizes, runs=2)

        with tempfile.TemporaryDirectory() as tmp_dir:
            json_file = os.path.join(tmp_dir, "results.json")
            csv_file = os.path.join(tmp_dir, "results.csv")

            export_results_to_json(master_res, json_file)
            export_results_to_csv(master_res, csv_file)

            self.assertTrue(os.path.exists(json_file))
            self.assertTrue(os.path.exists(csv_file))

            with open(json_file, "r", encoding="utf-8") as f:
                loaded_json = json.load(f)
                self.assertIn("ciphers", loaded_json)

            with open(csv_file, "r", encoding="utf-8") as f:
                csv_content = f.read()
                self.assertIn("Algorithm", csv_content)
                self.assertIn("KDR-CA-AEAD", csv_content)

    def test_benchmark_visualizations(self) -> None:
        """Verify plot generation for all 6 benchmark graphs."""
        sizes = [128, 1024, 10240]
        master_res = run_full_benchmark_suite(payload_sizes=sizes, runs=2)

        with tempfile.TemporaryDirectory() as tmp_dir:
            plots = generate_all_benchmark_plots(tmp_dir, master_res)
            self.assertEqual(len(plots), 6)
            for g_name, g_path in plots.items():
                self.assertTrue(os.path.exists(g_path), f"Missing benchmark plot: {g_name}")

    def test_run_benchmark_pipeline(self) -> None:
        """Integration test executing complete benchmark pipeline end-to-end."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            master_res = run_benchmark_pipeline(tmp_dir)

            self.assertTrue(os.path.exists(master_res["exported_json"]))
            self.assertTrue(os.path.exists(master_res["exported_csv"]))
            self.assertTrue(os.path.exists(master_res["exported_report"]))

            for g_path in master_res["generated_graphs"].values():
                self.assertTrue(os.path.exists(g_path))


if __name__ == "__main__":
    unittest.main()
