"""
Module:
    test_benchmark_verification.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Unit and Integration Test Suite for Phase 4.3 Performance Benchmark Verification.
    Verifies:
      - Statistical metrics calculation (mean, median, min, max, std dev, throughput)
      - Core cryptographic operation latency measurements
      - Payload scaling benchmarks (1KB to 10MB)
      - Regression detection against baseline values
      - Exported reports in Markdown, JSON, and CSV formats

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

import os
import unittest

from crypto.benchmarking.benchmark_report import generate_benchmark_reports
from crypto.benchmarking.benchmark_verification import (
    OperationBenchmarkResult,
    benchmark_core_operations,
    benchmark_payload_scaling,
    calculate_stats,
    detect_performance_regressions,
    run_full_benchmark_verification,
)


class TestBenchmarkVerification(unittest.TestCase):
    """Test suite for Phase 4.3 Performance Benchmark Verification Subsystem."""

    def test_statistical_calculations(self):
        """Verify statistical metrics calculation (mean, median, std dev, throughput)."""
        times = [10.0, 12.0, 11.0, 9.0, 13.0]
        stats = calculate_stats(times, payload_size_bytes=1024 * 1024)
        self.assertEqual(stats["mean_time_ms"], 11.0)
        self.assertEqual(stats["median_time_ms"], 11.0)
        self.assertEqual(stats["min_time_ms"], 9.0)
        self.assertEqual(stats["max_time_ms"], 13.0)
        self.assertGreater(stats["std_dev_ms"], 0.0)
        self.assertGreater(stats["throughput_mbps"], 0.0)

    def test_benchmark_core_operations(self):
        """Verify core cryptographic operations benchmarking."""
        results = benchmark_core_operations(iterations=5)
        self.assertEqual(len(results), 7)
        op_names = [r.operation_name for r in results]
        self.assertIn("HKDF Key Derivation", op_names)
        self.assertIn("Encryption (Payload)", op_names)
        self.assertIn("Decryption (Payload)", op_names)
        self.assertIn("Authentication Tag Verification", op_names)
        self.assertIn("Nonce Generation (CSPRNG)", op_names)
        self.assertIn("Salt Generation (CSPRNG)", op_names)
        self.assertIn("Full Encrypt-Decrypt Cycle", op_names)

        for res in results:
            self.assertEqual(res.iterations, 5)
            self.assertGreater(res.mean_time_ms, 0.0)

    def test_benchmark_payload_scaling(self):
        """Verify payload size scaling benchmarking (1KB to 10MB)."""
        sizes = [1024, 10240, 102400]
        results = benchmark_payload_scaling(payload_sizes=sizes, iterations=2)
        self.assertEqual(len(results), 3)
        for res in results:
            self.assertIn("encryption_throughput_mbps", res)
            self.assertIn("decryption_throughput_mbps", res)

    def test_detect_performance_regressions(self):
        """Verify performance regression detection against baseline."""
        core_ops = benchmark_core_operations(iterations=5)
        res = detect_performance_regressions(core_ops, threshold_percent=500.0)
        self.assertEqual(res["regressions_detected_count"], 0)
        self.assertEqual(res["regression_status"], "NO_REGRESSION")

    def test_run_full_benchmark_verification(self):
        """Verify full benchmark verification runner execution."""
        res = run_full_benchmark_verification()
        self.assertIn("core_operations_benchmarks", res)
        self.assertIn("payload_scaling_benchmarks", res)
        self.assertIn("regression_analysis", res)

    def test_benchmark_report_generation(self):
        """Verify generation of Markdown, JSON, and CSV benchmark report files."""
        reports_dir = "reports"
        res = generate_benchmark_reports(reports_dir)
        self.assertTrue(os.path.exists(res["json_path"]))
        self.assertTrue(os.path.exists(res["csv_path"]))
        self.assertTrue(os.path.exists(res["markdown_path"]))


if __name__ == "__main__":
    unittest.main()
