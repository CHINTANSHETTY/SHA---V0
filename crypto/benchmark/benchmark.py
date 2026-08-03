"""Benchmark Data Models and Configuration (`crypto.benchmark.benchmark`).

Provides `BenchmarkConfig`, `BenchmarkResult`, and `BenchmarkSuite` data structures
for large-scale cryptographic scalability and performance evaluations.
"""

import os
import platform
import sys
import datetime
from typing import Any, Dict, List, Optional

# Standard IEEE payload sizes: 1KB, 10KB, 100KB, 1MB, 5MB, 10MB, 25MB, 50MB, 100MB
LARGE_SCALE_BENCHMARK_SIZES: List[int] = [
    1024,          # 1 KB
    10240,         # 10 KB
    102400,        # 100 KB
    1048576,       # 1 MB
    5242880,       # 5 MB
    10485760,      # 10 MB
    26214400,      # 25 MB
    52428800,      # 50 MB
    104857600,     # 100 MB
]


def collect_hardware_and_software_metadata() -> Dict[str, Any]:
    """Collect comprehensive hardware, software, CPU, RAM, and Python metadata.

    Returns:
        Dict[str, Any]: Environment metadata dictionary.
    """
    metadata: Dict[str, Any] = {
        "python_implementation": platform.python_implementation(),
        "python_version": sys.version.split()[0],
        "os_name": os.name,
        "os_version": platform.version(),
        "platform": platform.platform(),
        "architecture": platform.machine() or "x86_64",
        "processor": platform.processor() or "x86_64",
        "cpu_count_logical": os.cpu_count() or 1,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "algorithm": "KDR-CA-AEAD",
    }

    try:
        import psutil
        vm = psutil.virtual_memory()
        metadata["ram_total_bytes"] = vm.total
        metadata["ram_total_gb"] = round(vm.total / (1024.0 ** 3), 2)
        metadata["cpu_count_physical"] = psutil.cpu_count(logical=False) or os.cpu_count()
    except Exception:
        metadata["ram_total_bytes"] = 0
        metadata["ram_total_gb"] = 0.0
        metadata["cpu_count_physical"] = os.cpu_count() or 1

    # Optional Git commit hash detection
    try:
        import subprocess
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        metadata["git_revision"] = git_hash.decode("utf-8").strip()
    except Exception:
        metadata["git_revision"] = "N/A"

    return metadata


class BenchmarkConfig:
    """Configuration options for large-scale benchmark execution."""

    def __init__(
        self,
        sizes: Optional[List[int]] = None,
        iterations: int = 10,
        warmup_iterations: int = 3,
        seed: int = 42,
        include_comparisons: bool = True,
        output_dir: str = "benchmark_results",
    ) -> None:
        """Initialize BenchmarkConfig."""
        self.sizes: List[int] = sizes if sizes is not None else list(LARGE_SCALE_BENCHMARK_SIZES)
        self.iterations: int = max(1, iterations)
        self.warmup_iterations: int = max(0, warmup_iterations)
        self.seed: int = seed
        self.include_comparisons: bool = include_comparisons
        self.output_dir: str = output_dir

    def to_dict(self) -> Dict[str, Any]:
        """Export config to dictionary."""
        return {
            "sizes": self.sizes,
            "iterations": self.iterations,
            "warmup_iterations": self.warmup_iterations,
            "seed": self.seed,
            "include_comparisons": self.include_comparisons,
            "output_dir": self.output_dir,
        }


class BenchmarkResult:
    """Encapsulates benchmark trial statistics for a single payload size."""

    def __init__(
        self,
        cipher_name: str,
        message_size_bytes: int,
        iterations: int,
        warmup_iterations: int,
        encryption_stats: Dict[str, Any],
        decryption_stats: Optional[Dict[str, Any]] = None,
        throughput_mbps_stats: Optional[Dict[str, Any]] = None,
        memory_stats: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize BenchmarkResult."""
        self.cipher_name: str = cipher_name
        self.message_size_bytes: int = message_size_bytes
        self.iterations: int = iterations
        self.warmup_iterations: int = warmup_iterations
        self.encryption_stats: Dict[str, Any] = encryption_stats
        self.decryption_stats: Dict[str, Any] = decryption_stats if decryption_stats is not None else {}
        self.throughput_mbps_stats: Dict[str, Any] = throughput_mbps_stats if throughput_mbps_stats is not None else {}
        self.memory_stats: Dict[str, Any] = memory_stats if memory_stats is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        """Export result as dictionary."""
        return {
            "cipher_name": self.cipher_name,
            "message_size_bytes": self.message_size_bytes,
            "iterations": self.iterations,
            "warmup_iterations": self.warmup_iterations,
            "encryption_latency": self.encryption_stats,
            "decryption_latency": self.decryption_stats,
            "throughput_mbps": self.throughput_mbps_stats,
            "memory": self.memory_stats,
        }


class BenchmarkSuite:
    """Encapsulates a full benchmark suite run including metadata and results."""

    def __init__(
        self,
        config: BenchmarkConfig,
        metadata: Optional[Dict[str, Any]] = None,
        results: Optional[List[BenchmarkResult]] = None,
        comparisons: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize BenchmarkSuite."""
        self.config: BenchmarkConfig = config
        self.metadata: Dict[str, Any] = metadata if metadata is not None else collect_hardware_and_software_metadata()
        self.results: List[BenchmarkResult] = results if results is not None else []
        self.comparisons: Dict[str, Any] = comparisons if comparisons is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        """Export suite data as dictionary."""
        return {
            "config": self.config.to_dict(),
            "metadata": self.metadata,
            "results": [r.to_dict() for r in self.results],
            "comparisons": self.comparisons,
        }
