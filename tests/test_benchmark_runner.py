"""Unit tests for BenchmarkRunner (research/benchmark.py) and LargeScaleBenchmarkRunner (crypto/benchmark/runner.py)."""

import json
import os
import tempfile
import pytest
from crypto.benchmark.benchmark import BenchmarkConfig
from crypto.benchmark.runner import LargeScaleBenchmarkRunner
from research.benchmark import BenchmarkRunner, get_system_metadata


class TestBenchmarkRunner:
    """Tests for BenchmarkRunner encryption, key schedule, and AEAD performance metrics."""

    def test_key_schedule_benchmark(self):
        """Verify key schedule benchmark returns latency and throughput ops/sec."""
        runner = BenchmarkRunner()
        res = runner.benchmark_key_schedule(iterations=10)

        assert res["iterations"] == 10
        assert res["ops_per_sec"] > 0.0
        assert "latency_ms" in res

    def test_encryption_benchmark(self):
        """Verify encryption benchmark computes throughput (MB/s) and latency (ms)."""
        runner = BenchmarkRunner()
        res = runner.benchmark_encryption(message_size=1024, iterations=5)

        assert res["message_size_bytes"] == 1024
        assert res["throughput_mbps"]["mean"] > 0.0
        assert res["latency_ms"]["mean"] > 0.0

    def test_run_and_export(self):
        """Verify full benchmark run and JSON file export."""
        runner = BenchmarkRunner()
        results = runner.run(sizes=[64, 256], iterations=3)

        assert "metadata" in results
        assert "key_schedule" in results
        assert len(results["scalability"]) == 2

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            runner.export_results(tmp_path)
            assert os.path.exists(tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "metadata" in data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_large_scale_benchmark_runner(self):
        """Verify LargeScaleBenchmarkRunner payload scalability execution."""
        config = BenchmarkConfig(sizes=[1024, 10240], iterations=3, warmup_iterations=1, include_comparisons=True)
        runner = LargeScaleBenchmarkRunner(config=config)
        suite = runner.run_suite()

        assert suite.config.sizes == [1024, 10240]
        assert len(suite.results) == 2
        assert "algorithm" in suite.metadata

        res0 = suite.results[0]
        assert res0.message_size_bytes == 1024
        assert res0.encryption_stats["mean"] > 0.0
        assert res0.throughput_mbps_stats["mean"] > 0.0
