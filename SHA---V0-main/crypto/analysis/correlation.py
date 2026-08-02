"""
Correlation Analysis Module for KDR-CA-AEAD.

Computes Pearson correlation coefficient between binary sequences and autocorrelation at specified lags.
"""

import math
from typing import Any
from crypto.analysis.entropy import validate_sequence
from crypto.analysis.exceptions import ComparisonError


def correlation(bits1: Any, bits2: Any) -> float:
    """
    Computes the Pearson correlation coefficient r between two equal-length binary sequences.

    Range: -1.0 <= r <= 1.0. Zero variance edge cases return 0.0.

    Args:
        bits1: First binary sequence.
        bits2: Second binary sequence.

    Returns:
        Pearson correlation coefficient float in [-1.0, 1.0].

    Raises:
        ComparisonError: If sequence lengths differ.
    """
    vbits1 = validate_sequence(bits1)
    vbits2 = validate_sequence(bits2)

    if len(vbits1) != len(vbits2):
        raise ComparisonError(
            f"Sequence lengths must be equal for correlation: {len(vbits1)} != {len(vbits2)}"
        )

    n = len(vbits1)
    if n == 0:
        return 0.0

    mean1 = sum(vbits1) / n
    mean2 = sum(vbits2) / n

    num = sum((x - mean1) * (y - mean2) for x, y in zip(vbits1, vbits2))
    den1 = sum((x - mean1) ** 2 for x in vbits1)
    den2 = sum((y - mean2) ** 2 for y in vbits2)

    denom = math.sqrt(den1 * den2)
    if denom == 0.0:
        return 0.0

    return round(num / denom, 10)


def pearson_correlation(bits1: Any, bits2: Any) -> float:
    """Alias for correlation."""
    return correlation(bits1, bits2)


def autocorrelation(bits: Any, lag: int = 1) -> float:
    """
    Computes the normalized autocorrelation coefficient for a binary sequence at a given lag.

    Bits are mapped to +1 (for 1) and -1 (for 0).

    Args:
        bits: Binary state vector.
        lag: Shift/lag integer d (1 <= lag < len(bits)). Default is 1.

    Returns:
        Normalized autocorrelation coefficient float in [-1.0, 1.0].
    """
    valid_bits = validate_sequence(bits)
    n = len(valid_bits)

    if isinstance(lag, bool) or not isinstance(lag, int):
        raise TypeError(f"Lag must be an integer, got {type(lag).__name__}")
    if not (1 <= lag < n):
        raise ValueError(f"Lag must be in range [1, {n - 1}], got {lag}")

    x = [1.0 if b == 1 else -1.0 for b in valid_bits]
    cov = sum(x[i] * x[i + lag] for i in range(n - lag))
    return round(cov / (n - lag), 10)
