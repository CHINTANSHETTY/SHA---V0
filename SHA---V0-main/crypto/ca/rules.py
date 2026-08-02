"""
Cellular Automata Rule Definitions Module.

Provides functions to validate and evaluate Elementary Cellular Automata (ECA)
Wolfram local transition rules (0 to 255).
"""

from typing import Dict, Tuple


def validate_rule_number(rule_number: int) -> int:
    """
    Validates that a rule number is an integer in the range [0, 255].

    Args:
        rule_number: The Wolfram rule number to validate.

    Returns:
        The validated rule number as an integer.

    Raises:
        TypeError: If rule_number is not an integer.
        ValueError: If rule_number is out of the valid range [0, 255].
    """
    if not isinstance(rule_number, int) or isinstance(rule_number, bool):
        raise TypeError(f"Rule number must be an integer, got {type(rule_number).__name__}")
    if not (0 <= rule_number <= 255):
        raise ValueError(f"Rule number must be in range [0, 255], got {rule_number}")
    return rule_number


def apply_rule(rule_number: int, left: int, center: int, right: int) -> int:
    """
    Applies an Elementary Cellular Automata (ECA) rule to a 3-bit neighborhood.

    The next state bit is algorithmically computed from the Wolfram rule number:
    Neighborhood index = (left << 2) | (center << 1) | right
    Next bit = (rule_number >> neighborhood_index) & 1

    Args:
        rule_number: Wolfram rule number (0 to 255).
        left: Left neighbor bit (0 or 1).
        center: Center cell bit (0 or 1).
        right: Right neighbor bit (0 or 1).

    Returns:
        The resulting next state bit (0 or 1).

    Raises:
        TypeError: If inputs are not integers.
        ValueError: If rule_number is invalid or neighborhood bits are not 0 or 1.
    """
    rule_number = validate_rule_number(rule_number)

    for name, val in (("left", left), ("center", center), ("right", right)):
        if not isinstance(val, int) or isinstance(val, bool):
            raise TypeError(f"Neighborhood bit '{name}' must be an integer, got {type(val).__name__}")
        if val not in (0, 1):
            raise ValueError(f"Neighborhood bit '{name}' must be 0 or 1, got {val}")

    neighborhood_index = (left << 2) | (center << 1) | right
    return (rule_number >> neighborhood_index) & 1


def get_rule_truth_table(rule_number: int) -> Dict[Tuple[int, int, int], int]:
    """
    Generates the complete 8-neighborhood truth table for a given Wolfram rule number.

    Args:
        rule_number: Wolfram rule number (0 to 255).

    Returns:
        A dictionary mapping (left, center, right) bit tuples to their output bit.
    """
    rule_number = validate_rule_number(rule_number)
    truth_table = {}
    for left in (1, 0):
        for center in (1, 0):
            for right in (1, 0):
                neighborhood = (left, center, right)
                truth_table[neighborhood] = apply_rule(rule_number, left, center, right)
    return truth_table
