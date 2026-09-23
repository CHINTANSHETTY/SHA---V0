"""Shannon Entropy, Min-Entropy, and Byte Distribution Analysis.

This module provides `EntropyAnalyzer` for computing Shannon entropy, min-entropy,
normalized entropy, byte occurrence histograms, and bit balance metrics.
"""

import math
from typing import Any, Dict, List


class EntropyAnalyzer:
    """Entropy and Distribution Analyzer."""

    def calculate_shannon_entropy(self, data: bytes) -> float:
        """Compute Shannon Entropy of a byte sequence in bits per byte [0.0, 8.0].

        Args:
            data: Binary byte sequence.

        Returns:
            float: Shannon entropy value.
        """
        if not data:
            return 0.0

        n = len(data)
        freqs: Dict[int, int] = {}
        for b in data:
            freqs[b] = freqs.get(b, 0) + 1

        entropy = 0.0
        for count in freqs.values():
            p = count / n
            entropy -= p * math.log2(p)

        return float(round(entropy, 6))

    def calculate_min_entropy(self, data: bytes) -> float:
        """Compute Min-Entropy H_infinity = -log2(max_i p_i).

        Args:
            data: Binary byte sequence.

        Returns:
            float: Min-entropy value.
        """
        if not data:
            return 0.0

        n = len(data)
        freqs: Dict[int, int] = {}
        for b in data:
            freqs[b] = freqs.get(b, 0) + 1

        max_prob = max(freqs.values()) / n
        return float(round(-math.log2(max_prob), 6))

    def calculate_normalized_entropy(self, data: bytes) -> float:
        """Compute Normalized Entropy H / 8.0 [0.0, 1.0].

        Args:
            data: Binary byte sequence.

        Returns:
            float: Normalized entropy value.
        """
        h = self.calculate_shannon_entropy(data)
        return float(round(h / 8.0, 6))

    def histogram(self, data: bytes) -> List[int]:
        """Compute 256-bin byte frequency occurrence histogram.

        Args:
            data: Binary byte sequence.

        Returns:
            List[int]: 256-element list of byte counts.
        """
        hist = [0] * 256
        for b in data:
            hist[b] += 1
        return hist

    def statistics(self, data: bytes) -> Dict[str, Any]:
        """Compute summary entropy and bit distribution statistics.

        Args:
            data: Binary byte sequence.

        Returns:
            Dict[str, Any]: Statistics dictionary.
        """
        if not data:
            return {
                "total_bytes": 0,
                "shannon_entropy": 0.0,
                "min_entropy": 0.0,
                "normalized_entropy": 0.0,
                "unique_bytes": 0,
                "bit_ratio_ones": 0.0,
                "passed": False,
            }

        total_bytes = len(data)
        shannon = self.calculate_shannon_entropy(data)
        min_ent = self.calculate_min_entropy(data)
        norm_ent = self.calculate_normalized_entropy(data)
        unique_b = len(set(data))

        total_bits = total_bytes * 8
        one_count = sum(bin(b).count("1") for b in data)
        one_ratio = one_count / total_bits if total_bits > 0 else 0.0

        passed = shannon >= 7.80 if total_bytes >= 100 else shannon >= 4.0

        return {
            "total_bytes": total_bytes,
            "unique_bytes": unique_b,
            "shannon_entropy": shannon,
            "min_entropy": min_ent,
            "normalized_entropy": norm_ent,
            "bit_ratio_ones": round(one_ratio, 6),
            "passed": passed,
        }

    def analyze(self, data: bytes) -> Dict[str, Any]:
        """Perform full entropy and byte frequency distribution analysis.

        Args:
            data: Binary byte sequence.

        Returns:
            Dict[str, Any]: Comprehensive analysis report.
        """
        stats = self.statistics(data)
        hist = self.histogram(data)
        return {
            **stats,
            "histogram": hist,
        }
