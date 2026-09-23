"""Statistical Analysis Subsystem for Cryptographic Research Validation.

Provides `StatisticalEngine` for Pearson correlation, Spearman rank correlation,
Kendall Tau, Autocorrelation, Cross-correlation, Shannon entropy, Min-entropy,
Chi-square goodness-of-fit, bit/byte frequency histograms, and Hamming distance propagation.
"""

import math
from typing import Any, Dict, List, Tuple


class StatisticalEngine:
    """Advanced Statistical Engine for Cryptographic Security Evaluations."""

    def mean(self, data: List[float]) -> float:
        """Compute arithmetic mean."""
        if not data:
            return 0.0
        return float(sum(data) / len(data))

    def variance(self, data: List[float]) -> float:
        """Compute sample variance."""
        if len(data) < 2:
            return 0.0
        m = self.mean(data)
        return float(sum((x - m) ** 2 for x in data) / (len(data) - 1))

    def std_dev(self, data: List[float]) -> float:
        """Compute sample standard deviation."""
        return float(math.sqrt(self.variance(data)))

    def pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Compute Pearson correlation coefficient r between two numeric vectors.

        r = sum((x_i - mean_x) * (y_i - mean_y)) / (sqrt(sum((x_i - mean_x)^2)) * sqrt(sum((y_i - mean_y)^2)))

        Args:
            x: First vector.
            y: Second vector.

        Returns:
            float: Pearson correlation coefficient in [-1.0, 1.0].
        """
        n = min(len(x), len(y))
        if n < 2:
            return 0.0

        mx = self.mean(x[:n])
        my = self.mean(y[:n])

        num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        den_x = sum((x[i] - mx) ** 2 for i in range(n))
        den_y = sum((y[i] - my) ** 2 for i in range(n))

        denom = math.sqrt(den_x * den_y)
        if denom == 0.0:
            return 0.0

        return float(max(-1.0, min(1.0, num / denom)))

    def _rank_vector(self, v: List[float]) -> List[float]:
        """Convert a vector of floats to fractional ranks."""
        n = len(v)
        indexed = sorted((v[i], i) for i in range(n))
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j][0] == indexed[j + 1][0]:
                j += 1
            avg_rank = (i + j + 2) / 2.0
            for k in range(i, j + 1):
                ranks[indexed[k][1]] = avg_rank
            i = j + 1
        return ranks

    def spearman_correlation(self, x: List[float], y: List[float]) -> float:
        """Compute Spearman rank correlation coefficient rho between two vectors.

        Args:
            x: First vector.
            y: Second vector.

        Returns:
            float: Spearman rank correlation in [-1.0, 1.0].
        """
        n = min(len(x), len(y))
        if n < 2:
            return 0.0

        rx = self._rank_vector(x[:n])
        ry = self._rank_vector(y[:n])
        return self.pearson_correlation(rx, ry)

    def kendall_tau(self, x: List[float], y: List[float]) -> float:
        """Compute Kendall Tau rank correlation coefficient.

        Args:
            x: First vector.
            y: Second vector.

        Returns:
            float: Kendall Tau correlation in [-1.0, 1.0].
        """
        n = min(len(x), len(y))
        if n < 2:
            return 0.0

        concordant = 0
        discordant = 0

        for i in range(n):
            for j in range(i + 1, n):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                prod = dx * dy
                if prod > 0:
                    concordant += 1
                elif prod < 0:
                    discordant += 1

        total_pairs = (n * (n - 1)) // 2
        if total_pairs == 0:
            return 0.0

        return float((concordant - discordant) / total_pairs)

    def autocorrelation(self, sequence: List[float], lag: int = 1) -> float:
        """Compute autocorrelation at specified lag k.

        Args:
            sequence: Input numeric sequence.
            lag: Lag offset (>= 1).

        Returns:
            float: Autocorrelation coefficient.
        """
        n = len(sequence)
        if n <= lag:
            return 0.0

        x1 = sequence[:-lag]
        x2 = sequence[lag:]
        return self.pearson_correlation(x1, x2)

    def cross_correlation(self, x: List[float], y: List[float], lag: int = 0) -> float:
        """Compute cross-correlation between x and y at specified lag.

        Args:
            x: First sequence.
            y: Second sequence.
            lag: Lag offset (>= 0).

        Returns:
            float: Cross-correlation coefficient.
        """
        if lag == 0:
            return self.pearson_correlation(x, y)
        if lag > 0:
            if len(x) <= lag:
                return 0.0
            return self.pearson_correlation(x[:-lag], y[lag:])
        abs_lag = abs(lag)
        if len(y) <= abs_lag:
            return 0.0
        return self.pearson_correlation(x[abs_lag:], y[:-abs_lag])

    def shannon_entropy(self, data: bytes) -> float:
        """Compute Shannon entropy H in bits per byte (ideal H = 8.0).

        H = - sum(p_i * log2(p_i))

        Args:
            data: Binary payload bytes.

        Returns:
            float: Shannon entropy in [0.0, 8.0].
        """
        if not data:
            return 0.0

        counts = [0] * 256
        for b in data:
            counts[b] += 1

        total = float(len(data))
        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        return float(round(entropy, 6))

    def min_entropy(self, data: bytes) -> float:
        """Compute Min-entropy H_infinity in bits per byte.

        H_infinity = - log2(max(p_i))

        Args:
            data: Binary payload bytes.

        Returns:
            float: Min-entropy value.
        """
        if not data:
            return 0.0

        counts = [0] * 256
        for b in data:
            counts[b] += 1

        max_count = max(counts)
        p_max = max_count / float(len(data))
        return float(round(-math.log2(p_max), 6))

    def max_entropy(self) -> float:
        """Get theoretical maximum entropy for 8-bit bytes (8.0 bits/byte)."""
        return 8.0

    def chi_square_statistic(self, data: bytes) -> Dict[str, float]:
        """Compute Chi-square goodness-of-fit statistic against uniform byte distribution.

        Chi2 = sum((observed_i - expected)^2 / expected), for 256 byte values (df=255).

        Args:
            data: Binary payload bytes.

        Returns:
            Dict[str, float]: Chi-square statistic and normalized value.
        """
        if not data:
            return {"chi_square": 0.0, "degrees_of_freedom": 255.0, "expected_frequency": 0.0}

        counts = [0] * 256
        for b in data:
            counts[b] += 1

        expected = len(data) / 256.0
        chi2 = 0.0
        for count in counts:
            chi2 += ((count - expected) ** 2) / expected if expected > 0 else 0.0

        return {
            "chi_square": float(round(chi2, 4)),
            "degrees_of_freedom": 255.0,
            "expected_frequency": float(round(expected, 4)),
        }

    def bit_frequency_histogram(self, data: bytes) -> Dict[str, int]:
        """Compute bit frequency count of 0s and 1s in byte payload.

        Args:
            data: Binary payload bytes.

        Returns:
            Dict[str, int]: Count of zeros and ones.
        """
        ones = sum(bin(b).count("1") for b in data)
        zeros = (len(data) * 8) - ones
        return {"zeros": zeros, "ones": ones}

    def byte_frequency_histogram(self, data: bytes) -> List[int]:
        """Compute 256-element byte frequency histogram array.

        Args:
            data: Binary payload bytes.

        Returns:
            List[int]: 256-element integer count array.
        """
        counts = [0] * 256
        for b in data:
            counts[b] += 1
        return counts

    def hamming_distance(self, b1: bytes, b2: bytes) -> int:
        """Compute Hamming distance (number of differing bits) between two byte sequences.

        Args:
            b1: First byte sequence.
            b2: Second byte sequence.

        Returns:
            int: Bit difference count.
        """
        n = min(len(b1), len(b2))
        dist = 0
        for i in range(n):
            dist += bin(b1[i] ^ b2[i]).count("1")
        return dist + (abs(len(b1) - len(b2)) * 8)

    def propagation_ratio(self, b1: bytes, b2: bytes) -> float:
        """Compute bit flip propagation ratio (flipped_bits / total_bits).

        Args:
            b1: First byte sequence.
            b2: Second byte sequence.

        Returns:
            float: Bit flip propagation ratio in [0.0, 1.0].
        """
        total_bits = max(len(b1), len(b2)) * 8
        if total_bits == 0:
            return 0.0
        hd = self.hamming_distance(b1, b2)
        return float(round(hd / float(total_bits), 6))
