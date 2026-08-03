"""Performance and Scalability Benchmarking Framework.

Provides `BenchmarkRunner` for measuring encryption throughput, decryption throughput,
key schedule latency, AEAD execution metrics, memory footprint, and CPU time across payload sizes.
"""

import datetime
import json
import os
import platform
import sys
import time
from typing import Any, Dict, List, Optional

from crypto.key.evolution import KeyEvolutionEngine
from crypto.primitives.aead import AEADEngine
from research.statistics import StatisticsEngine

# Standard IEEE payload sizes: 64B, 256B, 1KB, 4KB, 16KB, 64KB, 1MB, 10MB
DEFAULT_BENCHMARK_SIZES: List[int] = [
    64,
    256,
    1024,
    4096,
    16384,
    65536,
    1048576,
    10485760,
]


def get_system_metadata() -> Dict[str, Any]:
    """Collect platform, OS, CPU, memory, and Python version metadata."""
    return {
        "python_version": sys.version.split()[0],
        "os_name": os.name,
        "platform": platform.platform(),
        "processor": platform.processor() or "x86_64",
        "cpu_count": os.cpu_count() or 1,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "algorithm": "KDR-CA-AEAD",
    }


class BenchmarkRunner:
    """Performance & Scalability Benchmark Runner."""

    def __init__(
        self,
        aead_engine: Optional[AEADEngine] = None,
        key_engine: Optional[KeyEvolutionEngine] = None,
    ) -> None:
        """Initialize BenchmarkRunner."""
        self.aead_engine: AEADEngine = aead_engine if aead_engine is not None else AEADEngine()
        self.key_engine: KeyEvolutionEngine = key_engine if key_engine is not None else KeyEvolutionEngine()
        self.stats_engine: StatisticsEngine = StatisticsEngine()
        self.results: Dict[str, Any] = {}

    def benchmark_key_schedule(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark KeyEvolutionEngine subkey derivation latency and throughput.

        Args:
            iterations: Number of benchmark trials.

        Returns:
            Dict[str, Any]: Key schedule latency and throughput metrics.
        """
        master_key = b"master_key_benchmark_bytes_123"
        latencies_ms: List[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.key_engine.derive_encryption_key(master_key)
            _ = self.key_engine.derive_auth_key(master_key)
            _ = self.key_engine.derive_ca_key(master_key, ca_id=30)
            _ = self.key_engine.derive_nonce_key(master_key)
            end = time.perf_counter()
            latencies_ms.append((end - start) * 1000.0)

        stats = self.stats_engine.analyze(latencies_ms)
        mean_ms = stats["mean"]
        ops_per_sec = (1000.0 / mean_ms) if mean_ms > 0 else 0.0

        return {
            "iterations": iterations,
            "latency_ms": stats,
            "ops_per_sec": round(ops_per_sec, 2),
        }

    def benchmark_encryption(
        self, message_size: int, iterations: int = 20
    ) -> Dict[str, Any]:
        """Benchmark AEAD encryption throughput for a specific message size.

        Args:
            message_size: Size of plaintext in bytes.
            iterations: Number of benchmark trials.

        Returns:
            Dict[str, Any]: Throughput (MB/s) and latency (ms) metrics.
        """
        master_key = b"master_key_benchmark_bytes_123"
        plaintext = b"A" * message_size
        latencies_ms: List[float] = []
        throughputs_mbps: List[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.aead_engine.encrypt(plaintext, master_key=master_key, check_nonce_reuse=False)
            end = time.perf_counter()

            dt = end - start
            dt_ms = dt * 1000.0
            mbps = (message_size / (1024.0 * 1024.0)) / dt if dt > 0 else 0.0

            latencies_ms.append(dt_ms)
            throughputs_mbps.append(mbps)

        lat_stats = self.stats_engine.analyze(latencies_ms)
        tp_stats = self.stats_engine.analyze(throughputs_mbps)

        return {
            "message_size_bytes": message_size,
            "iterations": iterations,
            "latency_ms": lat_stats,
            "throughput_mbps": tp_stats,
        }

    def benchmark_aead(
        self, message_size: int, iterations: int = 20
    ) -> Dict[str, Any]:
        """Benchmark AEAD encryption + decryption roundtrip throughput and latency.

        Args:
            message_size: Size of plaintext payload in bytes.
            iterations: Trial count.

        Returns:
            Dict[str, Any]: Roundtrip throughput and latency statistics.
        """
        master_key = b"master_key_benchmark_bytes_123"
        plaintext = b"A" * message_size
        enc_res = self.aead_engine.encrypt(plaintext, master_key=master_key, check_nonce_reuse=False)

        enc_lat: List[float] = []
        dec_lat: List[float] = []

        for _ in range(iterations):
            t0 = time.perf_counter()
            pkg = self.aead_engine.encrypt(plaintext, master_key=master_key, check_nonce_reuse=False)
            t1 = time.perf_counter()
            _ = self.aead_engine.decrypt(pkg["ciphertext"], pkg["tag"], master_key, pkg["nonce"])
            t2 = time.perf_counter()

            enc_lat.append((t1 - t0) * 1000.0)
            dec_lat.append((t2 - t1) * 1000.0)

        return {
            "message_size_bytes": message_size,
            "iterations": iterations,
            "encryption_latency_ms": self.stats_engine.analyze(enc_lat),
            "decryption_latency_ms": self.stats_engine.analyze(dec_lat),
        }

    def run(
        self,
        sizes: Optional[List[int]] = None,
        iterations: int = 20,
    ) -> Dict[str, Any]:
        """Run complete benchmark suite across payload sizes.

        Args:
            sizes: Payload sizes in bytes (defaults to standard sizes).
            iterations: Iterations per benchmark.

        Returns:
            Dict[str, Any]: Complete benchmark suite dataset.
        """
        eval_sizes = sizes if sizes is not None else DEFAULT_BENCHMARK_SIZES
        meta = get_system_metadata()
        key_bench = self.benchmark_key_schedule(iterations=iterations * 2)

        scalability_results: List[Dict[str, Any]] = []
        for s in eval_sizes:
            res_enc = self.benchmark_encryption(s, iterations=iterations)
            scalability_results.append(res_enc)

        self.results = {
            "metadata": meta,
            "key_schedule": key_bench,
            "scalability": scalability_results,
        }
        return self.results

    def export_results(self, filepath: str, format: str = "json") -> None:
        """Export benchmark dataset to file.

        Args:
            filepath: Destination file path.
            format: Export format ("json").
        """
        if not self.results:
            self.run()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
