"""
Entropy Analysis Module for KDR-CA-AEAD.

Provides information-theoretic metrics including Shannon Entropy H(X), bit frequency,
and probability distribution calculations for binary state vectors.
"""

import math
from typing import Any, Dict, List
from crypto.analysis.exceptions import InvalidSequenceError


def validate_sequence(bits: Any) -> List[int]:
    """
    Validates and normalizes binary input sequence (list, tuple, or binary string).

    Args:
        bits: Input binary sequence.

    Returns:
        List of bit integers (0 or 1).

    Raises:
        TypeError: If bits is not iterable sequence or contains invalid types.
        InvalidSequenceError: If bits sequence is empty or contains non-binary elements.
    """
    if bits is None:
        raise TypeError("Sequence cannot be None")

    if isinstance(bits, str):
        if not bits:
            raise InvalidSequenceError("Sequence string cannot be empty")
        for c in bits:
            if c not in ("0", "1"):
                raise InvalidSequenceError(f"Invalid binary character '{c}' in sequence")
        return [int(c) for c in bits]

    if not isinstance(bits, (list, tuple)):
        raise TypeError(f"Sequence must be list, tuple, or string, got {type(bits).__name__}")

    if len(bits) == 0:
        raise InvalidSequenceError("Sequence cannot be empty")

    normalized = []
    for elem in bits:
        if isinstance(elem, bool) or not isinstance(elem, int):
            raise TypeError(f"Sequence element must be int, got {type(elem).__name__}")
        if elem not in (0, 1):
            raise InvalidSequenceError(f"Sequence element must be 0 or 1, got {elem}")
        normalized.append(elem)

    return normalized


def probability_distribution(bits: Any) -> Dict[int, float]:
    """
    Computes empirical probability distribution p(x) for x in {0, 1}.

    Args:
        bits: Binary state vector.

    Returns:
        Dictionary mapping bit values 0 and 1 to probabilities.
    """
    valid_bits = validate_sequence(bits)
    total = len(valid_bits)
    ones = sum(valid_bits)
    zeros = total - ones

    return {
        0: zeros / total,
        1: ones / total,
    }


def bit_frequency(bits: Any) -> Dict[str, Any]:
    """
    Computes the counts and ratios of zeros and ones in a binary sequence.

    Args:
        bits: Binary state vector.

    Returns:
        Dictionary with keys 'zeros', 'ones', 'zero_ratio', 'one_ratio'.
    """
    valid_bits = validate_sequence(bits)
    total = len(valid_bits)
    ones = sum(valid_bits)
    zeros = total - ones

    return {
        "zeros": zeros,
        "ones": ones,
        "zero_ratio": zeros / total,
        "one_ratio": ones / total,
    }


def calculate_entropy(bits: Any) -> float:
    """
    Calculates the Shannon Entropy H(X) of a binary sequence in bits.

    Formula: H(X) = - sum_{x in {0, 1}} p(x) * log2(p(x))

    Args:
        bits: Binary state vector.

    Returns:
        Shannon entropy float in [0.0, 1.0].
    """
    dist = probability_distribution(bits)
    entropy = 0.0

    for prob in dist.values():
        if prob > 0.0:
            entropy -= prob * math.log2(prob)

    return round(entropy, 10)


def shannon_entropy(bits: Any) -> float:
    """Alias for calculate_entropy."""
    return calculate_entropy(bits)
