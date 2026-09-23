"""Deterministic One-Dimensional Elementary Cellular Automata Evolution Engine.

This module implements deterministic 1D Cellular Automata evolution supporting
arbitrary binary state lengths, configurable boundary conditions ("periodic" and "null"),
and multi-generation step evolution.

Boundary Conditions:
    - Periodic ("periodic"):
        Wraps around both ends of the cell array.
        Left neighbor of cell 0 is cell N-1.
        Right neighbor of cell N-1 is cell 0.
        For a 1-cell array, left, center, and right neighbors are all cell 0.

    - Null ("null"):
        Boundary conditions outside the cell array are treated as 0 (zero-padded).
        Left neighbor of cell 0 is 0.
        Right neighbor of cell N-1 is 0.

Determinism & Security:
    Evolution is strictly deterministic. Given identical inputs (state, rule, generations,
    and boundary), the evolution output is guaranteed to be identical. No randomness is used.

Time Complexity:
    - evolve_step: O(N) where N is the length of the binary state array.
    - evolve: O(N * generations) where N is state length.
"""

from typing import Any, Dict, List, Set, Tuple, Union
from types import MappingProxyType

from .rules import (
    LookupTable,
    Neighborhood,
    State,
    VALID_BITS,
    parse_rule,
)

# =========================================================
# MODULE CONSTANTS
# =========================================================
BOUNDARY_PERIODIC: str = "periodic"
BOUNDARY_NULL: str = "null"
VALID_BOUNDARIES: Set[str] = {BOUNDARY_PERIODIC, BOUNDARY_NULL}


def validate_boundary(boundary: Any) -> str:
    """Validate and normalize a boundary condition string.

    Args:
        boundary: Boundary name ("periodic" or "null", case-insensitive).

    Returns:
        str: Normalized lowercase boundary condition string.

    Raises:
        TypeError: If boundary is not a string.
        ValueError: If boundary is not "periodic" or "null".
    """
    if not isinstance(boundary, str):
        raise TypeError(f"Boundary condition must be a string, got {type(boundary).__name__}")
    
    normalized = boundary.strip().lower()
    if normalized not in VALID_BOUNDARIES:
        raise ValueError(
            f"Invalid boundary condition '{boundary}'. "
            f"Supported boundaries are: {sorted(VALID_BOUNDARIES)}"
        )
    
    return normalized


def validate_generations(generations: Any) -> int:
    """Validate that generations count is a positive integer (>= 1).

    Args:
        generations: Generation count to validate.

    Returns:
        int: Validated generations integer.

    Raises:
        TypeError: If generations is not an integer.
        ValueError: If generations < 1.
    """
    if isinstance(generations, bool) or not isinstance(generations, int):
        raise TypeError(f"Generations count must be an integer, got {type(generations).__name__}")
    
    if generations < 1:
        raise ValueError(f"Generations count must be positive (>= 1), got {generations}")

    return generations


def validate_state(state: Any) -> State:
    """Validate and normalize a binary state input.

    Input state can be a list of bits, tuple of bits, or a binary bit string ("0101").

    Args:
        state: State input to validate (e.g. [0, 1, 0], (1, 1, 0), or "1010").

    Returns:
        State: List of binary integers (0 or 1).

    Raises:
        TypeError: If state is None or of an unsupported type.
        ValueError: If state is empty or contains non-binary elements.
    """
    if state is None:
        raise TypeError("State cannot be None")

    if isinstance(state, str):
        if len(state) == 0:
            raise ValueError("State cannot be empty")
        parsed: List[int] = []
        for char in state:
            if char not in ("0", "1"):
                raise ValueError(f"Invalid binary character '{char}' in state string")
            parsed.append(int(char))
        return parsed

    if isinstance(state, (list, tuple)):
        if len(state) == 0:
            raise ValueError("State cannot be empty")
        parsed = []
        for idx, elem in enumerate(state):
            if isinstance(elem, bool) or not isinstance(elem, int):
                raise TypeError(f"State element at index {idx} must be an integer bit (0 or 1), got {type(elem).__name__}")
            if elem not in VALID_BITS:
                raise ValueError(f"State element at index {idx} must be 0 or 1, got {elem}")
            parsed.append(elem)
        return parsed

    raise TypeError(f"State must be a list/tuple of bits or a binary bit string, got {type(state).__name__}")


def evolve_step(
    state: Union[List[int], Tuple[int, ...], str],
    lookup: Union[LookupTable, Dict[Neighborhood, int]],
    boundary: str = BOUNDARY_PERIODIC,
) -> State:
    """Perform a single generation evolution step for a 1D Cellular Automaton state.

    Args:
        state: Binary state sequence or bit string.
        lookup: Lookup table mapping (L, C, R) tuples to binary output bits.
        boundary: Boundary condition ("periodic" or "null").

    Returns:
        State: New binary state array after 1 evolution step.

    Raises:
        TypeError: If state or boundary are invalid types.
        ValueError: If state or boundary values are invalid.
    """
    norm_state = validate_state(state)
    norm_boundary = validate_boundary(boundary)
    
    length = len(norm_state)
    next_state: List[int] = [0] * length

    for i in range(length):
        center = norm_state[i]

        # Determine left neighbor
        if i > 0:
            left = norm_state[i - 1]
        elif norm_boundary == BOUNDARY_PERIODIC:
            left = norm_state[length - 1]
        else:  # BOUNDARY_NULL
            left = 0

        # Determine right neighbor
        if i < length - 1:
            right = norm_state[i + 1]
        elif norm_boundary == BOUNDARY_PERIODIC:
            right = norm_state[0]
        else:  # BOUNDARY_NULL
            right = 0

        next_state[i] = lookup[(left, center, right)]

    return next_state


def evolve(
    state: Union[List[int], Tuple[int, ...], str],
    rule: Any,
    generations: Any = 1,
    boundary: Any = BOUNDARY_PERIODIC,
) -> State:
    """Perform deterministic one-dimensional cellular automata evolution across multiple generations.

    Args:
        state: Initial binary state (list/tuple of 0s and 1s, or bit string like "01001").
        rule: Wolfram rule number (0 to 255).
        generations: Number of evolution steps (positive integer >= 1, defaults to 1).
        boundary: Boundary condition ("periodic" or "null", defaults to "periodic").

    Returns:
        State: Final binary state array after requested generations of evolution.

    Raises:
        TypeError: If any input has an invalid type.
        ValueError: If any input has an invalid value.
    """
    current_state = validate_state(state)
    lookup_table = parse_rule(rule)
    gen_count = validate_generations(generations)
    norm_boundary = validate_boundary(boundary)

    for _ in range(gen_count):
        current_state = evolve_step(current_state, lookup_table, norm_boundary)

    return current_state
