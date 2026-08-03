"""Elementary Cellular Automata (ECA) Rule Engine Representation and Utilities.

This module implements support for all 256 Wolfram Elementary Cellular Automata rules
(Rules 0 to 255). It provides rule validation, deterministic 8-bit lookup table conversion,
immutable cached lookup tables, and neighborhood evaluation utilities.

Wolfram Rule Representation:
    An Elementary Cellular Automaton consists of a 1D grid of binary cells.
    The next state of a cell depends on its current state and its left and right neighbors.
    There are 2^3 = 8 possible 3-cell neighborhood configurations (111 down to 000).

    Neighborhood to Bit Mapping:
        Neighborhood  (L, C, R)  Binary Value  Bit Position in Rule
        ----------------------------------------------------------
            111       (1, 1, 1)       7               Bit 7
            110       (1, 1, 0)       6               Bit 6
            101       (1, 0, 1)       5               Bit 5
            100       (1, 0, 0)       4               Bit 4
            011       (0, 1, 1)       3               Bit 3
            010       (0, 1, 0)       2               Bit 2
            001       (0, 0, 1)       1               Bit 1
            000       (0, 0, 0)       0               Bit 0

Time Complexity:
    - parse_rule: O(1) time complexity (memoized up to 256 entries).
    - validate_rule: O(1) time complexity.
    - get_neighborhood_output: O(1) time complexity.
"""

from functools import lru_cache
from types import MappingProxyType
from typing import Any, Dict, List, Set, Tuple, Union

# =========================================================
# MODULE CONSTANTS
# =========================================================
MIN_RULE: int = 0
MAX_RULE: int = 255
VALID_BITS: Set[int] = {0, 1}

# =========================================================
# TYPE ALIASES
# =========================================================
Neighborhood = Tuple[int, int, int]
LookupTable = MappingProxyType
State = List[int]


def validate_rule(rule: Any) -> int:
    """Validate that the given rule is an integer within the range [0, 255].

    Args:
        rule: The rule to validate. Must be an integer between 0 and 255 inclusive.

    Returns:
        int: The validated rule integer.

    Raises:
        TypeError: If rule is not an integer (or if it is a boolean/float/string/None).
        ValueError: If rule is outside the range [0, 255].
    """
    if isinstance(rule, bool) or not isinstance(rule, int):
        raise TypeError(f"Rule must be an integer, got {type(rule).__name__}")
    
    if not (MIN_RULE <= rule <= MAX_RULE):
        raise ValueError(f"Rule must be between {MIN_RULE} and {MAX_RULE}, got {rule}")

    return rule


@lru_cache(maxsize=256)
def _get_rule_table_proxy(rule: int) -> LookupTable:
    """Compute the immutable binary lookup table for a validated Wolfram rule integer.

    Args:
        rule: Validated integer rule (0-255).

    Returns:
        LookupTable: Immutable MappingProxyType dictionary mapping (L, C, R) -> output_bit.
    """
    table: Dict[Neighborhood, int] = {}
    for left in (0, 1):
        for center in (0, 1):
            for right in (0, 1):
                # Calculate integer index 0..7 from (left, center, right)
                bit_position = (left << 2) | (center << 1) | right
                # Extract bit_position bit from rule integer
                output_bit = (rule >> bit_position) & 1
                table[(left, center, right)] = output_bit
    return MappingProxyType(table)


def parse_rule(rule: Any) -> LookupTable:
    """Parse and convert an integer rule into an immutable binary lookup table.

    The returned lookup table maps every 3-cell neighborhood tuple (left, center, right)
    to its corresponding output bit (0 or 1).

    Args:
        rule: An integer rule number (0-255).

    Returns:
        LookupTable: Immutable MappingProxyType dictionary mapping (L, C, R) to output bit.

    Raises:
        TypeError: If rule is not an integer.
        ValueError: If rule is outside [0, 255].
    """
    validated_rule = validate_rule(rule)
    return _get_rule_table_proxy(validated_rule)


def rule_to_binary(rule: Any) -> str:
    """Convert an integer rule (0-255) into its 8-bit binary string representation.

    Args:
        rule: An integer rule number (0-255).

    Returns:
        str: 8-character string of '0' and '1' characters (e.g. Rule 30 -> "00011110").

    Raises:
        TypeError: If rule is not an integer.
        ValueError: If rule is outside [0, 255].
    """
    validated_rule = validate_rule(rule)
    return f"{validated_rule:08b}"


def get_neighborhood_output(rule: Any, left: Any, center: Any, right: Any) -> int:
    """Evaluate a single 3-cell neighborhood for a given Wolfram rule.

    Args:
        rule: An integer rule number (0-255).
        left: Left neighbor cell state (0 or 1).
        center: Target cell state (0 or 1).
        right: Right neighbor cell state (0 or 1).

    Returns:
        int: Output bit (0 or 1) according to the rule.

    Raises:
        TypeError: If rule or neighbor states are not integers.
        ValueError: If rule is out of bounds or neighbor states are not binary (0 or 1).
    """
    table = parse_rule(rule)
    
    for name, val in [("left", left), ("center", center), ("right", right)]:
        if isinstance(val, bool) or not isinstance(val, int):
            raise TypeError(f"Neighborhood cell '{name}' must be an integer bit (0 or 1), got {type(val).__name__}")
        if val not in VALID_BITS:
            raise ValueError(f"Neighborhood cell '{name}' must be 0 or 1, got {val}")

    return table[(left, center, right)]
