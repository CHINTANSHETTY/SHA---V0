"""
Rule Mapping Module for Dynamic Rule Scheduler.

Converts raw byte values and hash digests into valid Wolfram Cellular Automata
rule numbers (0 to 255).
"""

from typing import Any, List
from crypto.scheduler.exceptions import InvalidRuleError


def validate_rule(rule: Any) -> bool:
    """
    Checks if a given rule value is a valid Wolfram CA rule integer in the range [0, 255].

    Args:
        rule: Input rule value to validate.

    Returns:
        True if rule is an int and 0 <= rule <= 255, False otherwise.
    """
    if isinstance(rule, bool) or not isinstance(rule, int):
        return False
    return 0 <= rule <= 255


def rule_from_byte(byte: int) -> int:
    """
    Converts a single byte value (0–255) into a valid Wolfram CA rule number.

    Args:
        byte: Input byte integer (0 to 255).

    Returns:
        Valid Wolfram CA rule integer (0 to 255).

    Raises:
        TypeError: If byte is not an integer.
        InvalidRuleError: If byte is out of the valid range [0, 255].
    """
    if isinstance(byte, bool) or not isinstance(byte, int):
        raise TypeError(f"Byte input must be an integer, got {type(byte).__name__}")
    if not (0 <= byte <= 255):
        raise InvalidRuleError(f"Byte value must be in range [0, 255], got {byte}")

    return byte


def map_byte_to_rule(byte: int) -> int:
    """
    Alias for rule_from_byte for backward compatibility.
    """
    return rule_from_byte(byte)


def bytes_to_rules(data: bytes) -> List[int]:
    """
    Converts an entire byte stream into a list of valid Wolfram CA rules.

    Args:
        data: Input bytes or bytearray sequence.

    Returns:
        List of rule integers (0 to 255).

    Raises:
        TypeError: If data is not bytes or bytearray.
        ValueError: If data is empty.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"Data input must be bytes or bytearray, got {type(data).__name__}")
    if len(data) == 0:
        raise ValueError("Input data cannot be empty")

    return [rule_from_byte(b) for b in data]


def map_bytes_to_rules(data: bytes) -> List[int]:
    """
    Alias for bytes_to_rules for backward compatibility.
    """
    return bytes_to_rules(data)
