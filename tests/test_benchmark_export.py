"""Unit tests for BenchmarkExporter (crypto/benchmark/exporter.py)."""

import json
import os
import tempfile
import pytest
from crypto.benchmark.benchmark import BenchmarkConfig, BenchmarkResult, BenchmarkSuite
from crypto.benchmark.exporter import BenchmarkExporter


class TestBenchmarkExporter:
    """Tests for BenchmarkExporter CSV, JSON, Markdown, and Metadata file output."""

    def test_export_all_formats(self):
        """Verify export_all generates standardized directory layout and files."""
        config = BenchmarkConfig(sizes=[1024], iterations=3)
        res = BenchmarkResult(
            cipher_name="KDR-CA-AEAD",
            message_size_bytes=1024,
            iterations=3,
            warmup_iterations=1,
            encryption_stats={"mean": 0.5, "median": 0.5, "std_dev": 0.01, "confidence_interval_95": (0.48, 0.52)},
            throughput_mbps_stats={"mean": 25.0},
            memory_stats={"peak_rss_mb": 15.0, "heap_peak_bytes": 10240},
        )
        suite = BenchmarkSuite(config=config, results=[res])

        with tempfile.TemporaryDirectory() as tmp_dir:
            exporter = BenchmarkExporter(base_dir=tmp_dir)
            files = exporter.export_all(suite)

            assert os.path.exists(files["csv"])
            assert os.path.exists(files["json"])
            assert os.path.exists(files["markdown"])
            assert os.path.exists(files["metadata"])

            assert os.path.getsize(files["csv"]) > 20
            assert os.path.getsize(files["json"]) > 50
            assert os.path.getsize(files["markdown"]) > 50

            with open(files["json"], "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "config" in data
            assert len(data["results"]) == 1
