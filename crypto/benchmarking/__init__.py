"""
Module:
    __init__.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Performance Benchmarking & Verification Subsystem (Phase 4.3).

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

from crypto.benchmarking.benchmark_verification import (
    OperationBenchmarkResult,
    calculate_stats,
    benchmark_core_operations,
    benchmark_payload_scaling,
    detect_performance_regressions,
    run_full_benchmark_verification,
)
from crypto.benchmarking.benchmark_report import generate_benchmark_reports

__all__ = [
    "OperationBenchmarkResult",
    "calculate_stats",
    "benchmark_core_operations",
    "benchmark_payload_scaling",
    "detect_performance_regressions",
    "run_full_benchmark_verification",
    "generate_benchmark_reports",
]
