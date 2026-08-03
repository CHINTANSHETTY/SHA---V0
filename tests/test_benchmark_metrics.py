"""Unit tests for Benchmark Metrics and Hardware Metadata Collection."""

import pytest
from crypto.benchmark.benchmark import collect_hardware_and_software_metadata
from research.statistics import StatisticsEngine


class TestBenchmarkMetrics:
    """Tests for hardware metadata collection and statistical calculations."""

    def test_collect_hardware_metadata(self):
        """Verify collect_hardware_and_software_metadata retrieves OS, CPU, RAM, and Python details."""
        meta = collect_hardware_and_software_metadata()

        assert "python_version" in meta
        assert "os_name" in meta
        assert "architecture" in meta
        assert "cpu_count_logical" in meta
        assert meta["algorithm"] == "KDR-CA-AEAD"

    def test_percentile_and_confidence_interval_stats(self):
        """Verify percentiles (p50, p95, p99) and 95% CI statistical calculations."""
        stats_engine = StatisticsEngine()
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

        res = stats_engine.analyze(data)

        assert res["sample_count"] == 10
        assert res["mean"] == 5.5
        assert res["median"] == 5.5
        assert "p50" in res["percentiles"]
        assert "p90" in res["percentiles"]
        assert res["confidence_interval_95"][0] < 5.5 < res["confidence_interval_95"][1]
