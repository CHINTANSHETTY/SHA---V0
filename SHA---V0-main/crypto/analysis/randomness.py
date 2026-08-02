"""
Randomness Analysis Module for KDR-CA-AEAD.

Provides statistical tests including Runs Test and autocorrelation analysis for CA binary sequences.
"""

from typing import Any, Dict
from crypto.analysis.entropy import validate_sequence


def runs_test(bits: Any) -> Dict[str, Any]:
    """
    Performs a Runs Test on a binary sequence.

    A run is a maximal contiguous sequence of identical bits.

    Args:
        bits: Binary state vector.

    Returns:
        Dictionary with keys 'runs', 'longest_run', 'average_run', 'zero_runs', 'one_runs'.
    """
    valid_bits = validate_sequence(bits)
    total_len = len(valid_bits)

    zero_runs = 0
    one_runs = 0
    current_bit = None
    current_run_len = 0
    longest_run = 0
    run_lengths = []

    for b in valid_bits:
        if b != current_bit:
            if current_bit is not None:
                run_lengths.append(current_run_len)
                if current_run_len > longest_run:
                    longest_run = current_run_len
            current_bit = b
            current_run_len = 1
            if b == 0:
                zero_runs += 1
            else:
                one_runs += 1
        else:
            current_run_len += 1

    if current_run_len > 0:
        run_lengths.append(current_run_len)
        if current_run_len > longest_run:
            longest_run = current_run_len

    total_runs = zero_runs + one_runs
    avg_run = round(total_len / total_runs, 10) if total_runs > 0 else 0.0

    return {
        "runs": total_runs,
        "longest_run": longest_run,
        "average_run": avg_run,
        "zero_runs": zero_runs,
        "one_runs": one_runs,
    }
