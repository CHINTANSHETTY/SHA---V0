"""Cellular Automata Utility Module.

This module provides deterministic helper functions for binary state conversions,
state initialization, random state generation, state validation, distance and population
metrics, matrix manipulations, and state slicing operations used across the
KDR-CA-AEAD cryptographic engine.

Determinism & Security:
    - Random state generation uses an isolated `random.Random(seed)` instance to ensure
      100% reproducible states without modifying Python's global `random` state.
    - All conversion and metric functions behave deterministically.

Time Complexity:
    - State Conversions & Slicing: O(N) where N is the length of the binary state.
    - Metrics (Population count, Hamming distance, XOR, Inversion): O(N).
    - Matrix conversions: O(M * N) where M is generations and N is state width.
    - Integer conversions: O(width).
"""

import random
from typing import Any, List, Optional, Sequence, Set, Union

# =========================================================
# MODULE CONSTANTS
# =========================================================
VALID_BITS: Set[int] = {0, 1}
DEFAULT_PAD_VALUE: int = 0
MIN_STATE_LENGTH: int = 1

# =========================================================
# TYPE ALIASES
# =========================================================
Bit = int
State = List[int]
StateLike = Union[Sequence[int], str]
Matrix = List[List[int]]


# =========================================================
# VALIDATION HELPERS
# =========================================================
def validate_bit(bit: Any) -> Bit:
    """Validate that a value is a binary bit integer (0 or 1).

    Args:
        bit: Value to validate.

    Returns:
        Bit: Validated integer 0 or 1.

    Raises:
        TypeError: If bit is not an integer (e.g. bool, float, str, None).
        ValueError: If bit is an integer other than 0 or 1.
    """
    if isinstance(bit, bool) or not isinstance(bit, int):
        raise TypeError(f"Bit must be an integer (0 or 1), got {type(bit).__name__}")
    if bit not in VALID_BITS:
        raise ValueError(f"Bit must be 0 or 1, got {bit}")
    return bit


def validate_state_length(length: Any) -> int:
    """Validate that a state length parameter is an integer >= 1.

    Args:
        length: Length parameter to validate.

    Returns:
        int: Validated state length integer.

    Raises:
        TypeError: If length is not an integer.
        ValueError: If length < 1.
    """
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError(f"State length must be an integer, got {type(length).__name__}")
    if length < MIN_STATE_LENGTH:
        raise ValueError(f"State length must be >= {MIN_STATE_LENGTH}, got {length}")
    return length


def validate_width(width: Any) -> int:
    """Validate that a bit width parameter is an integer >= 1.

    Args:
        width: Width parameter to validate.

    Returns:
        int: Validated width integer.

    Raises:
        TypeError: If width is not an integer.
        ValueError: If width < 1.
    """
    if isinstance(width, bool) or not isinstance(width, int):
        raise TypeError(f"Width must be an integer, got {type(width).__name__}")
    if width < 1:
        raise ValueError(f"Width must be >= 1, got {width}")
    return width


def _validate_state(state: Any) -> State:
    """Internal helper to validate and normalize state inputs into a List[int].

    Accepts binary strings ("0101"), lists of bits, or tuples of bits.

    Args:
        state: Input state to validate.

    Returns:
        State: Normalized list of integer bits (0 or 1).

    Raises:
        TypeError: If state is None or an unsupported type.
        ValueError: If state is empty or contains non-binary values.
    """
    if state is None:
        raise TypeError("State cannot be None")

    if isinstance(state, str):
        if len(state) < MIN_STATE_LENGTH:
            raise ValueError("State cannot be empty")
        parsed: State = []
        for char in state:
            if char not in ("0", "1"):
                raise ValueError(f"Invalid binary character '{char}' in state string")
            parsed.append(int(char))
        return parsed

    if isinstance(state, (list, tuple)):
        if len(state) < MIN_STATE_LENGTH:
            raise ValueError("State cannot be empty")
        parsed = []
        for idx, elem in enumerate(state):
            if isinstance(elem, bool) or not isinstance(elem, int):
                raise TypeError(
                    f"State element at index {idx} must be an integer bit (0 or 1), got {type(elem).__name__}"
                )
            if elem not in VALID_BITS:
                raise ValueError(f"State element at index {idx} must be 0 or 1, got {elem}")
            parsed.append(elem)
        return parsed

    raise TypeError(
        f"State must be a list/tuple of bits or a binary bit string, got {type(state).__name__}"
    )


# =========================================================
# STATE CONVERSIONS
# =========================================================
def state_from_string(bits: str) -> State:
    """Convert a binary string (e.g. "010101") into a List[int] state.

    Args:
        bits: Binary string composed of '0' and '1' characters.

    Returns:
        State: List of binary integers [0, 1, 0, 1, 0, 1].

    Raises:
        TypeError: If bits is not a string.
        ValueError: If bits is empty or contains non-binary characters.
    """
    if not isinstance(bits, str):
        raise TypeError(f"Expected a binary string, got {type(bits).__name__}")
    return _validate_state(bits)


def state_to_string(state: StateLike) -> str:
    """Convert a binary state sequence into a string representation (e.g. [1,0,1] -> "101").

    Args:
        state: Binary state sequence or string.

    Returns:
        str: String of '0' and '1' characters.

    Raises:
        TypeError: If state is invalid.
        ValueError: If state is empty or contains invalid bits.
    """
    norm_state = _validate_state(state)
    return "".join(str(b) for b in norm_state)


def int_to_state(value: Any, width: Any) -> State:
    """Convert a non-negative integer into a big-endian binary state array of specified width.

    Args:
        value: Non-negative integer to convert (>= 0).
        width: Exact bit width for the output state (>= 1).

    Returns:
        State: Big-endian list of binary bits of length equal to width.

    Raises:
        TypeError: If value or width are not integers.
        ValueError: If value < 0, width < 1, or value overflows specified width.
    """
    valid_w = validate_width(width)

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Value must be an integer, got {type(value).__name__}")

    if value < 0:
        raise ValueError(f"Value must be non-negative (>= 0), got {value}")

    max_value = (1 << valid_w) - 1
    if value > max_value:
        raise ValueError(
            f"Value {value} overflows specified width {valid_w} (maximum value is {max_value})"
        )

    binary_str = f"{value:0{valid_w}b}"
    return [int(char) for char in binary_str]


def state_to_int(state: StateLike) -> int:
    """Convert a big-endian binary state array back into an integer.

    Args:
        state: Binary state sequence or bit string (e.g. [1, 1, 0, 1]).

    Returns:
        int: Converted integer value (e.g. 13).

    Raises:
        TypeError: If state has invalid types.
        ValueError: If state is empty or contains non-binary bits.
    """
    norm_state = _validate_state(state)
    val = 0
    for bit in norm_state:
        val = (val << 1) | bit
    return val


# =========================================================
# STATE INITIALIZATION
# =========================================================
def zero_state(length: Any) -> State:
    """Generate an all-zero binary state array of specified length.

    Args:
        length: State length (positive integer >= 1).

    Returns:
        State: List of zeros of specified length.
    """
    valid_len = validate_state_length(length)
    return [0] * valid_len


def one_state(length: Any) -> State:
    """Generate an all-one binary state array of specified length.

    Args:
        length: State length (positive integer >= 1).

    Returns:
        State: List of ones of specified length.
    """
    valid_len = validate_state_length(length)
    return [1] * valid_len


def random_state(length: Any, seed: Optional[Any] = None) -> State:
    """Generate a pseudo-random binary state array.

    Uses an isolated `random.Random(seed)` generator so global random state is unaffected.

    Args:
        length: Desired state length (>= 1).
        seed: Optional integer seed for reproducible generation.

    Returns:
        State: Random binary state array of specified length.

    Raises:
        TypeError: If length or seed have invalid types.
        ValueError: If length < 1.
    """
    valid_len = validate_state_length(length)

    if seed is not None:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError(f"Seed must be an integer, got {type(seed).__name__}")

    rng = random.Random(seed)
    return [rng.randint(0, 1) for _ in range(valid_len)]


def copy_state(state: StateLike) -> State:
    """Return a deep copy of a binary state array.

    Args:
        state: Binary state to copy.

    Returns:
        State: Independent copy of the state array.
    """
    norm_state = _validate_state(state)
    return list(norm_state)


# =========================================================
# ANALYSIS UTILITIES
# =========================================================
def population_count(state: StateLike) -> int:
    """Count the number of set bits (ones) in a binary state.

    Args:
        state: Binary state sequence or bit string.

    Returns:
        int: Number of 1 bits.
    """
    norm_state = _validate_state(state)
    return sum(norm_state)


def hamming_distance(state1: StateLike, state2: StateLike) -> int:
    """Calculate the Hamming distance (number of differing positions) between two equal-length states.

    Args:
        state1: First binary state.
        state2: Second binary state.

    Returns:
        int: Number of differing bit positions.

    Raises:
        ValueError: If state lengths differ.
    """
    norm1 = _validate_state(state1)
    norm2 = _validate_state(state2)

    if len(norm1) != len(norm2):
        raise ValueError(
            f"States must have equal lengths for Hamming distance, got {len(norm1)} and {len(norm2)}"
        )

    return sum(b1 != b2 for b1, b2 in zip(norm1, norm2))


def compare_states(a: Any, b: Any) -> bool:
    """Compare two binary states for equality.

    Args:
        a: First state to compare.
        b: Second state to compare.

    Returns:
        bool: True if both states are valid and identical, False otherwise.
    """
    try:
        norm_a = _validate_state(a)
        norm_b = _validate_state(b)
        return norm_a == norm_b
    except (TypeError, ValueError):
        return False


def invert_state(state: StateLike) -> State:
    """Bitwise invert a binary state (0 -> 1, 1 -> 0).

    Args:
        state: Binary state to invert.

    Returns:
        State: Inverted binary state array.
    """
    norm_state = _validate_state(state)
    return [1 - b for b in norm_state]


def xor_states(a: StateLike, b: StateLike) -> State:
    """Perform bitwise XOR between two equal-length binary states.

    Args:
        a: First binary state.
        b: Second binary state.

    Returns:
        State: Resulting binary state array.

    Raises:
        ValueError: If state lengths differ.
    """
    norm_a = _validate_state(a)
    norm_b = _validate_state(b)

    if len(norm_a) != len(norm_b):
        raise ValueError(
            f"States must have equal lengths for XOR operation, got {len(norm_a)} and {len(norm_b)}"
        )

    return [x ^ y for x, y in zip(norm_a, norm_b)]


# =========================================================
# MATRIX UTILITIES
# =========================================================
def states_to_matrix(states: Any) -> Matrix:
    """Convert a sequence of generation states into a 2D matrix (List[List[int]]).

    Args:
        states: Sequence of binary states.

    Returns:
        Matrix: 2D matrix of integer bits.

    Raises:
        TypeError: If input is invalid.
        ValueError: If states is empty or row lengths vary.
    """
    if not isinstance(states, (list, tuple)):
        raise TypeError(f"States matrix input must be a list/tuple, got {type(states).__name__}")

    if len(states) == 0:
        raise ValueError("States sequence cannot be empty")

    matrix: Matrix = []
    expected_width: Optional[int] = None

    for idx, row in enumerate(states):
        norm_row = _validate_state(row)
        if expected_width is None:
            expected_width = len(norm_row)
        elif len(norm_row) != expected_width:
            raise ValueError(
                f"Matrix row {idx} length ({len(norm_row)}) does not match expected width ({expected_width})"
            )
        matrix.append(norm_row)

    return matrix


def matrix_to_states(matrix: Any) -> Matrix:
    """Validate and convert a 2D matrix representation back into a list of state rows.

    Args:
        matrix: 2D matrix to validate.

    Returns:
        Matrix: Standardized list of state rows.
    """
    return states_to_matrix(matrix)


# =========================================================
# MISCELLANEOUS UTILITIES
# =========================================================
def chunk_state(state: StateLike, size: Any) -> List[State]:
    """Split a binary state into fixed-size chunk sub-states.

    Args:
        state: Binary state to split.
        size: Target chunk size (>= 1).

    Returns:
        List[State]: List of state chunks.

    Raises:
        TypeError: If size is not an integer.
        ValueError: If size < 1.
    """
    norm_state = _validate_state(state)

    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError(f"Chunk size must be an integer, got {type(size).__name__}")
    if size < 1:
        raise ValueError(f"Chunk size must be >= 1, got {size}")

    return [norm_state[i : i + size] for i in range(0, len(norm_state), size)]


def flatten_states(states: Any) -> State:
    """Flatten a sequence of nested binary states into a single 1D state array.

    Args:
        states: Sequence of binary states.

    Returns:
        State: Flattened binary state array.

    Raises:
        TypeError: If input or elements are invalid.
    """
    if not isinstance(states, (list, tuple)):
        raise TypeError(f"Expected a list/tuple of states, got {type(states).__name__}")

    if len(states) == 0:
        return []

    flattened: State = []
    for substate in states:
        flattened.extend(_validate_state(substate))

    return flattened


def pad_state(
    state: StateLike, length: Any, value: Any = DEFAULT_PAD_VALUE
) -> State:
    """Pad a binary state to target length using specified bit value.

    Args:
        state: Binary state to pad.
        length: Target state length (>= 1).
        value: Bit value for padding (0 or 1, defaults to 0).

    Returns:
        State: Padded state list.
    """
    norm_state = _validate_state(state)
    target_len = validate_state_length(length)
    pad_bit = validate_bit(value)

    if len(norm_state) >= target_len:
        return list(norm_state)

    return norm_state + [pad_bit] * (target_len - len(norm_state))


def trim_state(state: StateLike, length: Any) -> State:
    """Trim a binary state to a shorter target length.

    Args:
        state: Binary state to trim.
        length: Target state length (>= 1).

    Returns:
        State: Trimmed state list.

    Raises:
        ValueError: If target length > current state length.
    """
    norm_state = _validate_state(state)
    target_len = validate_state_length(length)

    if target_len > len(norm_state):
        raise ValueError(
            f"Target length {target_len} exceeds current state length {len(norm_state)}"
        )

    return norm_state[:target_len]
