"""
Unit tests for Cellular Automata Utilities (crypto/ca/utils.py).
"""

import pytest
from crypto.ca.utils import (
    bits_to_string,
    hex_to_state,
    random_binary_state,
    state_to_hex,
    string_to_bits,
    validate_binary_state,
)


class TestCAUtils:
    """Test suite for utility functions in crypto/ca/utils.py."""

    def test_validate_binary_state_valid(self):
        """Verify validation of valid state representations."""
        assert validate_binary_state([0, 1, 1, 0]) == [0, 1, 1, 0]
        assert validate_binary_state((1, 0, 0, 1)) == [1, 0, 0, 1]
        assert validate_binary_state("1010") == [1, 0, 1, 0]

    def test_validate_binary_state_invalid_types(self):
        """Verify invalid type inputs raise TypeError."""
        with pytest.raises(TypeError, match="State cannot be None"):
            validate_binary_state(None)

        with pytest.raises(TypeError, match="State must be a list, tuple, or string"):
            validate_binary_state(12345)

        with pytest.raises(TypeError, match="State elements must be integers"):
            validate_binary_state([0, 1, "0", 1])

        with pytest.raises(TypeError, match="State elements must be integers"):
            validate_binary_state([0, 1, True, 0])

    def test_validate_binary_state_invalid_values(self):
        """Verify out-of-range bit values raise ValueError."""
        with pytest.raises(ValueError, match="State sequence cannot be empty"):
            validate_binary_state([])

        with pytest.raises(ValueError, match="State string cannot be empty"):
            validate_binary_state("")

        with pytest.raises(ValueError, match="State elements must be 0 or 1"):
            validate_binary_state([0, 2, 1])

        with pytest.raises(ValueError, match="State binary string contains invalid character"):
            validate_binary_state("10201")

    def test_string_to_bits_binary_digit_string(self):
        """Verify parsing strings of 0s and 1s directly as bit arrays."""
        assert string_to_bits("01101") == [0, 1, 1, 0, 1]

    def test_string_to_bits_ascii_text(self):
        """Verify converting text string into 8-bit UTF-8 sequences."""
        # 'A' ASCII = 65 = 01000001
        assert string_to_bits("A") == [0, 1, 0, 0, 0, 0, 0, 1]

    def test_string_to_bits_invalid(self):
        """Verify string_to_bits error conditions."""
        with pytest.raises(TypeError, match="Expected string input"):
            string_to_bits(123)  # type: ignore

        with pytest.raises(ValueError, match="Input string cannot be empty"):
            string_to_bits("")

    def test_bits_to_string_binary(self):
        """Verify converting bit array back to binary digit string."""
        assert bits_to_string([0, 1, 1, 0, 1], mode="binary") == "01101"

    def test_bits_to_string_ascii(self):
        """Verify converting bit array back to ASCII text."""
        bits = [0, 1, 0, 0, 0, 0, 0, 1]  # 'A'
        assert bits_to_string(bits, mode="ascii") == "A"

    def test_bits_to_string_ascii_unaligned(self):
        """Verify ASCII mode fails if bit length is not a multiple of 8."""
        with pytest.raises(ValueError, match="must be a multiple of 8"):
            bits_to_string([0, 1, 1], mode="ascii")

    def test_bits_to_string_invalid_mode(self):
        """Verify invalid mode parameter raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported mode"):
            bits_to_string([0, 1, 0], mode="invalid_mode")

    def test_state_to_hex(self):
        """Verify binary state to hex conversion."""
        # 1111 0000 -> f0
        assert state_to_hex([1, 1, 1, 1, 0, 0, 0, 0]) == "f0"
        # 101 -> padded to 0101 -> 5
        assert state_to_hex([1, 0, 1]) == "5"

    def test_hex_to_state(self):
        """Verify hex string to binary state conversion."""
        assert hex_to_state("f0") == [1, 1, 1, 1, 0, 0, 0, 0]
        assert hex_to_state("0xf0") == [1, 1, 1, 1, 0, 0, 0, 0]
        assert hex_to_state("0X5") == [0, 1, 0, 1]

    def test_hex_to_state_invalid(self):
        """Verify hex_to_state error conditions."""
        with pytest.raises(TypeError, match="Expected string input"):
            hex_to_state(0xF0)  # type: ignore

        with pytest.raises(ValueError, match="Hex string cannot be empty"):
            hex_to_state("")

        with pytest.raises(ValueError, match="Invalid hexadecimal character"):
            hex_to_state("1g")

    def test_random_binary_state_length(self):
        """Verify random binary state length and elements."""
        state = random_binary_state(32)
        assert len(state) == 32
        assert all(b in (0, 1) for b in state)

    def test_random_binary_state_seeded(self):
        """Verify deterministic random state generation when seed is provided."""
        s1 = random_binary_state(16, seed=42)
        s2 = random_binary_state(16, seed=42)
        assert s1 == s2

    def test_random_binary_state_invalid(self):
        """Verify invalid parameters for random_binary_state."""
        with pytest.raises(TypeError, match="Length must be an integer"):
            random_binary_state(10.5)  # type: ignore

        with pytest.raises(ValueError, match="Length must be at least 1"):
            random_binary_state(0)
