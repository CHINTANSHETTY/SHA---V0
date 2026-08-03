"""Statistical Analysis Subsystem for Cryptographic Research.

Provides `StatisticsEngine` for computing mean, median, variance, standard deviation,
95% confidence intervals, min/max bounds, and percentiles for benchmark datasets.
"""

import math
from typing import Any, Dict, List, Tuple


class StatisticsEngine:
    """Statistical Analysis Engine for research datasets."""

    def calculate_mean(self, data: List[float]) -> float:
        """Compute arithmetic mean of a dataset.

        Args:
            data: List of numeric values.

        Returns:
            float: Mean value.
        """
        if not data:
            return 0.0
        return float(sum(data) / len(data))

    def calculate_median(self, data: List[float]) -> float:
        """Compute median value of a dataset.

        Args:
            data: List of numeric values.

        Returns:
            float: Median value.
        """
        if not data:
            return 0.0
        sorted_d = sorted(data)
        n = len(sorted_d)
        mid = n // 2
        if n % 2 == 1:
            return float(sorted_d[mid])
        return float((sorted_d[mid - 1] + sorted_d[mid]) / 2.0)

    def calculate_variance(self, data: List[float]) -> float:
        """Compute sample variance of a dataset.

        Args:
            data: List of numeric values.

        Returns:
            float: Sample variance.
        """
        if len(data) < 2:
            return 0.0
        m = self.calculate_mean(data)
        return float(sum((x - m) ** 2 for x in data) / (len(data) - 1))

    def calculate_std_dev(self, data: List[float]) -> float:
        """Compute sample standard deviation of a dataset.

        Args:
            data: List of numeric values.

        Returns:
            float: Sample standard deviation.
        """
        return float(math.sqrt(self.calculate_variance(data)))

    def calculate_confidence_interval(
        self, data: List[float], confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Compute confidence interval (default 95% CI) for mean.

        95% CI = mean +/- (1.96 * std_dev / sqrt(n)).

        Args:
            data: List of numeric values.
            confidence: Confidence level (0.95 or 0.99).

        Returns:
            Tuple[float, float]: (ci_lower, ci_upper).
        """
        if not data:
            return (0.0, 0.0)
        n = len(data)
        mean_val = self.calculate_mean(data)
        if n < 2:
            return (mean_val, mean_val)

        std_err = self.calculate_std_dev(data) / math.sqrt(n)
        z = 1.96 if confidence == 0.95 else 2.576
        margin = z * std_err
        return (float(round(mean_val - margin, 6)), float(round(mean_val + margin, 6)))

    def calculate_percentiles(
        self, data: List[float], percentiles: List[float] = None
    ) -> Dict[str, float]:
        """Compute percentiles (p25, p50, p75, p90, p99) for a dataset.

        Args:
            data: List of numeric values.
            percentiles: List of percentile ranks (defaults to [25, 50, 75, 90, 99]).

        Returns:
            Dict[str, float]: Percentile values dictionary.
        """
        if percentiles is None:
            percentiles = [25.0, 50.0, 75.0, 90.0, 99.0]

        if not data:
            return {f"p{int(p)}": 0.0 for p in percentiles}

        sorted_d = sorted(data)
        n = len(sorted_d)
        res: Dict[str, float] = {}

        for p in percentiles:
            k = (n - 1) * (p / 100.0)
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                val = sorted_d[int(k)]
            else:
                val = sorted_d[int(f)] * (c - k) + sorted_d[int(c)] * (k - f)
            res[f"p{int(p)}"] = float(round(val, 6))

        return res

    def analyze(self, data: List[float]) -> Dict[str, Any]:
        """Compute comprehensive statistical metrics dictionary for a dataset.

        Args:
            data: List of numeric sample values.

        Returns:
            Dict[str, Any]: Statistical metrics summary.
        """
        if not data:
            return {
                "sample_count": 0,
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "variance": 0.0,
                "std_dev": 0.0,
                "confidence_interval_95": (0.0, 0.0),
                "percentiles": {},
            }

        n = len(data)
        mean_val = self.calculate_mean(data)
        median_val = self.calculate_median(data)
        min_val = float(min(data))
        max_val = float(max(data))
        var_val = self.calculate_variance(data)
        std_val = self.calculate_std_dev(data)
        ci95 = self.calculate_confidence_interval(data, confidence=0.95)
        pcts = self.calculate_percentiles(data)

        return {
            "sample_count": n,
            "mean": round(mean_val, 6),
            "median": round(median_val, 6),
            "min": round(min_val, 6),
            "max": round(max_val, 6),
            "variance": round(var_val, 6),
            "std_dev": round(std_val, 6),
            "confidence_interval_95": ci95,
            "percentiles": pcts,
        }

    def summary(self, stats: Dict[str, Any]) -> str:
        """Generate formatted human-readable statistical summary string.

        Args:
            stats: Statistical metrics dictionary.

        Returns:
            str: Human-readable summary string.
        """
        n = stats.get("sample_count", 0)
        mean_v = stats.get("mean", 0.0)
        std_v = stats.get("std_dev", 0.0)
        ci = stats.get("confidence_interval_95", (0.0, 0.0))
        pcts = stats.get("percentiles", {})

        return (
            f"Statistical Summary (N={n}):\n"
            f"  Mean: {mean_v:.6f} +/- {std_v:.6f}\n"
            f"  Median: {stats.get('median', 0.0):.6f}\n"
            f"  95% CI: [{ci[0]:.6f}, {ci[1]:.6f}]\n"
            f"  Min / Max: {stats.get('min', 0.0):.6f} / {stats.get('max', 0.0):.6f}\n"
            f"  P50 / P95: {pcts.get('p50', 0.0):.6f} / {pcts.get('p90', 0.0):.6f}"
        )
