"""
Randomness & Entropy Analysis Package for KDR-CA-AEAD.
"""

from crypto.analysis.avalanche import avalanche_effect, calculate_avalanche, hamming_distance
from crypto.analysis.correlation import autocorrelation, correlation, pearson_correlation
from crypto.analysis.entropy import (
    bit_frequency,
    calculate_entropy,
    probability_distribution,
    shannon_entropy,
    validate_sequence,
)
from crypto.analysis.exceptions import AnalysisError, ComparisonError, InvalidSequenceError
from crypto.analysis.randomness import runs_test
from crypto.analysis.report import AnalysisReport

__all__ = [
    "calculate_entropy",
    "shannon_entropy",
    "bit_frequency",
    "probability_distribution",
    "validate_sequence",
    "runs_test",
    "autocorrelation",
    "avalanche_effect",
    "calculate_avalanche",
    "hamming_distance",
    "correlation",
    "pearson_correlation",
    "AnalysisReport",
    "AnalysisError",
    "InvalidSequenceError",
    "ComparisonError",
]
