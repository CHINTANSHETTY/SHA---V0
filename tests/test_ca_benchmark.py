"""Unit tests for CA Benchmark Framework (crypto/ca/benchmark.py)."""

import json
import pytest
from crypto.ca.benchmark import BenchmarkMetadata, BenchmarkResult, CABenchmark


class TestCABenchmark:
    """Tests for CABenchmark suite."""

    def test_benchmark_single_rule(self):
        """Verify single rule benchmark returns valid timing and memory metrics."""
        bm = CABenchmark()
        res = bm.benchmark_rule(rule_id=30, state_size=100, generations=10, engine_type="optimized")

        assert isinstance(res, BenchmarkResult)
        assert res.rule_id == 30
        assert res.state_size == 100
        assert res.generations == 10
        assert res.execution_time_seconds > 0
        assert res.throughput_ops_per_sec > 0
        assert isinstance(res.metadata, BenchmarkMetadata)
        assert res.metadata.python_version != ""

    def test_run_benchmark_suite(self):
        """Verify running suite across multiple rules and state sizes."""
        bm = CABenchmark()
        results = bm.run_benchmark(rules=[30, 90], state_sizes=[50, 100], generations=5, engine_types=["optimized"])

        assert len(results) == 4
        for r in results:
            assert r.generations == 5

    def test_generate_reports(self):
        """Verify markdown and JSON report generation."""
        bm = CABenchmark()
        results = bm.run_benchmark(rules=[30], state_sizes=[50], generations=5, engine_types=["optimized"])

        md_report = bm.generate_report(results, format="markdown")
        assert "# Cellular Automata Performance Benchmark Report" in md_report
        assert "System Metadata" in md_report
        assert "| 30 |" in md_report

        json_report = bm.generate_report(results, format="json")
        parsed = json.loads(json_report)
        assert isinstance(parsed, list)
        assert parsed[0]["state_size"] == 50
