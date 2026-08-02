"""
Unit tests for Rule Mapping module (crypto/scheduler/mapping.py).
"""

import pytest
from crypto.scheduler import (
    InvalidRuleError,
    bytes_to_rules,
    map_byte_to_rule,
    map_bytes_to_rules,
    rule_from_byte,
    validate_rule,
)


class TestRuleMapping:
    """Test suite for mapping functions in crypto/scheduler/mapping.py."""

    def test_rule_from_byte_valid(self):
        """Verify byte values map to identical Wolfram rule numbers in [0, 255]."""
        assert rule_from_byte(0) == 0
        assert rule_from_byte(30) == 30
        assert rule_from_byte(90) == 90
        assert rule_from_byte(110) == 110
        assert rule_from_byte(150) == 150
        assert rule_from_byte(255) == 255

    def test_rule_from_byte_out_of_bounds(self):
        """Verify values outside [0, 255] raise InvalidRuleError."""
        with pytest.raises(InvalidRuleError, match="must be in range"):
            rule_from_byte(-1)

        with pytest.raises(InvalidRuleError, match="must be in range"):
            rule_from_byte(256)

    def test_rule_from_byte_invalid_types(self):
        """Verify non-integer inputs raise TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            rule_from_byte("30")  # type: ignore

        with pytest.raises(TypeError, match="must be an integer"):
            rule_from_byte(30.5)  # type: ignore

        with pytest.raises(TypeError, match="must be an integer"):
            rule_from_byte(True)  # type: ignore

    def test_map_byte_to_rule_alias(self):
        """Verify map_byte_to_rule alias behaves identically."""
        assert map_byte_to_rule(30) == 30
        with pytest.raises(InvalidRuleError):
            map_byte_to_rule(300)

    def test_bytes_to_rules_valid(self):
        """Verify mapping byte sequences into lists of rule numbers."""
        data = b"\x00\x1e\x5a\x6e\x96"  # 0, 30, 90, 110, 150
        rules = bytes_to_rules(data)
        assert rules == [0, 30, 90, 110, 150]

    def test_map_bytes_to_rules_alias(self):
        """Verify map_bytes_to_rules alias behaves identically."""
        data = b"\x1e\x5a"
        assert map_bytes_to_rules(data) == [30, 90]

    def test_bytes_to_rules_empty(self):
        """Verify empty byte sequence raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            bytes_to_rules(b"")

    def test_bytes_to_rules_invalid_type(self):
        """Verify non-bytes input raises TypeError."""
        with pytest.raises(TypeError, match="must be bytes or bytearray"):
            bytes_to_rules([0, 30, 90])  # type: ignore

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
