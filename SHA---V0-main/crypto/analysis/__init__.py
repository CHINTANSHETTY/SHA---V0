"""
Randomness & Entropy Analysis Package for KDR-CA-AEAD.
"""

from crypto.analysis.entropy import (
    bit_frequency,
    probability_distribution,
    shannon_entropy,
)
from crypto.analysis.randomness import (
    autocorrelation,
    avalanche_effect,
    hamming_distance,
    runs_test,
)

__all__ = [
    "shannon_entropy",
    "bit_frequency",
    "probability_distribution",
    "runs_test",
    "autocorrelation",
    "avalanche_effect",
    "hamming_distance",
]
