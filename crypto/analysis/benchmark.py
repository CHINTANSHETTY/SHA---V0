"""
Module:
    benchmark.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Core Performance Benchmarking Engine for Phase 2.4. Evaluates encryption latency,
    decryption latency, execution throughput (MB/s), peak memory utilization,
    and CPU scaling across configurable payload sizes.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)

IEEE Mapping:
    Section VI-B – Performance Benchmarking Engine & Measurement Protocol
"""

from __future__ import annotations

import gc
from typing import Any, Callable, Dict, List

from crypto.analysis.benchmark_utils import (
    MemoryTracker,
    PrecisionTimer,
    compute_statistics,
)


def benchmark_function(
    func: Callable[[], Any],
    runs: int = 20,
    warmup_runs: int = 3
) -> Dict[str, Any]:
    """Executes a target function repeatedly and computes execution time statistics and memory usage.

    Args:
        func: Zero-argument callable to benchmark.
        runs: Number of timed iterations (default 20).
        warmup_runs: Number of un-timed warm-up iterations (default 3).

    Returns:
        Dictionary containing timing statistics (ms) and peak memory allocation (KB).
    """
    # Warmup runs to fill instruction cache and CPU pipelines
    for _ in range(warmup_runs):
        _ = func()

    gc.collect()

    latencies_ms: List[float] = []
    for _ in range(runs):
        with PrecisionTimer() as timer:
            _ = func()
        latencies_ms.append(timer.elapsed_ms)

    # Memory allocation tracking
    gc.collect()
    with MemoryTracker() as mem_tracker:
        _ = func()
    peak_kb = mem_tracker.peak_kb

    stats = compute_statistics(latencies_ms)
    stats["peak_memory_kb"] = peak_kb
    stats["raw_latencies_ms"] = latencies_ms

    return stats


def run_algorithm_benchmark(
    algorithm_name: str,
    encrypt_fn: Callable[[bytes], Any],
    decrypt_fn: Callable[[Any], bytes],
    payload: bytes,
    runs: int = 20
) -> Dict[str, Any]:
    """Benchmarks encryption and decryption performance for a given cipher algorithm and payload.

    Args:
        algorithm_name: Identifier string of the cipher (e.g., 'KDR-CA-AEAD').
        encrypt_fn: Function mapping payload bytes -> ciphertext/package.
        decrypt_fn: Function mapping ciphertext/package -> plaintext bytes.
        payload: Input byte buffer.
        runs: Repeated measurement trial count.

    Returns:
        Dictionary containing complete performance metrics, throughput, latency, and memory metrics.
    """
    payload_size_bytes = len(payload)
    payload_size_mb = payload_size_bytes / (1024.0 * 1024.0)

    # 1. Benchmark Encryption
    enc_stats = benchmark_function(lambda: encrypt_fn(payload), runs=runs)
    enc_mean_sec = enc_stats["mean"] / 1000.0
    enc_throughput_mbps = payload_size_mb / enc_mean_sec if enc_mean_sec > 0 else 0.0

    # Generate reference ciphertext package for decryption benchmarking
    ciphertext_pkg = encrypt_fn(payload)

    # 2. Benchmark Decryption
    dec_stats = benchmark_function(lambda: decrypt_fn(ciphertext_pkg), runs=runs)
    dec_mean_sec = dec_stats["mean"] / 1000.0
    dec_throughput_mbps = payload_size_mb / dec_mean_sec if dec_mean_sec > 0 else 0.0

    # Calculate CPU efficiency / time per byte (microseconds per byte)
    us_per_byte_enc = (enc_stats["mean"] * 1000.0) / payload_size_bytes if payload_size_bytes > 0 else 0.0
    us_per_byte_dec = (dec_stats["mean"] * 1000.0) / payload_size_bytes if payload_size_bytes > 0 else 0.0

    return {
        "algorithm": algorithm_name,
        "payload_size_bytes": payload_size_bytes,
        "payload_size_kb": round(payload_size_bytes / 1024.0, 2),
        "payload_size_mb": round(payload_size_mb, 4),
        "runs": runs,
        "encryption": {
            "mean_ms": enc_stats["mean"],
            "std_dev_ms": enc_stats["std_dev"],
            "min_ms": enc_stats["min"],
            "max_ms": enc_stats["max"],
            "median_ms": enc_stats["median"],
            "ci_95_margin_ms": enc_stats["ci_95_margin"],
            "throughput_mb_per_sec": round(enc_throughput_mbps, 2),
            "us_per_byte": round(us_per_byte_enc, 4),
            "peak_memory_kb": enc_stats["peak_memory_kb"],
        },
        "decryption": {
            "mean_ms": dec_stats["mean"],
            "std_dev_ms": dec_stats["std_dev"],
            "min_ms": dec_stats["min"],
            "max_ms": dec_stats["max"],
            "median_ms": dec_stats["median"],
            "ci_95_margin_ms": dec_stats["ci_95_margin"],
            "throughput_mb_per_sec": round(dec_throughput_mbps, 2),
            "us_per_byte": round(us_per_byte_dec, 4),
            "peak_memory_kb": dec_stats["peak_memory_kb"],
        },
    }
