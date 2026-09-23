"""Unit tests for Cellular Automata Rule Engine (crypto/ca/rules.py)."""

import pytest
from types import MappingProxyType

from crypto.ca.rules import (
    MIN_RULE,
    MAX_RULE,
    VALID_BITS,
    validate_rule,
    parse_rule,
    rule_to_binary,
    get_neighborhood_output,
)


class TestRuleValidation:
    """Tests for validate_rule function."""

    @pytest.mark.parametrize("rule", [0, 1, 30, 90, 110, 150, 254, 255])
    def test_valid_rules(self, rule):
        """Verify that valid integer rules between 0 and 255 are accepted."""
        assert validate_rule(rule) == rule

    @pytest.mark.parametrize("invalid_rule", [-1, -100, 256, 1000])
    def test_out_of_bounds_rules(self, invalid_rule):
        """Verify that integer rules outside [0, 255] raise ValueError."""
        with pytest.raises(ValueError, match="Rule must be between 0 and 255"):
            validate_rule(invalid_rule)

    @pytest.mark.parametrize(
        "invalid_type_rule",
        [30.0, "30", None, True, False, [30], (30,), {"rule": 30}],
    )
    def test_invalid_rule_types(self, invalid_type_rule):
        """Verify that non-integer types (including bool, float, str, None) raise TypeError."""
        with pytest.raises(TypeError, match="Rule must be an integer"):
            validate_rule(invalid_type_rule)


class TestRuleParsing:
    """Tests for parse_rule function."""

    def test_rule_0_table(self):
        """Verify Rule 0 produces all zeros lookup table."""
        table = parse_rule(0)
        assert len(table) == 8
        for key in table:
            assert table[key] == 0

    def test_rule_255_table(self):
        """Verify Rule 255 produces all ones lookup table."""
        table = parse_rule(255)
        assert len(table) == 8
        for key in table:
            assert table[key] == 1

    def test_rule_30_table(self):
        """Verify Rule 30 (00011110 binary) truth table."""
        table = parse_rule(30)
        expected = {
            (1, 1, 1): 0,  # bit 7
            (1, 1, 0): 0,  # bit 6
            (1, 0, 1): 0,  # bit 5
            (1, 0, 0): 1,  # bit 4
            (0, 1, 1): 1,  # bit 3
            (0, 1, 0): 1,  # bit 2
            (0, 0, 1): 1,  # bit 1
            (0, 0, 0): 0,  # bit 0
        }
        for neighborhood, expected_bit in expected.items():
            assert table[neighborhood] == expected_bit

    def test_rule_90_table(self):
        """Verify Rule 90 (01011010 binary) XOR truth table."""
        table = parse_rule(90)
        for (left, center, right), output in table.items():
            # Rule 90 output is Left XOR Right
            assert output == (left ^ right)

    def test_lookup_table_immutability(self):
        """Verify that returned lookup table is immutable and cannot be mutated."""
        table = parse_rule(30)
        assert isinstance(table, MappingProxyType)
        with pytest.raises(TypeError):
            table[(1, 1, 1)] = 1

    def test_parse_rule_caching(self):
        """Verify that repeated parse_rule calls use cached lookup table."""
        table1 = parse_rule(30)
        table2 = parse_rule(30)
        assert table1 is table2


class TestRuleToBinary:
    """Tests for rule_to_binary function."""

    def test_binary_string_conversion(self):
        """Verify 8-bit binary string representation for rules."""
        assert rule_to_binary(0) == "00000000"
        assert rule_to_binary(30) == "00011110"
        assert rule_to_binary(90) == "01011010"
        assert rule_to_binary(110) == "01101110"
        assert rule_to_binary(255) == "11111111"

    def test_invalid_rule_binary_conversion(self):
        """Verify invalid inputs raise error in rule_to_binary."""
        with pytest.raises(ValueError):
            rule_to_binary(256)
        with pytest.raises(TypeError):
            rule_to_binary("30")


class TestNeighborhoodOutput:
    """Tests for get_neighborhood_output function."""

    def test_valid_neighborhood_evaluation(self):
        """Verify neighborhood outputs under Rule 30."""
        assert get_neighborhood_output(30, 1, 0, 0) == 1
        assert get_neighborhood_output(30, 0, 1, 1) == 1
        assert get_neighborhood_output(30, 1, 1, 1) == 0
        assert get_neighborhood_output(30, 0, 0, 0) == 0

    @pytest.mark.parametrize("invalid_cell", [2, -1, 10, "1", 1.0, True])
    def test_invalid_neighborhood_cells(self, invalid_cell):
        """Verify invalid cell values raise TypeError or ValueError."""
        with pytest.raises((TypeError, ValueError)):
            get_neighborhood_output(30, invalid_cell, 0, 0)
        with pytest.raises((TypeError, ValueError)):
            get_neighborhood_output(30, 0, invalid_cell, 0)
        with pytest.raises((TypeError, ValueError)):
            get_neighborhood_output(30, 0, 0, invalid_cell)
