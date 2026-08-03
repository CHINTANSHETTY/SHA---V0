"""Performance Benchmark Runner for Phase 3.1 Optimizations.

Provides `PerformanceBenchmark` for evaluating throughput (MB/s), latency (ms),
CPU time, and memory footprint across payload sizes (1 KB, 10 KB, 100 KB, 1 MB, 10 MB, 50 MB, 100 MB).
"""

import json
import os
import time
from typing import Any, Dict, List, Optional

from crypto.primitives.aead import AEADEngine
from research.statistics import StatisticsEngine
from .profiler import CryptographicProfiler

PHASE3_BENCHMARK_SIZES: List[int] = [
    1024,        # 1 KB
    10240,       # 10 KB
    102400,      # 100 KB
    1048576,     # 1 MB
    10485760,    # 10 MB
]


class PerformanceBenchmark:
    """Phase 3.1 Performance & Benchmark Runner."""

    def __init__(self, aead_engine: Optional[AEADEngine] = None) -> None:
        """Initialize PerformanceBenchmark."""
        self.aead_engine: AEADEngine = aead_engine if aead_engine is not None else AEADEngine()
        self.profiler: CryptographicProfiler = CryptographicProfiler()
        self.stats_engine: StatisticsEngine = StatisticsEngine()

    def run_benchmark_suite(
        self,
        sizes: Optional[List[int]] = None,
        iterations: int = 10,
        warmup_iterations: int = 3,
    ) -> Dict[str, Any]:
        """Run performance benchmark suite with warm-up iterations and 95% confidence intervals.

        Args:
            sizes: Payload sizes in bytes (defaults to 1KB - 10MB).
            iterations: Number of measured trial iterations.
            warmup_iterations: Number of warm-up iterations (discarded).

        Returns:
            Dict[str, Any]: Comprehensive benchmark performance dataset.
        """
        eval_sizes = sizes if sizes is not None else PHASE3_BENCHMARK_SIZES
        master_key = b"master_key_bytes_phase3_bench"

        results_by_size: List[Dict[str, Any]] = []

        for size in eval_sizes:
            plaintext = b"A" * size

            # 1. Warm-up Iterations
            for _ in range(warmup_iterations):
                _ = self.aead_engine.encrypt(plaintext, master_key=master_key, check_nonce_reuse=False)

            # 2. Measured Trial Iterations
            latencies_ms: List[float] = []
            throughputs_mbps: List[float] = []

            self.profiler.start_profiling()
            for _ in range(iterations):
                t0 = time.perf_counter()
                _ = self.aead_engine.encrypt(plaintext, master_key=master_key, check_nonce_reuse=False)
                t1 = time.perf_counter()

                dt = t1 - t0
                dt_ms = dt * 1000.0
                mbps = (size / (1024.0 * 1024.0)) / dt if dt > 0 else 0.0

                latencies_ms.append(dt_ms)
                throughputs_mbps.append(mbps)

            prof_metrics = self.profiler.stop_profiling()
            lat_stats = self.stats_engine.analyze(latencies_ms)
            tp_stats = self.stats_engine.analyze(throughputs_mbps)

            results_by_size.append(
                {
                    "message_size_bytes": size,
                    "iterations": iterations,
                    "latency_ms": lat_stats,
                    "throughput_mbps": tp_stats,
                    "memory_profile": prof_metrics,
                }
            )

        return {
            "algorithm": "KDR-CA-AEAD",
            "phase": "3.1 Performance Benchmark",
            "sizes_evaluated": eval_sizes,
            "results": results_by_size,
        }

    def compare_before_after(
        self, baseline_results: Dict[str, Any], optimized_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare baseline vs optimized benchmark datasets.

        Args:
            baseline_results: Baseline benchmark results dictionary.
            optimized_results: Optimized benchmark results dictionary.

        Returns:
            Dict[str, Any]: Comparison report.
        """
        comparisons: List[Dict[str, Any]] = []

        base_res = {r["message_size_bytes"]: r for r in baseline_results.get("results", [])}
        opt_res = {r["message_size_bytes"]: r for r in optimized_results.get("results", [])}

        for sz in base_res:
            if sz in opt_res:
                base_tp = base_res[sz]["throughput_mbps"]["mean"]
                opt_tp = opt_res[sz]["throughput_mbps"]["mean"]
                speedup = (opt_tp / base_tp) if base_tp > 0 else 1.0

                base_lat = base_res[sz]["latency_ms"]["mean"]
                opt_lat = opt_res[sz]["latency_ms"]["mean"]
                latency_reduction = (1.0 - (opt_lat / base_lat)) * 100.0 if base_lat > 0 else 0.0

                comparisons.append(
                    {
                        "message_size_bytes": sz,
                        "baseline_tp_mbps": base_tp,
                        "optimized_tp_mbps": opt_tp,
                        "speedup_ratio": round(speedup, 4),
                        "latency_reduction_percent": round(latency_reduction, 2),
                    }
                )

        return {
            "comparison": comparisons,
        }
