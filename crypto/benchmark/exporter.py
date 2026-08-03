"""Benchmark Exporter Subsystem (`crypto.benchmark.exporter`).

Provides `BenchmarkExporter` for exporting benchmark suite results into publication-ready
CSV files, JSON documents, Markdown tables, and environment metadata files.
"""

import csv
import json
import os
from typing import Any, Dict, List, Optional

from crypto.benchmark.benchmark import BenchmarkSuite


class BenchmarkExporter:
    """Benchmark Results Exporter for CSV, JSON, Markdown, and Metadata formats."""

    def __init__(self, base_dir: str = "benchmark_results") -> None:
        """Initialize BenchmarkExporter and ensure standardized directory structure.

        Directory Layout:
            benchmark_results/
                csv/
                json/
                markdown/
                metadata/
        """
        self.base_dir: str = base_dir
        self.csv_dir: str = os.path.join(base_dir, "csv")
        self.json_dir: str = os.path.join(base_dir, "json")
        self.md_dir: str = os.path.join(base_dir, "markdown")
        self.meta_dir: str = os.path.join(base_dir, "metadata")

        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.md_dir, exist_ok=True)
        os.makedirs(self.meta_dir, exist_ok=True)

    def export_all(self, suite: BenchmarkSuite) -> Dict[str, str]:
        """Export all benchmark outputs to target directories.

        Args:
            suite: BenchmarkSuite object.

        Returns:
            Dict[str, str]: Map of format names to absolute exported file paths.
        """
        csv_file = os.path.join(self.csv_dir, "benchmark_scalability.csv")
        json_file = os.path.join(self.json_dir, "benchmark_suite_full.json")
        md_file = os.path.join(self.md_dir, "benchmark_tables.md")
        meta_file = os.path.join(self.meta_dir, "environment_metadata.json")

        self.export_csv(suite, csv_file)
        self.export_json(suite, json_file)
        self.export_markdown(suite, md_file)
        self.export_metadata(suite.metadata, meta_file)

        return {
            "csv": csv_file,
            "json": json_file,
            "markdown": md_file,
            "metadata": meta_file,
        }

    def export_csv(self, suite: BenchmarkSuite, filepath: str) -> str:
        """Export scalability benchmark results to CSV format.

        Args:
            suite: BenchmarkSuite object.
            filepath: Target file path.

        Returns:
            str: Destination file path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        suite_dict = suite.to_dict()
        results = suite_dict.get("results", [])

        fieldnames = [
            "cipher_name",
            "message_size_bytes",
            "iterations",
            "warmup_iterations",
            "enc_latency_mean_ms",
            "enc_latency_median_ms",
            "enc_latency_std_dev_ms",
            "enc_latency_ci95_low",
            "enc_latency_ci95_high",
            "throughput_mean_mbps",
            "peak_rss_mb",
            "heap_peak_bytes",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                enc = r.get("encryption_latency", {})
                tp = r.get("throughput_mbps", {})
                mem = r.get("memory", {})
                ci = enc.get("confidence_interval_95", (0.0, 0.0))

                writer.writerow(
                    {
                        "cipher_name": r.get("cipher_name", "KDR-CA-AEAD"),
                        "message_size_bytes": r.get("message_size_bytes", 0),
                        "iterations": r.get("iterations", 0),
                        "warmup_iterations": r.get("warmup_iterations", 0),
                        "enc_latency_mean_ms": enc.get("mean", 0.0),
                        "enc_latency_median_ms": enc.get("median", 0.0),
                        "enc_latency_std_dev_ms": enc.get("std_dev", 0.0),
                        "enc_latency_ci95_low": ci[0],
                        "enc_latency_ci95_high": ci[1],
                        "throughput_mean_mbps": tp.get("mean", 0.0),
                        "peak_rss_mb": mem.get("peak_rss_mb", 0.0),
                        "heap_peak_bytes": mem.get("heap_peak_bytes", 0),
                    }
                )

        return filepath

    def export_json(self, suite: BenchmarkSuite, filepath: str) -> str:
        """Export full benchmark suite to structured JSON format.

        Args:
            suite: BenchmarkSuite object.
            filepath: Target file path.

        Returns:
            str: Destination file path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(suite.to_dict(), f, indent=2)
        return filepath

    def export_markdown(self, suite: BenchmarkSuite, filepath: str) -> str:
        """Export Markdown benchmark performance & comparison tables.

        Args:
            suite: BenchmarkSuite object.
            filepath: Target file path.

        Returns:
            str: Destination file path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        suite_dict = suite.to_dict()
        results = suite_dict.get("results", [])
        meta = suite_dict.get("metadata", {})
        comp = suite_dict.get("comparisons", {})

        md = f"""# Large-Scale Cryptographic Benchmark Results

## Environment & Hardware Metadata
- **Algorithm**: {meta.get("algorithm", "KDR-CA-AEAD")}
- **Python Version**: {meta.get("python_implementation", "CPython")} {meta.get("python_version", "3.13")}
- **OS / Platform**: {meta.get("platform", "Windows")}
- **CPU Architecture**: {meta.get("processor", "x86_64")} ({meta.get("cpu_count_logical", 1)} cores)
- **RAM Capacity**: {meta.get("ram_total_gb", 0.0)} GB
- **Timestamp (UTC)**: {meta.get("timestamp_utc", "N/A")}
- **Git Revision**: `{meta.get("git_revision", "N/A")}`

---

## Payload Scalability Benchmark Table

| Payload Size | Iterations | Enc Latency Mean (ms) | 95% Confidence Interval (ms) | Throughput Mean (MB/s) | Peak RSS (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for r in results:
            sz = r.get("message_size_bytes", 0)
            iters = r.get("iterations", 0)
            enc = r.get("encryption_latency", {})
            tp = r.get("throughput_mbps", {})
            mem = r.get("memory", {})
            ci = enc.get("confidence_interval_95", (0.0, 0.0))

            md += f"| `{sz} B` | `{iters}` | `{enc.get('mean', 0.0):.4f} ms` | `[{ci[0]:.4f}, {ci[1]:.4f}]` | `{tp.get('mean', 0.0):.4f} MB/s` | `{mem.get('peak_rss_mb', 0.0):.2f} MB` |\n"

        if comp:
            md += """
---

## Multi-Cipher Comparative Evaluation Table

| Cipher Scheme | Implementation Engine | Throughput (MB/s) | Latency Mean (ms) |
| :--- | :--- | :--- | :--- |
"""
            for c_data in comp.values():
                c_name = c_data.get("cipher_name", "N/A")
                imp = c_data.get("implementation", "N/A")
                tp = c_data.get("throughput_mbps", 0.0)
                lat = c_data.get("latency_ms", {}).get("mean", 0.0)
                md += f"| `{c_name}` | `{imp}` | `{tp:.4f} MB/s` | `{lat:.4f} ms` |\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        return filepath

    def export_metadata(self, metadata: Dict[str, Any], filepath: str) -> str:
        """Export hardware and software environment metadata to JSON format.

        Args:
            metadata: Metadata dictionary.
            filepath: Target file path.

        Returns:
            str: Destination file path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        return filepath
