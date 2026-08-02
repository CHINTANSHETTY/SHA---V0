"""
Avalanche Effect Analysis Module for KDR-CA-AEAD.

Calculates Hamming Distance and percentage bit difference (Avalanche Effect) between binary sequences.
"""

from typing import Any, Dict
from crypto.analysis.entropy import validate_sequence
from crypto.analysis.exceptions import ComparisonError


def hamming_distance(bits1: Any, bits2: Any) -> int:
    """
    Calculates the Hamming distance between two equal-length binary sequences.

    Args:
        bits1: First binary sequence.
        bits2: Second binary sequence.

    Returns:
        Integer count of differing bit positions.

    Raises:
        ComparisonError: If sequence lengths differ.
    """
    vbits1 = validate_sequence(bits1)
    vbits2 = validate_sequence(bits2)

    if len(vbits1) != len(vbits2):
        raise ComparisonError(
            f"Sequence lengths must be equal for Hamming distance: {len(vbits1)} != {len(vbits2)}"
        )

    return sum(b1 != b2 for b1, b2 in zip(vbits1, vbits2))


def calculate_avalanche(bits1: Any, bits2: Any) -> Dict[str, float]:
    """
    Calculates the Avalanche Effect metrics between two equal-length binary sequences.

    Args:
        bits1: Original binary state vector.
        bits2: Transformed binary state vector.

    Returns:
        Dictionary with keys 'distance' and 'percentage'.
    """
    dist = hamming_distance(bits1, bits2)
    vbits1 = validate_sequence(bits1)
    length = len(vbits1)
    percentage = round((dist / length) * 100.0, 10)

    return {
        "distance": dist,
        "percentage": percentage,
    }


def avalanche_effect(bits1: Any, bits2: Any) -> float:
    """
    Calculates the Avalanche Effect ratio (0.0 to 1.0) between two binary sequences.

    Returns:
        Float ratio in range [0.0, 1.0].
    """
    res = calculate_avalanche(bits1, bits2)
    return round(res["percentage"] / 100.0, 10)
