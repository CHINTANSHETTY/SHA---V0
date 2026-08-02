"""
Randomness Analysis Module for KDR-CA-AEAD.

Provides statistical tests including Runs Test, Autocorrelation, Hamming Distance,
and Avalanche Effect measurement for evaluating CA-generated binary sequences.
"""

from typing import Any, Dict
from crypto.ca.utils import validate_binary_state


def runs_test(bits: Any) -> Dict[str, int]:
    """
    Performs a Runs Test on a binary sequence.

    A run is defined as a maximal contiguous sequence of identical bits.

    Args:
        bits: Binary state vector (list/tuple of 0/1 or bit string).

    Returns:
        Dictionary with keys 'runs', 'zero_runs', 'one_runs'.

    Raises:
        TypeError: If bits is not an iterable or contains invalid types.
        ValueError: If bits is empty or contains non-binary elements.
    """
    valid_bits = validate_binary_state(bits)

    zero_runs = 0
    one_runs = 0
    current_bit = None

    for b in valid_bits:
        if b != current_bit:
            current_bit = b
            if b == 0:
                zero_runs += 1
            else:
                one_runs += 1

    total_runs = zero_runs + one_runs

    return {
        "runs": total_runs,
        "zero_runs": zero_runs,
        "one_runs": one_runs,
    }


def hamming_distance(bits1: Any, bits2: Any) -> int:
    """
    Calculates the Hamming distance between two equal-length binary sequences.

    The Hamming distance is the number of bit positions in which bits1 and bits2 differ.

    Args:
        bits1: First binary state vector.
        bits2: Second binary state vector.

    Returns:
        Integer count of differing bit positions.

    Raises:
        TypeError: If either input is not an iterable or contains invalid types.
        ValueError: If either input is empty or sequences have unequal lengths.
    """
    vbits1 = validate_binary_state(bits1)
    vbits2 = validate_binary_state(bits2)

    if len(vbits1) != len(vbits2):
        raise ValueError(
            f"Sequence lengths must be equal for Hamming distance: {len(vbits1)} != {len(vbits2)}"
        )

    return sum(b1 != b2 for b1, b2 in zip(vbits1, vbits2))


def avalanche_effect(bits1: Any, bits2: Any) -> float:
    """
    Calculates the Avalanche Effect ratio between two equal-length binary sequences.

    Ratio = Hamming Distance / Total Bits
    Ideal cryptographic avalanche ratio is approximately 0.5.

    Args:
        bits1: Original binary state vector.
        bits2: Transformed binary state vector.

    Returns:
        Float ratio in range [0.0, 1.0].

    Raises:
        TypeError: If inputs are invalid types.
        ValueError: If inputs are empty or have unequal lengths.
    """
    dist = hamming_distance(bits1, bits2)
    vbits1 = validate_binary_state(bits1)
    return round(dist / len(vbits1), 10)


def autocorrelation(bits: Any, lag: int = 1) -> float:
    """
    Computes the normalized autocorrelation coefficient for a binary sequence at a given lag.

    Bits are mapped to +1 (for 1) and -1 (for 0).
    A(d) = (1 / (N - d)) * sum_{i=0}^{N - 1 - d} X_i * X_{i+d}

    Args:
        bits: Binary state vector.
        lag: Shift/lag integer d (must be 1 <= lag < len(bits)). Default is 1.

    Returns:
        Normalized autocorrelation coefficient as a float in [-1.0, 1.0].

    Raises:
        TypeError: If bits is invalid or lag is not an integer.
        ValueError: If bits is empty or lag is out of range [1, N-1].
    """
    valid_bits = validate_binary_state(bits)
    n = len(valid_bits)

    if isinstance(lag, bool) or not isinstance(lag, int):
        raise TypeError(f"Lag must be an integer, got {type(lag).__name__}")
    if not (1 <= lag < n):
        raise ValueError(f"Lag must be in range [1, {n - 1}], got {lag}")

    # Map {0, 1} to {-1, +1}
    x = [1.0 if b == 1 else -1.0 for b in valid_bits]

    cov = sum(x[i] * x[i + lag] for i in range(n - lag))
    return round(cov / (n - lag), 10)
