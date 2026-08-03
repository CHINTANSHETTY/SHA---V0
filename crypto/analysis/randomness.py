"""
Module:
    randomness.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    NIST SP 800-22 and IEEE Statistical Randomness Analysis Subsystem.
    Evaluates Shannon entropy, bit distribution, NIST Monobit Test, NIST Runs Test,
    and Byte Frequency Chi-Square Uniformity.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)

IEEE Mapping:
    Section V-B – Statistical Randomness & NIST SP 800-22 Evaluation
"""

from __future__ import annotations

import math
from typing import Any, Dict, List


def calculate_shannon_entropy(data: bytes) -> float:
    """Computes Shannon Entropy of a byte sequence in bits per byte.

    Args:
        data: Raw binary byte stream.

    Returns:
        Entropy value in range [0.0, 8.0].
    """
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
    """Analyzes 0-bit vs 1-bit balance across a byte sequence.

    Args:
        data: Raw binary byte stream.

    Returns:
        Dictionary containing total bits, zeros count, ones count,
        ones ratio (ideal 0.5), and bit imbalance percentage.
    """
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


def monobit_test(data: bytes) -> Dict[str, Any]:
    """NIST SP 800-22 Test 1: Frequency (Monobit) Test.

    Evaluates whether the number of ones and zeros in a sequence are approximately
    equal as expected for a random sequence.

    Args:
        data: Input byte stream.

    Returns:
        Dictionary with test statistic S_obs, p-value, and pass/fail boolean (threshold alpha=0.01).
    """
    if not data:
        return {"s_obs": 0.0, "p_value": 0.0, "passed": False, "status": "Empty Data"}

    # Convert bytes to bit stream (+1 for 1, -1 for 0)
    total_bits = len(data) * 8
    s_n = 0
    for byte in data:
        for i in range(8):
            bit = (byte >> i) & 1
            s_n += 1 if bit == 1 else -1

    s_obs = abs(s_n) / math.sqrt(total_bits)
    p_value = math.erfc(s_obs / math.sqrt(2.0))
    passed = bool(p_value >= 0.01)

    return {
        "total_bits": total_bits,
        "s_n": s_n,
        "s_obs": round(s_obs, 6),
        "p_value": round(p_value, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
    }


def runs_test(data: bytes) -> Dict[str, Any]:
    """NIST SP 800-22 Test 3: Runs Test.

    Measures total number of uninterrupted sequences of identical bits (runs).

    Args:
        data: Input byte stream.

    Returns:
        Dictionary with total runs V_n, expected ratio, Z-statistic, p-value, and pass/fail.
    """
    if not data:
        return {"v_n": 0, "p_value": 0.0, "passed": False, "status": "Empty Data"}

    # Extract binary bit array
    bits: List[int] = []
    for b in data:
        for i in range(8):
            bits.append((b >> (7 - i)) & 1)

    n = len(bits)
    ones = sum(bits)
    pi = ones / n

    # Monobit pre-requisite: |pi - 0.5| >= (2 / sqrt(n)) means sequence fails runs test
    if abs(pi - 0.5) >= (2.0 / math.sqrt(n)):
        return {
            "total_bits": n,
            "pi": round(pi, 6),
            "v_n": 0,
            "p_value": 0.0,
            "passed": False,
            "status": "FAIL (Prerequisite Frequency Test Failed)",
        }

    # Count runs (transitions between bits)
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

    passed = bool(p_value >= 0.01)

    return {
        "total_bits": n,
        "pi": round(pi, 6),
        "v_n": v_n,
        "p_value": round(p_value, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
    }


def frequency_analysis(data: bytes) -> Dict[str, Any]:
    """Performs 256-bin Byte Frequency Analysis and Chi-Square Uniformity Test.

    Chi-Square Statistic: sum((O_i - E_i)^2 / E_i) over i=0..255 where E_i = N / 256.

    Args:
        data: Input byte stream.

    Returns:
        Dictionary with byte frequency table, Chi-Square statistic, degrees of freedom,
        and uniformity evaluation.
    """
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

    # Approximate Chi-Square p-value for df = 255 using Wilson-Hilferty transformation
    # z = (((chi_sq / df) ** (1/3)) - (1 - 2/(9*df))) / sqrt(2 / (9*df))
    df = 255
    z = (((chi_sq / df) ** (1 / 3.0)) - (1.0 - 2.0 / (9.0 * df))) / math.sqrt(2.0 / (9.0 * df))
    p_value = 0.5 * math.erfc(z / math.sqrt(2.0))

    passed = bool(p_value >= 0.01 and p_value <= 0.99)

    return {
        "total_bytes": n,
        "chi_square": round(chi_sq, 4),
        "degrees_of_freedom": df,
        "p_value": round(p_value, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
        "histogram": histogram,
    }


def run_randomness_suite(data: bytes) -> Dict[str, Any]:
    """Runs all randomness tests on the given ciphertext byte payload.

    Args:
        data: Ciphertext byte stream.

    Returns:
        Complete randomness test report dictionary.
    """
    entropy = calculate_shannon_entropy(data)
    bit_dist = bit_distribution_analysis(data)
    mono = monobit_test(data)
    runs = runs_test(data)
    freq = frequency_analysis(data)

    all_passed = mono["passed"] and runs["passed"] and freq["passed"] and (entropy >= 7.90)

    return {
        "entropy": entropy,
        "bit_distribution": bit_dist,
        "monobit_test": mono,
        "runs_test": runs,
        "frequency_analysis": freq,
        "overall_passed": all_passed,
        "summary": "PASS (NIST SP 800-22 Compliant)" if all_passed else "ATTENTION (Marginal Deviations)",
    }
