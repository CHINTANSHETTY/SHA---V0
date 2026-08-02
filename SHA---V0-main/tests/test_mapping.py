"""
Unit tests for Rule Mapping module (crypto/scheduler/mapping.py).
"""

import pytest
from crypto.scheduler.mapping import map_byte_to_rule, map_bytes_to_rules, validate_rule


class TestRuleMapping:
    """Test suite for mapping functions in crypto/scheduler/mapping.py."""

    def test_map_byte_to_rule_valid(self):
        """Verify byte values map to identical Wolfram rule numbers in [0, 255]."""
        assert map_byte_to_rule(0) == 0
        assert map_byte_to_rule(30) == 30
        assert map_byte_to_rule(128) == 128
        assert map_byte_to_rule(255) == 255

    def test_map_byte_to_rule_out_of_bounds(self):
        """Verify values outside [0, 255] raise ValueError."""
        with pytest.raises(ValueError, match="must be in range"):
            map_byte_to_rule(-1)

        with pytest.raises(ValueError, match="must be in range"):
            map_byte_to_rule(256)

    def test_map_byte_to_rule_invalid_types(self):
        """Verify non-integer inputs raise TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            map_byte_to_rule("30")  # type: ignore

        with pytest.raises(TypeError, match="must be an integer"):
            map_byte_to_rule(30.5)  # type: ignore

        with pytest.raises(TypeError, match="must be an integer"):
            map_byte_to_rule(True)  # type: ignore

    def test_map_bytes_to_rules_valid(self):
        """Verify mapping byte sequences into lists of rule numbers."""
        data = b"\x00\x1e\x5a\x6e\x96"  # 0, 30, 90, 110, 150
        rules = map_bytes_to_rules(data)
        assert rules == [0, 30, 90, 110, 150]

    def test_map_bytes_to_rules_empty(self):
        """Verify empty byte sequence raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            map_bytes_to_rules(b"")

    def test_map_bytes_to_rules_invalid_type(self):
        """Verify non-bytes input raises TypeError."""
        with pytest.raises(TypeError, match="must be bytes or bytearray"):
            map_bytes_to_rules([0, 30, 90])  # type: ignore

    def test_validate_rule(self):
        """Verify validate_rule boolean checks."""
        assert validate_rule(0) is True
        assert validate_rule(110) is True
        assert validate_rule(255) is True
        assert validate_rule(-1) is False
        assert validate_rule(256) is False
        assert validate_rule("30") is False
        assert validate_rule(True) is False
        assert validate_rule(None) is False
