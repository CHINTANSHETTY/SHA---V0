r"""
Statistical Performance Consolidation Subsystem (`crypto.evaluation.consolidation`).

Computes comprehensive statistical metrics across benchmark iterations:
- Mean / Average
- Median
- Minimum & Maximum
- Standard Deviation ($\sigma$) & Variance ($\sigma^2$)
- 95% Confidence Intervals (Student's $t$-distribution for $N < 30$, Normal $Z = 1.96$ for $N \ge 30$)
"""

import math
from typing import Any, Dict, List, Sequence, Tuple


def compute_statistics(values: Sequence[float]) -> Dict[str, float]:
    """Computes full statistical distribution metrics for a list of numerical samples.

    Args:
        values: Sequence of numerical values (e.g. latency in milliseconds or throughput in MB/s).

    Returns:
        Dict[str, float]: Calculated statistical metrics dictionary.
    """
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "min": 0.0,
            "max": 0.0,
            "variance": 0.0,
            "std_dev": 0.0,
            "sem": 0.0,
            "ci_95_margin": 0.0,
            "ci_95_lower": 0.0,
            "ci_95_upper": 0.0,
        }

    n = len(values)
    sorted_vals = sorted(values)
    mean_val = sum(values) / n

    if n % 2 == 1:
        median_val = sorted_vals[n // 2]
    else:
        median_val = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

    min_val = sorted_vals[0]
    max_val = sorted_vals[-1]

    if n > 1:
        var_val = sum((x - mean_val) ** 2 for x in values) / (n - 1)
        std_val = math.sqrt(var_val)
    else:
        var_val = 0.0
        std_val = 0.0

    sem = std_val / math.sqrt(n) if n > 0 else 0.0

    # Student's t-distribution critical values for 95% confidence level (alpha = 0.05, two-tailed)
    t_table = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
        16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
        26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045,
    }

    if n < 30:
        t_crit = t_table.get(n - 1 if n > 1 else 1, 2.045)
    else:
        t_crit = 1.960  # Normal Z approximation

    margin = t_crit * sem

    return {
        "count": float(n),
        "mean": round(mean_val, 6),
        "median": round(median_val, 6),
        "min": round(min_val, 6),
        "max": round(max_val, 6),
        "variance": round(var_val, 8),
        "std_dev": round(std_val, 6),
        "sem": round(sem, 6),
        "ci_95_margin": round(margin, 6),
        "ci_95_lower": round(mean_val - margin, 6),
        "ci_95_upper": round(mean_val + margin, 6),
    }


class PerformanceConsolidator:
    """Consolidates benchmark data across runs and workloads into unified statistical summaries."""

    @staticmethod
    def consolidate_algorithm_runs(
        enc_times_ms: List[float],
        dec_times_ms: List[float],
        payload_size_bytes: int,
        peak_memory_bytes: int = 0,
    ) -> Dict[str, Any]:
        """Consolidate encryption and decryption execution metrics for a specific workload.

        Args:
            enc_times_ms: List of encryption execution times in milliseconds.
            dec_times_ms: List of decryption execution times in milliseconds.
            payload_size_bytes: Size of test payload in bytes.
            peak_memory_bytes: Peak RAM allocation in bytes.

        Returns:
            Dict[str, Any]: Consolidated metrics dictionary.
        """
        enc_stats = compute_statistics(enc_times_ms)
        dec_stats = compute_statistics(dec_times_ms)

        enc_tp_samples = [(payload_size_bytes / (1024.0 * 1024.0)) / (t / 1000.0) for t in enc_times_ms if t > 0]
        dec_tp_samples = [(payload_size_bytes / (1024.0 * 1024.0)) / (t / 1000.0) for t in dec_times_ms if t > 0]

        enc_tp_stats = compute_statistics(enc_tp_samples)
        dec_tp_stats = compute_statistics(dec_tp_samples)

        return {
            "payload_size_bytes": payload_size_bytes,
            "payload_size_kb": round(payload_size_bytes / 1024.0, 2),
            "payload_size_mb": round(payload_size_bytes / (1024.0 * 1024.0), 2),
            "peak_memory_kb": round(peak_memory_bytes / 1024.0, 2),
            "encryption": {
                "latency_ms": enc_stats,
                "throughput_mb_s": enc_tp_stats,
            },
            "decryption": {
                "latency_ms": dec_stats,
                "throughput_mb_s": dec_tp_stats,
            },
        }
