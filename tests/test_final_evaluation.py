"""
Phase 4.2 Comprehensive Evaluation Tests (`tests/test_final_evaluation.py`).

Verifies FrameworkEvaluator, PerformanceConsolidator, compute_statistics,
comparative algorithm wrappers, reliability stress testing, and memory leak checks.
"""

import pytest
from crypto.evaluation import (
    FrameworkEvaluator,
    PerformanceConsolidator,
    compute_statistics,
)


class TestPerformanceConsolidator:
    """Tests for compute_statistics and PerformanceConsolidator."""

    def test_compute_statistics_empty_and_single(self) -> None:
        """Verify compute_statistics on empty and single element inputs."""
        empty_stats = compute_statistics([])
        assert empty_stats["count"] == 0
        assert empty_stats["mean"] == 0.0

        single_stats = compute_statistics([42.0])
        assert single_stats["count"] == 1.0
        assert single_stats["mean"] == 42.0
        assert single_stats["min"] == 42.0
        assert single_stats["max"] == 42.0
        assert single_stats["std_dev"] == 0.0

    def test_compute_statistics_t_distribution_vs_z(self) -> None:
        """Verify Student t-distribution (<30) vs Normal Z (>=30) CI computation."""
        small_samples = [10.0, 12.0, 11.0, 13.0, 10.5]
        stats_small = compute_statistics(small_samples)

        assert stats_small["count"] == 5.0
        assert stats_small["mean"] == 11.3
        assert stats_small["ci_95_margin"] > 0.0

        large_samples = [10.0 + (i * 0.1) for i in range(35)]
        stats_large = compute_statistics(large_samples)

        assert stats_large["count"] == 35.0
        assert stats_large["ci_95_margin"] > 0.0

    def test_consolidate_algorithm_runs(self) -> None:
        """Verify consolidation of encryption/decryption execution runs."""
        enc_times = [1.2, 1.3, 1.1, 1.25, 1.15]
        dec_times = [0.8, 0.85, 0.79, 0.82, 0.81]
        payload_size = 1048576  # 1 MB

        summary = PerformanceConsolidator.consolidate_algorithm_runs(
            enc_times, dec_times, payload_size, peak_memory_bytes=204800
        )

        assert summary["payload_size_bytes"] == payload_size
        assert summary["payload_size_mb"] == 1.0
        assert summary["peak_memory_kb"] == 200.0
        assert "encryption" in summary
        assert "decryption" in summary
        assert summary["encryption"]["throughput_mb_s"]["mean"] > 0.0


class TestFrameworkEvaluator:
    """Tests for FrameworkEvaluator execution routines."""

    def test_evaluator_final_benchmarks_quick(self) -> None:
        """Verify FrameworkEvaluator runs final benchmarks for specified payload sizes."""
        evaluator = FrameworkEvaluator()
        res = evaluator.run_final_benchmarks(payload_sizes=[1024, 10240], runs=3)

        assert "kdr_ca_aead" in res
        assert len(res["kdr_ca_aead"]) == 2
        assert res["kdr_ca_aead"][0]["payload_size_bytes"] == 1024

    def test_evaluator_comparative_analysis(self) -> None:
        """Verify comparative analysis against baseline ciphers."""
        evaluator = FrameworkEvaluator()
        comp = evaluator.run_comparative_analysis(payload_sizes=[10240], runs=3)

        assert "AES-128-GCM" in comp
        assert "ChaCha20-Poly1305" in comp
        assert "AES-CTR+HMAC-SHA256" in comp

    def test_evaluator_reliability_evaluation(self) -> None:
        """Verify reliability stress test and memory leak check."""
        evaluator = FrameworkEvaluator()
        rel = evaluator.run_reliability_evaluation(iterations=20)

        assert rel["total_iterations"] == 20
        assert rel["failed_iterations"] == 0
        assert rel["success_rate_percent"] == 100.0
        assert rel["memory_leak_detected"] is False

    def test_comprehensive_evaluation_pipeline(self) -> None:
        """Verify full evaluation pipeline in quick test mode."""
        evaluator = FrameworkEvaluator()
        data = evaluator.run_comprehensive_evaluation(quick=True)

        assert "reproducibility" in data
        assert "benchmarks" in data
        assert "security_validation" in data
        assert "comparative_analysis" in data
        assert "reliability_evaluation" in data
