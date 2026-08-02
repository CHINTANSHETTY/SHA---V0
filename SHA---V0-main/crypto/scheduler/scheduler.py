"""
Dynamic Rule Scheduler Module for KDR-CA-AEAD.

Derives deterministic, key-dependent Cellular Automata rule schedules using
iterative SHA-512 hashing and rule diversity optimization.
"""

import hashlib
from typing import Any, Dict, List, Union

from crypto.scheduler.exceptions import (
    InvalidKeyError,
    ScheduleExhaustedError,
    SchedulerError,
)
from crypto.scheduler.mapping import bytes_to_rules


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

    def __init__(
        self,
        key: Union[str, bytes, bytearray],
        encoding: str = "utf-8",
        rounds: int = 64,
    ) -> None:
        """
        Initializes the Dynamic Rule Scheduler.

        Args:
            key: Secret key material as string, bytes, or bytearray.
            encoding: Encoding format if key is string ('utf-8', 'raw', 'bytes', 'hex'). Default is 'utf-8'.
            rounds: Default number of CA rule rounds to schedule (must be > 0). Default is 64.

        Raises:
            TypeError: If key or encoding is invalid type.
            InvalidKeyError: If key is empty, hex string invalid, or encoding unsupported.
            ValueError: If rounds <= 0.
        """
        self._key_bytes = self._process_key(key, encoding)
        
        if isinstance(rounds, bool) or not isinstance(rounds, int):
            raise TypeError(f"Rounds must be an integer, got {type(rounds).__name__}")
        if rounds <= 0:
            raise ValueError(f"Rounds must be greater than 0, got {rounds}")

        self._rounds = rounds
        self._current_index = 0
        self._history_list: List[int] = []
        self._schedule: List[int] = []

        self.generate_schedule(self._rounds)

    def _process_key(self, key: Union[str, bytes, bytearray], encoding: str) -> bytes:
        """Helper to process and validate key input in various formats."""
        if not isinstance(encoding, str):
            raise TypeError(f"Encoding must be a string, got {type(encoding).__name__}")

        enc = encoding.strip().lower()
        if enc not in ("utf-8", "utf8", "hex", "raw", "bytes"):
            raise InvalidKeyError(f"Unsupported key encoding: '{encoding}'")

        if key is None:
            raise InvalidKeyError("Secret key cannot be None")

        if isinstance(key, (bytes, bytearray)):
            key_bytes = bytes(key)
        elif isinstance(key, str):
            if enc == "hex":
                clean_hex = key.strip()
                if clean_hex.startswith("0x") or clean_hex.startswith("0X"):
                    clean_hex = clean_hex[2:]
                try:
                    key_bytes = bytes.fromhex(clean_hex)
                except ValueError as e:
                    raise InvalidKeyError(f"Invalid hexadecimal key string: {e}")
            else:
                try:
                    key_bytes = key.encode("utf-8")
                except UnicodeEncodeError as e:
                    raise InvalidKeyError(f"Invalid UTF-8 key string: {e}")
        else:
            raise TypeError(f"Secret key must be str, bytes, or bytearray, got {type(key).__name__}")

        if len(key_bytes) == 0:
            raise InvalidKeyError("Secret key cannot be empty")

        return key_bytes

    @property
    def key(self) -> bytes:
        """Returns the raw processed key bytes."""
        return self._key_bytes

    @property
    def rounds(self) -> int:
        """Returns the configured default number of schedule rounds."""
        return self._rounds

    @property
    def schedule(self) -> List[int]:
        """Returns a copy of the generated rule schedule."""
        return list(self._schedule)

    def generate_schedule(self, rounds: Union[int, None] = None) -> List[int]:
        """
        Generates deterministic rule schedule of specified rounds using SHA-512 expansion.

        Block 1: D_1 = SHA512(key_bytes)
        Block k: D_k = SHA512(D_{k-1})

        Args:
            rounds: Optional number of rounds to generate. Defaults to configured self._rounds.

        Returns:
            List of scheduled Wolfram rule numbers.
        """
        if rounds is None:
            rounds = self._rounds

        if isinstance(rounds, bool) or not isinstance(rounds, int):
            raise TypeError(f"Rounds must be an integer, got {type(rounds).__name__}")
        if rounds <= 0:
            raise ValueError(f"Rounds must be greater than 0, got {rounds}")

        self._rounds = rounds
        raw_bytes = bytearray()
        previous_digest = self._key_bytes

        while len(raw_bytes) < rounds:
            digest = hashlib.sha512(previous_digest).digest()
            raw_bytes.extend(digest)
            previous_digest = digest

        selected_bytes = bytes(raw_bytes[:rounds])
        raw_rules = bytes_to_rules(selected_bytes)
        self._schedule = optimize_schedule(raw_rules)
        self._current_index = 0
        self._history_list = []
        return list(self._schedule)

    def next_rule(self) -> int:
        """
        Advances the scheduler pointer and returns the next CA rule in the schedule.

        Returns:
            The next Wolfram rule integer (0 to 255).

        Raises:
            ScheduleExhaustedError: If the schedule has been exhausted.
        """
        if self._current_index >= len(self._schedule):
            raise ScheduleExhaustedError("Schedule exhausted. Call reset() to restart schedule.")

        rule = self._schedule[self._current_index]
        self._history_list.append(rule)
        self._current_index += 1
        return rule

    def peek(self) -> int:
        """
        Returns the next CA rule in the schedule without consuming it.

        Returns:
            The next Wolfram rule integer (0 to 255).

        Raises:
            ScheduleExhaustedError: If the schedule has been exhausted.
        """
        if self._current_index >= len(self._schedule):
            raise ScheduleExhaustedError("Schedule exhausted. Cannot peek.")
        return self._schedule[self._current_index]

    def reset(self) -> None:
        """Resets the scheduler pointer to 0 and clears rule history."""
        self._current_index = 0
        self._history_list.clear()

    def remaining(self) -> List[int]:
        """Returns the list of remaining unconsumed rules in the schedule."""
        return list(self._schedule[self._current_index :])

    def history(self) -> List[int]:
        """Returns a copy of the list of rule numbers served so far."""
        return list(self._history_list)

    def get_history(self) -> List[int]:
        """Alias for history() for backward compatibility."""
        return self.history()

    def current_index(self) -> int:
        """Returns the current schedule index pointer."""
        return self._current_index

    def export(self) -> Dict[str, Any]:
        """
        Exports the scheduler state into a serializable dictionary format.

        Returns:
            Dictionary containing key_hash, rules, and rounds count.
        """
        key_hash = hashlib.sha512(self._key_bytes).hexdigest()
        return {
            "key_hash": key_hash,
            "rules": list(self._schedule),
            "rounds": len(self._schedule),
        }

    def import_schedule(self, data: Dict[str, Any]) -> None:
        """
        Imports and loads a schedule dictionary structure.

        Args:
            data: Dictionary containing 'rules' list.

        Raises:
            TypeError: If data is not a dict.
            ValueError: If data is invalid or missing required keys.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Exported data must be a dict, got {type(data).__name__}")
        if "rules" not in data or not isinstance(data["rules"], list):
            raise ValueError("Exported data must contain a 'rules' list")
        if len(data["rules"]) == 0:
            raise ValueError("Imported rules list cannot be empty")

        for r in data["rules"]:
            if isinstance(r, bool) or not isinstance(r, int) or not (0 <= r <= 255):
                raise ValueError(f"Imported rules list contains invalid rule value: {r}")

        self._schedule = list(data["rules"])
        self._rounds = len(self._schedule)
        self._current_index = 0
        self._history_list = []

    @classmethod
    def from_export(cls, data: Dict[str, Any]) -> "DynamicRuleScheduler":
        """
        Creates a DynamicRuleScheduler instance from exported dictionary structure.
        """
        instance = cls(key=b"placeholder_key_for_import")
        instance.import_schedule(data)
        return instance
