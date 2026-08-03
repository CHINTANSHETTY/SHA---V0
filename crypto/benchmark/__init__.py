"""Cryptographic Profiling & Benchmark Subsystem (`crypto.benchmark`).

Provides `CryptographicProfiler`, `PerformanceBenchmark`, `PerformanceMetrics`,
`BenchmarkConfig`, `BenchmarkResult`, `BenchmarkSuite`, `LargeScaleBenchmarkRunner`,
and `BenchmarkExporter` for publication-ready performance and scalability evaluations.
"""

from .benchmark import (
    LARGE_SCALE_BENCHMARK_SIZES,
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkSuite,
    collect_hardware_and_software_metadata,
)
from .exporter import BenchmarkExporter
from .metrics import PerformanceMetrics
from .performance import PHASE3_BENCHMARK_SIZES, PerformanceBenchmark
from .profiler import CryptographicProfiler
from .runner import LargeScaleBenchmarkRunner

__all__ = [
    "CryptographicProfiler",
    "PerformanceBenchmark",
    "PerformanceMetrics",
    "PHASE3_BENCHMARK_SIZES",
    "LARGE_SCALE_BENCHMARK_SIZES",
    "BenchmarkConfig",
    "BenchmarkResult",
    "BenchmarkSuite",
    "LargeScaleBenchmarkRunner",
    "BenchmarkExporter",
    "collect_hardware_and_software_metadata",
]
