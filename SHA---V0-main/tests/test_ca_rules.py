"""
Unit tests for Cellular Automata Rule Definitions (crypto/ca/rules.py).
"""

import pytest
from crypto.ca.rules import apply_rule, get_rule_truth_table, validate_rule_number


class TestCARules:
    """Test suite for CA rule definitions and application."""

    def test_rule_30_truth_table(self):
        """Verify Rule 30 produces exact Wolfram neighborhood mappings."""
        # Rule 30 binary = 00011110 (30)
        expected = {
            (1, 1, 1): 0,
            (1, 1, 0): 0,
            (1, 0, 1): 0,
            (1, 0, 0): 1,
            (0, 1, 1): 1,
            (0, 1, 0): 1,
            (0, 0, 1): 1,
            (0, 0, 0): 0,
        }
        for (l, c, r), bit in expected.items():
            assert apply_rule(30, l, c, r) == bit

    def test_rule_90_truth_table(self):
        """Verify Rule 90 (left XOR right) truth table."""
        # Rule 90 binary = 01011010 (90)
        for l in (0, 1):
            for c in (0, 1):
                for r in (0, 1):
                    assert apply_rule(90, l, c, r) == (l ^ r)

    def test_rule_110_truth_table(self):
        """Verify Rule 110 truth table."""
        # Rule 110 binary = 01101110 (110)
        expected = {
            (1, 1, 1): 0,
            (1, 1, 0): 1,
            (1, 0, 1): 1,
            (1, 0, 0): 0,
            (0, 1, 1): 1,
            (0, 1, 0): 1,
            (0, 0, 1): 1,
            (0, 0, 0): 0,
        }
        for (l, c, r), bit in expected.items():
            assert apply_rule(110, l, c, r) == bit

    def test_rule_150_truth_table(self):
        """Verify Rule 150 (left XOR center XOR right) truth table."""
        # Rule 150 binary = 10010110 (150)
        for l in (0, 1):
            for c in (0, 0):
                for r in (0, 1):
                    assert apply_rule(150, l, c, r) == (l ^ c ^ r)

    def test_get_rule_truth_table(self):
        """Verify get_rule_truth_table returns full 8-neighborhood dictionary."""
        table = get_rule_truth_table(30)
        assert len(table) == 8
        assert table[(1, 0, 0)] == 1
        assert table[(1, 1, 1)] == 0

    def test_validate_rule_number_valid(self):
        """Verify valid rule numbers pass validation."""
        assert validate_rule_number(0) == 0
        assert validate_rule_number(128) == 128
        assert validate_rule_number(255) == 255

    def test_validate_rule_number_out_of_range(self):
        """Verify invalid rule numbers raise ValueError."""
        with pytest.raises(ValueError, match="Rule number must be in range"):
            validate_rule_number(-1)

        with pytest.raises(ValueError, match="Rule number must be in range"):
            validate_rule_number(256)

    def test_validate_rule_number_invalid_type(self):
        """Verify non-integer rule numbers raise TypeError."""
        with pytest.raises(TypeError, match="Rule number must be an integer"):
            validate_rule_number(30.5)  # type: ignore

        with pytest.raises(TypeError, match="Rule number must be an integer"):
            validate_rule_number("30")  # type: ignore

        with pytest.raises(TypeError, match="Rule number must be an integer"):
            validate_rule_number(True)  # type: ignore

    def test_apply_rule_invalid_neighborhood_bits(self):
        """Verify invalid neighborhood bit values raise appropriate exceptions."""
        with pytest.raises(ValueError, match="must be 0 or 1"):
            apply_rule(30, 2, 0, 0)

        with pytest.raises(TypeError, match="must be an integer"):
            apply_rule(30, 0, "1", 0)  # type: ignore

        with pytest.raises(TypeError, match="must be an integer"):
            apply_rule(30, 0, 1, True)  # type: ignore
