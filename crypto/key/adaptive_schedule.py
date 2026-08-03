r"""Adaptive Key Scheduler and Forward-Secure Key Chains.

This module provides:
1. `AdaptiveKeyScheduler`: Dynamically schedules subkey derivations (round keys, session keys, context keys)
   by delegating key derivation logic to `KeyEvolutionEngine`.
2. `ForwardKeyChain`: Implements one-way forward-secure key ratcheting, where previous keys are dereferenced
   and overwritten to guarantee forward secrecy.
"""

import hashlib
import random
from typing import Any, Callable, Dict, List, Optional, Set, Union

from crypto.primitives.hkdf import hkdf_extract
from .evolution import (
    FORWARD_RATCHET_LABEL,
    InvalidContextError,
    InvalidKeyLengthError,
    KeyErrorBase,
    KeyEvolutionEngine,
    KeyEvolutionError,
)


# =========================================================
# EXCEPTION CLASSES
# =========================================================
class SchedulerError(KeyErrorBase, ValueError):
    """Raised when key scheduler configuration is invalid or depleted."""
    pass


class ChainDepletedError(KeyErrorBase, RuntimeError):
    """Raised when forward key chain limit has been reached."""
    pass


# =========================================================
# ADAPTIVE KEY SCHEDULER
# =========================================================
class AdaptiveKeyScheduler:
    """Adaptive Key Scheduler.

    Schedules subkey derivations generation-by-generation. Handles schedule ordering
    and delegates cryptographic derivation to `KeyEvolutionEngine`.
    """

    MODE_SEQUENTIAL: str = "sequential"
    MODE_CYCLIC: str = "cyclic"
    MODE_SESSION: str = "session"
    MODE_CONTEXT: str = "context"
    MODE_DETERMINISTIC_RANDOM: str = "deterministic_random"
    MODE_USER_DEFINED: str = "user_defined"

    VALID_MODES: Set[str] = {
        MODE_SEQUENTIAL,
        MODE_CYCLIC,
        MODE_SESSION,
        MODE_CONTEXT,
        MODE_DETERMINISTIC_RANDOM,
        MODE_USER_DEFINED,
    }

    def __init__(
        self,
        mode: str = MODE_SEQUENTIAL,
        round_sequence: Optional[List[int]] = None,
        session_sequence: Optional[List[str]] = None,
        context_sequence: Optional[List[bytes]] = None,
        seed_value: Optional[Union[int, bytes, str]] = None,
        user_callback: Optional[Callable[[int, KeyEvolutionEngine, bytes], bytes]] = None,
    ) -> None:
        """Initialize AdaptiveKeyScheduler.

        Args:
            mode: Scheduler mode ("sequential", "cyclic", "session", "context", "deterministic_random", "user_defined").
            round_sequence: List of round numbers for cyclic mode.
            session_sequence: List of session IDs for session mode.
            context_sequence: List of context byte objects for context mode.
            seed_value: Seed value for deterministic_random mode.
            user_callback: Custom derivation callback `(step, engine, master_key) -> bytes`.
        """
        if mode not in self.VALID_MODES:
            raise SchedulerError(f"Invalid scheduler mode '{mode}'. Valid modes: {sorted(self.VALID_MODES)}")

        self._mode: str = mode
        self._step_counter: int = 0
        self._round_sequence: List[int] = list(round_sequence) if round_sequence else []
        self._session_sequence: List[str] = list(session_sequence) if session_sequence else []
        self._context_sequence: List[bytes] = list(context_sequence) if context_sequence else []
        self._user_callback: Optional[Callable[[int, KeyEvolutionEngine, bytes], bytes]] = user_callback

        self._seed_value: Optional[Union[int, bytes, str]] = seed_value
        self._rng: random.Random = random.Random()
        if seed_value is not None:
            self.seed(seed_value)
        elif self._mode == self.MODE_DETERMINISTIC_RANDOM:
            self.seed(42)

    def seed(self, seed_value: Union[int, bytes, str]) -> None:
        """Seed the isolated random generator for deterministic_random mode.

        Args:
            seed_value: Seed integer, bytes, or string.
        """
        self._seed_value = seed_value
        if isinstance(seed_value, bytes):
            seed_int = int.from_bytes(hashlib.sha256(seed_value).digest(), byteorder="big")
        elif isinstance(seed_value, str):
            seed_int = int.from_bytes(hashlib.sha256(seed_value.encode("utf-8")).digest(), byteorder="big")
        elif isinstance(seed_value, int):
            seed_int = seed_value
        else:
            raise SchedulerError(f"seed_value must be int, bytes, or str, got {type(seed_value).__name__}")

        self._rng = random.Random(seed_int)
        self.reset()

    def reset(self) -> None:
        """Reset step counter to 0."""
        self._step_counter = 0

    def next_key(self, engine: KeyEvolutionEngine, master_key: bytes) -> bytes:
        """Advance one step and derive the scheduled key using KeyEvolutionEngine.

        Args:
            engine: KeyEvolutionEngine instance.
            master_key: Master key bytes.

        Returns:
            bytes: Derived subkey.

        Raises:
            SchedulerError: If scheduler configuration or step parameter is invalid.
        """
        step = self._step_counter
        self._step_counter += 1

        if self._mode == self.MODE_SEQUENTIAL:
            return engine.derive_round_key(master_key, round_num=step)

        elif self._mode == self.MODE_CYCLIC:
            if not self._round_sequence:
                raise SchedulerError("Cyclic mode requires a non-empty round_sequence")
            round_val = self._round_sequence[step % len(self._round_sequence)]
            return engine.derive_round_key(master_key, round_num=round_val)

        elif self._mode == self.MODE_SESSION:
            if not self._session_sequence:
                raise SchedulerError("Session mode requires a non-empty session_sequence")
            sess_id = self._session_sequence[step % len(self._session_sequence)]
            return engine.derive_session_key(master_key, session_id=sess_id)

        elif self._mode == self.MODE_CONTEXT:
            if not self._context_sequence:
                raise SchedulerError("Context mode requires a non-empty context_sequence")
            ctx = self._context_sequence[step % len(self._context_sequence)]
            return engine.derive_context_key(master_key, context=ctx)

        elif self._mode == self.MODE_DETERMINISTIC_RANDOM:
            random_round = self._rng.randint(0, 1000000)
            return engine.derive_round_key(master_key, round_num=random_round)

        elif self._mode == self.MODE_USER_DEFINED:
            if self._user_callback is None:
                raise SchedulerError("User defined mode requires user_callback")
            try:
                return self._user_callback(step, engine, master_key)
            except Exception as err:
                raise SchedulerError(f"User callback failed at step {step}: {err}") from err

        raise SchedulerError(f"Unknown scheduler mode '{self._mode}'")

    def export_schedule(self, engine: KeyEvolutionEngine, master_key: bytes, length: int) -> List[bytes]:
        """Export scheduled key sequence for specified number of steps without mutating state.

        Args:
            engine: KeyEvolutionEngine instance.
            master_key: Master key bytes.
            length: Number of steps to export (>= 1).

        Returns:
            List[bytes]: List of derived keys.
        """
        if length < 1:
            raise SchedulerError(f"Export length must be >= 1, got {length}")

        saved_counter = self._step_counter
        saved_rng_state = self._rng.getstate()
        try:
            schedule: List[bytes] = []
            for _ in range(length):
                schedule.append(self.next_key(engine, master_key))
            return schedule
        finally:
            self._step_counter = saved_counter
            self._rng.setstate(saved_rng_state)


# =========================================================
# FORWARD SECURE KEY CHAIN
# =========================================================
class ForwardKeyChain:
    r"""Forward-Secure Key Chain.

    Implements one-way ratcheting progression ($K_0 \to K_1 \to \dots \to K_n$) where
    previous keys are dereferenced and overwritten (overwriting bytearray buffers) upon ratcheting.
    """

    def __init__(self, initial_key: Optional[bytes] = None, chain_length: int = 100) -> None:
        """Initialize ForwardKeyChain.

        Args:
            initial_key: Optional initial master key.
            chain_length: Maximum allowed ratchets (defaults to 100).
        """
        self._current_key_buf: Optional[bytearray] = None
        self._step_count: int = 0
        self._max_chain_length: int = chain_length

        if initial_key is not None:
            self.initialize(initial_key, chain_length=chain_length)

    def initialize(self, initial_key: bytes, chain_length: int = 100) -> None:
        """Initialize or reset key chain with a new key and chain limit.

        Args:
            initial_key: Non-empty bytes object of at least 16 bytes.
            chain_length: Positive maximum chain length (>= 1).

        Raises:
            InvalidContextError: If initial_key is invalid.
        """
        if not initial_key or not isinstance(initial_key, (bytes, bytearray)):
            raise InvalidContextError("initial_key must be a non-empty bytes-like object")
        if len(initial_key) < 16:
            raise InvalidContextError(f"initial_key must be at least 16 bytes, got {len(initial_key)}")
        if chain_length < 1:
            raise InvalidContextError(f"chain_length must be >= 1, got {chain_length}")

        # Wiping old key buffer if present
        self._wipe_current_key()

        self._current_key_buf = bytearray(initial_key)
        self._step_count = 0
        self._max_chain_length = chain_length

    def _wipe_current_key(self) -> None:
        """Overwrite current key bytearray with zeros to best effort wipe memory."""
        if self._current_key_buf is not None:
            for i in range(len(self._current_key_buf)):
                self._current_key_buf[i] = 0
            self._current_key_buf = None

    def current_key(self) -> bytes:
        """Return the current key in the chain without advancing.

        Returns:
            bytes: Current active key bytes.

        Raises:
            ChainDepletedError: If key chain is uninitialized.
        """
        if self._current_key_buf is None:
            raise ChainDepletedError("ForwardKeyChain is uninitialized or depleted")
        return bytes(self._current_key_buf)

    def next_key(self) -> bytes:
        """Perform one-way ratchet step and return the new active key.

        Overwrites old key memory buffer to enforce forward secrecy.

        Returns:
            bytes: Next key after ratcheting.

        Raises:
            ChainDepletedError: If chain length limit reached or uninitialized.
        """
        if self._current_key_buf is None:
            raise ChainDepletedError("ForwardKeyChain is uninitialized or depleted")

        if self._step_count >= self._max_chain_length:
            self._wipe_current_key()
            raise ChainDepletedError(f"ForwardKeyChain reached maximum chain length ({self._max_chain_length})")

        # One-way HKDF-Extract ratchet step
        next_key_bytes = hkdf_extract(salt=FORWARD_RATCHET_LABEL, ikm=bytes(self._current_key_buf))

        # Best effort memory overwrite of previous key
        self._wipe_current_key()

        self._current_key_buf = bytearray(next_key_bytes)
        self._step_count += 1
        return bytes(self._current_key_buf)

    def checkpoint(self) -> Dict[str, Any]:
        """Export current key chain metadata (step counter & max length) without exposing key material.

        Returns:
            Dict[str, Any]: Metadata state dictionary.
        """
        return {
            "step_count": self._step_count,
            "max_chain_length": self._max_chain_length,
            "is_active": self._current_key_buf is not None,
        }
