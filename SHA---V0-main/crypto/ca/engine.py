"""
Cellular Automata Engine Module.

Implements the reusable `CellularAutomataEngine` class to evolve binary state
vectors using dynamically reconfigurable elementary cellular automata rules
and specified boundary conditions.
"""

from typing import Any, List

from crypto.ca.rules import apply_rule, validate_rule_number
from crypto.ca.utils import validate_binary_state


class CellularAutomataEngine:
    """
    Modular Cellular Automata Engine for 1D Elementary Cellular Automata.

    Supports dynamic rule selection (Wolfram rules 0–255) and boundary modes
    ('wrap' periodic or 'fixed_zero').
    """

    SUPPORTED_BOUNDARIES = {"wrap", "fixed_zero"}

    def __init__(self, rule: int = 30, boundary: str = "wrap") -> None:
        """
        Initializes the Cellular Automata Engine.

        Args:
            rule: Wolfram rule number (0 to 255). Default is 30.
            boundary: Boundary condition mode ('wrap' or 'fixed_zero'). Default is 'wrap'.

        Raises:
            TypeError: If rule is not an int or boundary is not a string.
            ValueError: If rule or boundary mode is invalid.
        """
        self.set_rule(rule)
        self.set_boundary(boundary)

    def set_rule(self, rule: int) -> None:
        """
        Reconfigures the engine's active Wolfram rule number.

        Args:
            rule: Wolfram rule number (0 to 255).

        Raises:
            TypeError: If rule is not an integer.
            ValueError: If rule is not in range [0, 255].
        """
        self._rule = validate_rule_number(rule)

    @property
    def rule(self) -> int:
        """Returns the active Wolfram rule number."""
        return self._rule

    def set_boundary(self, mode: str) -> None:
        """
        Sets the boundary condition mode for state evolution.

        Args:
            mode: Boundary mode ('wrap' or 'fixed_zero').

        Raises:
            TypeError: If mode is not a string.
            ValueError: If mode is not one of the supported boundary modes.
        """
        if not isinstance(mode, str):
            raise TypeError(f"Boundary mode must be a string, got {type(mode).__name__}")
        clean_mode = mode.strip().lower()
        if clean_mode not in self.SUPPORTED_BOUNDARIES:
            raise ValueError(
                f"Unsupported boundary mode '{mode}'. Supported modes are: {sorted(list(self.SUPPORTED_BOUNDARIES))}"
            )
        self._boundary = clean_mode

    @property
    def boundary(self) -> str:
        """Returns the active boundary mode."""
        return self._boundary

    def evolve(self, state: Any) -> List[int]:
        """
        Evolves a binary state by one step (round) using the active rule and boundary condition.

        Args:
            state: Binary state vector (list/tuple of bits or bit string).

        Returns:
            The evolved next-state bit vector as a list of integers (0 or 1).

        Raises:
            ValueError: If state is empty or contains non-binary values.
        """
        bits = validate_binary_state(state)
        n = len(bits)
        next_state = [0] * n

        if n == 1:
            # Single cell state handling
            if self._boundary == "wrap":
                left = bits[0]
                right = bits[0]
            else:  # fixed_zero
                left = 0
                right = 0
            next_state[0] = apply_rule(self._rule, left, bits[0], right)
            return next_state

        for i in range(n):
            # Determine left neighbor
            if i == 0:
                left = bits[n - 1] if self._boundary == "wrap" else 0
            else:
                left = bits[i - 1]

            center = bits[i]

            # Determine right neighbor
            if i == n - 1:
                right = bits[0] if self._boundary == "wrap" else 0
            else:
                right = bits[i + 1]

            next_state[i] = apply_rule(self._rule, left, center, right)

        return next_state

    def evolve_rounds(self, state: Any, rounds: int) -> List[int]:
        """
        Evolves a binary state by a specified number of rounds.

        Args:
            state: Initial binary state vector.
            rounds: Number of evolution steps (must be >= 0).

        Returns:
            The resulting state bit vector after the specified rounds.

        Raises:
            TypeError: If rounds is not an integer.
            ValueError: If rounds < 0 or state is invalid.
        """
        if not isinstance(rounds, int) or isinstance(rounds, bool):
            raise TypeError(f"Rounds must be an integer, got {type(rounds).__name__}")
        if rounds < 0:
            raise ValueError(f"Rounds must be non-negative (>= 0), got {rounds}")

        current_state = validate_binary_state(state)
        for _ in range(rounds):
            current_state = self.evolve(current_state)
        return current_state
