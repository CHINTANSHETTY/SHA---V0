"""
Custom Exception Classes for Randomness and Entropy Analysis Module.
"""


class AnalysisError(Exception):
    """Base exception class for analysis module errors."""
    pass


class InvalidSequenceError(AnalysisError, ValueError):
    """Raised when an invalid binary state sequence is provided."""
    pass


class ComparisonError(AnalysisError, ValueError):
    """Raised when comparing incompatible sequences (e.g., unequal length)."""
    pass
