"""Cryptographic Profiler Subsystem.

Provides `CryptographicProfiler` for measuring execution latency, Python heap allocations,
peak Resident Set Size (RSS), and object allocations using `tracemalloc` and `perf_counter_ns`.
"""

import os
import sys
import time
import tracemalloc
from typing import Any, Callable, Dict, Optional, Tuple

from .metrics import PerformanceMetrics


def _get_peak_rss_mb() -> float:
    """Get current peak Resident Set Size (RSS) memory footprint in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return float(process.memory_info().rss / (1024.0 * 1024.0))
    except Exception:
        # Fallback to sys/getsizeof heuristic or resource module on POSIX
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            # On Linux maxrss is in KB, on macOS in Bytes
            factor = 1024.0 if sys.platform.startswith("linux") else (1024.0 * 1024.0)
            return float(usage.ru_maxrss / factor)
        except Exception:
            return 0.0


class CryptographicProfiler:
    """High-resolution Cryptographic Profiler."""

    def __init__(self) -> None:
        """Initialize CryptographicProfiler."""
        self._is_active: bool = False
        self._start_time: int = 0
        self._start_rss: float = 0.0

    def start_profiling(self) -> None:
        """Start memory and latency profiling."""
        tracemalloc.start()
        self._start_rss = _get_peak_rss_mb()
        self._start_time = time.perf_counter_ns()
        self._is_active = True

    def stop_profiling(self) -> Dict[str, Any]:
        """Stop profiling and return performance metrics summary.

        Returns:
            Dict[str, Any]: Profile metrics summary dictionary.
        """
        if not self._is_active:
            return {}

        end_time = time.perf_counter_ns()
        current_alloc, peak_alloc = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_rss = _get_peak_rss_mb()
        dt_ms = (end_time - self._start_time) / 1000000.0
        self._is_active = False

        return {
            "execution_time_ms": round(dt_ms, 4),
            "heap_peak_bytes": peak_alloc,
            "heap_current_bytes": current_alloc,
            "peak_rss_mb": round(end_rss, 4),
        }

    def profile_function(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Tuple[Any, Dict[str, Any]]:
        """Profile execution latency and memory footprint of a target function.

        Args:
            func: Target function to execute.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Tuple[Any, Dict[str, Any]]: Function result and profiling metrics dictionary.
        """
        self.start_profiling()
        result = func(*args, **kwargs)
        metrics = self.stop_profiling()
        return result, metrics
