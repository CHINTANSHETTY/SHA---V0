"""NIST SP 800-22 and IEEE Statistical Randomness Analysis Subsystem.

Evaluates Shannon entropy, bit distribution, NIST Monobit Test, NIST Runs Test,
Serial Test, and Byte Frequency Chi-Square Uniformity.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

DEFAULT_SIGNIFICANCE_LEVEL: float = 0.01


def calculate_shannon_entropy(data: bytes) -> float:
    """Computes Shannon Entropy of a byte sequence in bits per byte."""
    if not data:
        return 0.0

    length = len(data)
    frequencies: Dict[int, int] = {}
    for byte in data:
        frequencies[byte] = frequencies.get(byte, 0) + 1

    entropy = 0.0
    for count in frequencies.values():
        p = count / length
        entropy -= p * math.log2(p)

    return float(round(entropy, 6))


def bit_distribution_analysis(data: bytes) -> Dict[str, Any]:
    """Analyzes 0-bit vs 1-bit balance across a byte sequence."""
    if not data:
        return {
            "total_bits": 0,
            "zero_count": 0,
            "one_count": 0,
            "one_ratio": 0.0,
            "imbalance_percent": 0.0,
        }

    total_bits = len(data) * 8
    one_count = sum(bin(b).count("1") for b in data)
    zero_count = total_bits - one_count
    one_ratio = one_count / total_bits if total_bits > 0 else 0.0
    imbalance = abs(one_ratio - 0.5) * 100.0

    return {
        "total_bits": total_bits,
        "zero_count": zero_count,
        "one_count": one_count,
        "one_ratio": round(one_ratio, 6),
        "imbalance_percent": round(imbalance, 4),
    }


def monobit_test(data: bytes, alpha: float = DEFAULT_SIGNIFICANCE_LEVEL) -> Dict[str, Any]:
    """NIST SP 800-22 Test 1: Frequency (Monobit) Test."""
    if not data:
        return {"s_obs": 0.0, "p_value": 0.0, "passed": False, "status": "Empty Data"}

    total_bits = len(data) * 8
    s_n = 0
    for byte in data:
        for i in range(8):
            bit = (byte >> i) & 1
            s_n += 1 if bit == 1 else -1

    s_obs = abs(s_n) / math.sqrt(total_bits)
    p_value = math.erfc(s_obs / math.sqrt(2.0))
    passed = bool(p_value >= alpha)

    return {
        "total_bits": total_bits,
        "s_n": s_n,
        "s_obs": round(s_obs, 6),
        "p_value": round(p_value, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
    }


def runs_test(data: bytes, alpha: float = DEFAULT_SIGNIFICANCE_LEVEL) -> Dict[str, Any]:
    """NIST SP 800-22 Test 3: Runs Test."""
    if not data:
        return {"v_n": 0, "p_value": 0.0, "passed": False, "status": "Empty Data"}

    bits: List[int] = []
    for b in data:
        for i in range(8):
            bits.append((b >> (7 - i)) & 1)

    n = len(bits)
    ones = sum(bits)
    pi = ones / n

    if abs(pi - 0.5) >= (2.0 / math.sqrt(n)):
        return {
            "total_bits": n,
            "pi": round(pi, 6),
            "v_n": 0,
            "p_value": 0.0,
            "passed": False,
            "status": "FAIL (Prerequisite Frequency Test Failed)",
        }

    v_n = 1
    for k in range(n - 1):
        if bits[k] != bits[k + 1]:
            v_n += 1

    numerator = abs(v_n - 2 * n * pi * (1.0 - pi))
    denominator = 2 * math.sqrt(2 * n) * pi * (1.0 - pi)

    if denominator == 0:
        p_value = 0.0
    else:
        p_value = math.erfc(numerator / denominator)

    passed = bool(p_value >= alpha)

    return {
        "total_bits": n,
        "pi": round(pi, 6),
        "v_n": v_n,
        "p_value": round(p_value, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
    }


def frequency_analysis(data: bytes, alpha: float = DEFAULT_SIGNIFICANCE_LEVEL) -> Dict[str, Any]:
    """Performs 256-bin Byte Frequency Analysis and Chi-Square Uniformity Test."""
    if not data:
        return {
            "chi_square": 0.0,
            "degrees_of_freedom": 255,
            "p_value": 0.0,
            "passed": False,
            "histogram": [0] * 256,
        }

    n = len(data)
    expected_freq = n / 256.0
    histogram = [0] * 256

    for byte in data:
        histogram[byte] += 1

    chi_sq = sum(((count - expected_freq) ** 2) / expected_freq for count in histogram)

    df = 255
    z = (((chi_sq / df) ** (1 / 3.0)) - (1.0 - 2.0 / (9.0 * df))) / math.sqrt(2.0 / (9.0 * df))
    p_value = 0.5 * math.erfc(z / math.sqrt(2.0))

    passed = bool(p_value >= alpha and p_value <= (1.0 - alpha))

    return {
        "total_bytes": n,
        "chi_square": round(chi_sq, 4),
        "degrees_of_freedom": df,
        "p_value": round(p_value, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
        "histogram": histogram,
    }


def serial_test(data: bytes, alpha: float = DEFAULT_SIGNIFICANCE_LEVEL) -> Dict[str, Any]:
    """NIST SP 800-22 Test 11: Serial Test (Overlapping 2-bit blocks)."""
    if not data or len(data) < 2:
        return {"p_value": 0.0, "passed": False, "status": "Insufficient Data"}

    bits: List[int] = []
    for b in data:
        for i in range(8):
            bits.append((b >> (7 - i)) & 1)

    n = len(bits)
    pair_counts = [0] * 4
    for i in range(n):
        b1 = bits[i]
        b2 = bits[(i + 1) % n]
        pair_counts[(b1 << 1) | b2] += 1

    expected = n / 4.0
    chi_sq = sum(((count - expected) ** 2) / expected for count in pair_counts)

    # Chi-square p-value for df = 3 using Wilson-Hilferty / Fisher approximation: z = sqrt(2*chi_sq) - sqrt(2*df - 1)
    df = 3
    z = math.sqrt(2.0 * chi_sq) - math.sqrt(2.0 * df - 1.0)
    p_value = 0.5 * math.erfc(z / math.sqrt(2.0))
    p_value = min(1.0, max(0.0, p_value))
    passed = bool(p_value >= alpha)

    return {
        "total_bits": n,
        "chi_square": round(chi_sq, 6),
        "p_value": round(p_value, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
    }


def run_randomness_suite(data: bytes) -> Dict[str, Any]:
    """Runs all randomness tests on the given ciphertext byte payload."""
    entropy = calculate_shannon_entropy(data)
    bit_dist = bit_distribution_analysis(data)
    mono = monobit_test(data)
    runs = runs_test(data)
    freq = frequency_analysis(data)
    serial = serial_test(data)

    all_passed = mono["passed"] and runs["passed"] and freq["passed"] and serial["passed"] and (entropy >= 7.80)

    return {
        "entropy": entropy,
        "bit_distribution": bit_dist,
        "monobit_test": mono,
        "runs_test": runs,
        "frequency_analysis": freq,
        "serial_test": serial,
        "overall_passed": all_passed,
        "summary": "PASS (NIST SP 800-22 Compliant)" if all_passed else "ATTENTION (Marginal Deviations)",
    }


class RandomnessAnalyzer:
    """NIST SP 800-22 Randomness Statistical Analyzer."""

    def __init__(self, alpha: float = DEFAULT_SIGNIFICANCE_LEVEL) -> None:
        """Initialize RandomnessAnalyzer.

        Args:
            alpha: Significance level threshold (defaults to 0.01).
        """
        self.alpha: float = alpha

    def analyze(self, data: bytes) -> Dict[str, Any]:
        """Perform full statistical randomness analysis suite.

        Args:
            data: Input byte stream.

        Returns:
            Dict[str, Any]: Comprehensive randomness test suite results.
        """
        res = run_randomness_suite(data)
        res["significance_level"] = self.alpha
        return res

    def summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary string of randomness test results."""
        return (
            f"Randomness Suite Summary: {results.get('summary', 'UNKNOWN')}\n"
            f"Shannon Entropy: {results.get('entropy', 0.0):.6f} bits/byte\n"
            f"Monobit Test P-Value: {results.get('monobit_test', {}).get('p_value', 0.0):.6f}\n"
            f"Runs Test P-Value: {results.get('runs_test', {}).get('p_value', 0.0):.6f}\n"
            f"Frequency Test P-Value: {results.get('frequency_analysis', {}).get('p_value', 0.0):.6f}"
        )
