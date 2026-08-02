"""
Dynamic Rule Scheduler Module for KDR-CA-AEAD.

Derives deterministic, key-dependent Cellular Automata rule schedules using
iterative SHA-512 hashing and rule diversity optimization.
"""

import hashlib
from typing import List, Union

from crypto.scheduler.mapping import map_bytes_to_rules


def optimize_schedule(schedule: List[int]) -> List[int]:
    """
    Optimizes a rule schedule to enforce rule diversity.

    Guarantees that no more than 3 identical consecutive rules occur in the schedule.
    The optimization is 100% deterministic and uses no randomness.

    Args:
        schedule: List of Wolfram CA rule integers (0 to 255).

    Returns:
        Optimized list of rule integers with no 4 identical consecutive rules.
    """
    if len(schedule) < 4:
        return list(schedule)

    optimized = list(schedule)
    for i in range(3, len(optimized)):
        if (
            optimized[i] == optimized[i - 1]
            and optimized[i] == optimized[i - 2]
            and optimized[i] == optimized[i - 3]
        ):
            # Deterministically alter rule to break long consecutive run
            candidate = (optimized[i] + 1) % 256
            while candidate == optimized[i - 1]:
                candidate = (candidate + 1) % 256
            optimized[i] = candidate

    return optimized


class DynamicRuleScheduler:
    """
    Keyed Dynamic Rule Scheduler for Cellular Automata.

    Generates deterministic pseudo-random sequences of CA rules derived from
    a secret key using iterative SHA-512 digest extension.
    """

    def __init__(self, key: Union[bytes, bytearray], rounds: int = 64) -> None:
        """
        Initializes the Dynamic Rule Scheduler.

        Args:
            key: Secret key material as bytes or bytearray.
            rounds: Number of CA rule rounds to schedule (must be > 0). Default is 64.

        Raises:
            TypeError: If key is not bytes/bytearray or rounds is not an integer.
            ValueError: If key is empty or rounds <= 0.
        """
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError(f"Secret key must be bytes or bytearray, got {type(key).__name__}")
        if len(key) == 0:
            raise ValueError("Secret key cannot be empty")

        if isinstance(rounds, bool) or not isinstance(rounds, int):
            raise TypeError(f"Rounds must be an integer, got {type(rounds).__name__}")
        if rounds <= 0:
            raise ValueError(f"Rounds must be greater than 0, got {rounds}")

        self._key = bytes(key)
        self._rounds = rounds
        self._current_index = 0
        self._history: List[int] = []
        self._schedule: List[int] = []

        self.generate_schedule()

    @property
    def key(self) -> bytes:
        """Returns the secret key material."""
        return self._key

    @property
    def rounds(self) -> int:
        """Returns the configured number of schedule rounds."""
        return self._rounds

    @property
    def schedule(self) -> List[int]:
        """Returns a copy of the generated rule schedule."""
        return list(self._schedule)

    def generate_schedule(self) -> List[int]:
        """
        Generates the deterministic rule schedule using iterative SHA-512 hashing.

        Block 1: D_1 = SHA512(key)
        Block k: D_k = SHA512(D_{k-1})

        Output rule bytes are mapped to rules and optimized for diversity.

        Returns:
            List of scheduled Wolfram rule numbers.
        """
        raw_bytes = bytearray()
        previous_digest = self._key

        while len(raw_bytes) < self._rounds:
            digest = hashlib.sha512(previous_digest).digest()
            raw_bytes.extend(digest)
            previous_digest = digest

        selected_bytes = bytes(raw_bytes[: self._rounds])
        raw_rules = map_bytes_to_rules(selected_bytes)
        self._schedule = optimize_schedule(raw_rules)
        self._current_index = 0
        self._history = []
        return list(self._schedule)

    def next_rule(self) -> int:
        """
        Advances the scheduler pointer and returns the next CA rule in the schedule.

        Returns:
            The next Wolfram rule integer (0 to 255).

        Raises:
            IndexError: If the schedule has been exhausted.
        """
        if self._current_index >= len(self._schedule):
            raise IndexError("Schedule exhausted. Call reset() to restart schedule.")

        rule = self._schedule[self._current_index]
        self._history.append(rule)
        self._current_index += 1
        return rule

    def reset(self) -> None:
        """Resets the scheduler pointer to 0 and clears rule history."""
        self._current_index = 0
        self._history.clear()

    def get_history(self) -> List[int]:
        """Returns a copy of the list of rule numbers served so far."""
        return list(self._history)

    def current_index(self) -> int:
        """Returns the current schedule index pointer."""
        return self._current_index
