"""
Statistical Report Generator Module for KDR-CA-AEAD.

Aggregates entropy, bit frequency, and runs test metrics into structured reports and JSON exports.
"""

import json
from typing import Any, Dict
from crypto.analysis.entropy import bit_frequency, calculate_entropy, validate_sequence
from crypto.analysis.randomness import runs_test


class AnalysisReport:
    """Statistical Report Generator for CA Binary Bitstreams."""

    def __init__(self) -> None:
        self._report_data: Dict[str, Any] = {}

    def generate(self, bits: Any) -> Dict[str, Any]:
        """
        Generates statistical metrics report for a binary sequence.

        Args:
            bits: Binary sequence (list, tuple, or binary string).

        Returns:
            Dictionary containing 'entropy', 'frequency', 'runs', and 'length'.
        """
        valid_bits = validate_sequence(bits)

        self._report_data = {
            "entropy": calculate_entropy(valid_bits),
            "frequency": bit_frequency(valid_bits),
            "runs": runs_test(valid_bits),
            "length": len(valid_bits),
        }
        return dict(self._report_data)

    def summary(self) -> str:
        """
        Generates a human-readable text summary of the statistical analysis.

        Returns:
            Formatted summary text string.
        """
        if not self._report_data:
            return "No analysis report generated yet."

        freq = self._report_data["frequency"]
        runs = self._report_data["runs"]
        entropy = self._report_data["entropy"]
        length = self._report_data["length"]

        return (
            f"=== Statistical Analysis Report ===\n"
            f"Sequence Length: {length} bits\n"
            f"Shannon Entropy: {entropy:.6f} bits/bit\n"
            f"Bit Frequency  : 0s={freq['zeros']} ({freq['zero_ratio']:.2%}), 1s={freq['ones']} ({freq['one_ratio']:.2%})\n"
            f"Runs Test      : Total={runs['runs']}, Longest={runs['longest_run']}, Avg Length={runs['average_run']:.2f}\n"
            f"==================================="
        )

    def export_dict(self) -> Dict[str, Any]:
        """Returns a copy of the generated report dictionary."""
        return dict(self._report_data)

    def export_json(self) -> str:
        """Exports the generated report as a formatted JSON string."""
        return json.dumps(self._report_data, indent=2)
