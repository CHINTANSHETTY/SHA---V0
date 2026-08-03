"""Performance Metrics Data Structure.

Provides `PerformanceMetrics` for storing execution latency, memory heap allocations,
peak Resident Set Size (RSS), object allocation counts, and throughput metrics.
"""

from typing import Any, Dict, Optional, Tuple


class PerformanceMetrics:
    """Performance & Memory Metrics Data Structure."""

    def __init__(
        self,
        execution_time_ms: float = 0.0,
        heap_allocated_bytes: int = 0,
        peak_rss_mb: float = 0.0,
        object_allocations: int = 0,
        throughput_mbps: float = 0.0,
        confidence_interval_95: Tuple[float, float] = (0.0, 0.0),
    ) -> None:
        """Initialize PerformanceMetrics."""
        self.execution_time_ms: float = execution_time_ms
        self.heap_allocated_bytes: int = heap_allocated_bytes
        self.peak_rss_mb: float = peak_rss_mb
        self.object_allocations: int = object_allocations
        self.throughput_mbps: float = throughput_mbps
        self.confidence_interval_95: Tuple[float, float] = confidence_interval_95

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        return {
            "execution_time_ms": round(self.execution_time_ms, 4),
            "heap_allocated_bytes": self.heap_allocated_bytes,
            "peak_rss_mb": round(self.peak_rss_mb, 4),
            "object_allocations": self.object_allocations,
            "throughput_mbps": round(self.throughput_mbps, 4),
            "confidence_interval_95": self.confidence_interval_95,
        }
