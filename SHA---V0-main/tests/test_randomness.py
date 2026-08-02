"""
Unit tests for Randomness Analysis Module (crypto/analysis/randomness.py).
"""

import pytest
from crypto.analysis import runs_test


class TestRandomnessAnalysis:
    """Test suite for functions in crypto/analysis/randomness.py."""

    def test_single_run(self):
        """Verify single run sequence (e.g. all 1s)."""
        bits = [1, 1, 1, 1, 1]
        res = runs_test(bits)
        assert res["runs"] == 1
        assert res["longest_run"] == 5
        assert res["average_run"] == 5.0
        assert res["one_runs"] == 1
        assert res["zero_runs"] == 0

    def test_alternating_runs(self):
        """Verify alternating sequence (e.g. 010101)."""
        bits = [0, 1, 0, 1, 0, 1]
        res = runs_test(bits)
        assert res["runs"] == 6
        assert res["longest_run"] == 1
        assert res["average_run"] == 1.0
        assert res["zero_runs"] == 3
        assert res["one_runs"] == 3

    def test_random_runs_pattern(self):
        """Verify multi-bit run patterns (e.g., 000 11 0 1111)."""
        bits = [0, 0, 0, 1, 1, 0, 1, 1, 1, 1]
        res = runs_test(bits)
        assert res["runs"] == 4  # 000, 11, 0, 1111
        assert res["longest_run"] == 4
        assert res["average_run"] == 2.5
        assert res["zero_runs"] == 2
        assert res["one_runs"] == 2

    def test_binary_string_runs(self):
        """Verify runs_test accepts binary string input."""
        res = runs_test("110001111")
        assert res["runs"] == 3  # 11, 000, 1111
        assert res["longest_run"] == 4
