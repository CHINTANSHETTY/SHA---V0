"""
Entropy Analysis Module for KDR-CA-AEAD.

Provides information-theoretic metrics including Shannon Entropy, bit frequency,
and probability distribution calculations for binary state vectors.
"""

import math
from typing import Any, Dict
from crypto.ca.utils import validate_binary_state


def probability_distribution(bits: Any) -> Dict[int, float]:
    """
    Computes the empirical probability distribution p(x) for x in {0, 1}.

    Args:
        bits: Binary state vector (list/tuple of 0/1 or bit string).

    Returns:
        Dictionary mapping bit values 0 and 1 to their respective probabilities.

    Raises:
        TypeError: If bits is not an iterable or contains invalid types.
        ValueError: If bits is empty or contains non-binary elements.
    """
    valid_bits = validate_binary_state(bits)
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

    Raises:
        TypeError: If bits is not an iterable or contains invalid types.
        ValueError: If bits is empty or contains non-binary elements.
    """
    valid_bits = validate_binary_state(bits)
    total = len(valid_bits)
    ones = sum(valid_bits)
    zeros = total - ones

    return {
        "zeros": zeros,
        "ones": ones,
        "zero_ratio": zeros / total,
        "one_ratio": ones / total,
    }


def shannon_entropy(bits: Any) -> float:
    """
    Calculates the Shannon Entropy H(X) of a binary sequence in bits.

    Formula:
        H(X) = - sum_{x in {0, 1}} p(x) * log2(p(x))

    For binary sequences, 0.0 <= H(X) <= 1.0, where 1.0 represents maximal entropy.

    Args:
        bits: Binary state vector.

    Returns:
        Shannon entropy value as a float in [0.0, 1.0].

    Raises:
        TypeError: If bits is not an iterable or contains invalid types.
        ValueError: If bits is empty or contains non-binary elements.
    """
    dist = probability_distribution(bits)
    entropy = 0.0

    for prob in dist.values():
        if prob > 0.0:
            entropy -= prob * math.log2(prob)

    # Round slightly to handle floating-point precision artifacts near 0.0 or 1.0
    return round(entropy, 10)
