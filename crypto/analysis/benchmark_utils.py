"""
Module:
    benchmark_utils.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    System Environment Discovery, Statistical Calculations, High-Precision Timing,
    and Tracemalloc Memory Measurement Utilities for Phase 2.4 Performance Benchmarking.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)

IEEE Mapping:
    Section VI-A – Benchmark Experimental Setup & System Environment Specifications
"""

from __future__ import annotations

import math
import os
import platform
import sys
import time
import tracemalloc
from typing import Any, Dict, List, Tuple


def get_system_metadata() -> Dict[str, Any]:
    """Discovers hardware, operating system, and Python runtime metadata.

    Returns:
        Dictionary containing OS name, CPU architecture, logical core count,
        Python version, and process ID.
    """
    return {
        "os_platform": platform.platform(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor() or "x86_64/ARM Generic",
        "cpu_count": os.cpu_count() or 1,
        "python_version": sys.version.split()[0],
        "python_compiler": platform.python_compiler(),
        "process_id": os.getpid(),
    }


def compute_statistics(data_points: List[float]) -> Dict[str, float]:
    """Calculates summary statistics for a list of measurement data points.

    Computes mean (mu), standard deviation (sigma), min, max, median,
    and 95% Confidence Interval (CI) half-margin.

    Args:
        data_points: List of float values (e.g. latency in ms).

    Returns:
        Dictionary with statistical summary metrics.
    """
    n = len(data_points)
    if n == 0:
        return {
            "mean": 0.0,
            "std_dev": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0,
            "ci_95_margin": 0.0,
            "ci_95_lower": 0.0,
            "ci_95_upper": 0.0,
        }

    sorted_pts = sorted(data_points)
    mean_val = sum(data_points) / n

    if n > 1:
        variance = sum((x - mean_val) ** 2 for x in data_points) / (n - 1)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 0.0

    # 95% Confidence Interval margin using z = 1.96
    ci_margin = 1.96 * (std_dev / math.sqrt(n)) if n > 1 else 0.0

    # Median
    if n % 2 == 1:
        median_val = sorted_pts[n // 2]
    else:
        median_val = (sorted_pts[n // 2 - 1] + sorted_pts[n // 2]) / 2.0

    return {
        "mean": round(mean_val, 6),
        "std_dev": round(std_dev, 6),
        "min": round(sorted_pts[0], 6),
        "max": round(sorted_pts[-1], 6),
        "median": round(median_val, 6),
        "ci_95_margin": round(ci_margin, 6),
        "ci_95_lower": round(max(0.0, mean_val - ci_margin), 6),
        "ci_95_upper": round(mean_val + ci_margin, 6),
    }


class PrecisionTimer:
    """Context manager for high-resolution nanosecond timing using time.perf_counter_ns()."""

    def __init__(self) -> None:
        self.start_ns: int = 0
        self.end_ns: int = 0
        self.elapsed_ns: int = 0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> PrecisionTimer:
        self.start_ns = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_ns = time.perf_counter_ns()
        self.elapsed_ns = self.end_ns - self.start_ns
        self.elapsed_ms = self.elapsed_ns / 1e6


class MemoryTracker:
    """Context manager for tracking memory allocation using Python tracemalloc."""

    def __init__(self) -> None:
        self.peak_bytes: int = 0
        self.current_bytes: int = 0

    def __enter__(self) -> MemoryTracker:
        tracemalloc.start()
        tracemalloc.reset_peak()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.current_bytes = current
        self.peak_bytes = peak

    @property
    def peak_kb(self) -> float:
        """Returns peak memory in Kilobytes."""
        return round(self.peak_bytes / 1024.0, 3)

    @property
    def peak_mb(self) -> float:
        """Returns peak memory in Megabytes."""
        return round(self.peak_bytes / (1024.0 * 1024.0), 4)
