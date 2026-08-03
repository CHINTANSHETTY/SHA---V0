"""Dynamic Cellular Automata Evolution Engine, Schedulers, and Adaptive Neighborhoods.

This module implements the dynamic evolution engine for KDR-CA-AEAD, supporting:
- Runtime-selectable rules and dynamic rule switching.
- Adaptive neighborhood models (Radius 1 & 2).
- Configurable boundary conditions (Periodic, Null, Reflective, Fixed).
- Deterministic Rule Evolution Scheduling (Fixed, Cyclic, Seeded Random, Key-Derived, User-Defined).
- Hybrid rule execution with multi-rule transitions and step intervals.

Determinism & Security:
    All random generation uses isolated `random.Random(seed)` instances.
    Key-dependent scheduling uses explicit byte/int seed inputs without external dependencies.
"""

import hashlib
import random
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from .dynamic_rules import (
    CAError,
    DynamicRuleEngine,
    EvolutionError,
    InvalidNeighborhoodError,
    InvalidRuleError,
    InvalidSchedulerError,
    RuleDefinition,
    RuleNotFoundError,
)
from .utils import StateLike, validate_state_length

# =========================================================
# BOUNDARY CONDITION CONSTANTS
# =========================================================
BOUNDARY_PERIODIC: str = "periodic"
BOUNDARY_NULL: str = "null"
BOUNDARY_REFLECTIVE: str = "reflective"
BOUNDARY_FIXED: str = "fixed"
VALID_BOUNDARIES: Set[str] = {
    BOUNDARY_PERIODIC,
    BOUNDARY_NULL,
    BOUNDARY_REFLECTIVE,
    BOUNDARY_FIXED,
}

VALID_RADII: Set[int] = {1, 2}


def validate_boundary(boundary: Any) -> str:
    """Validate and normalize boundary condition name.

    Args:
        boundary: Boundary condition string.

    Returns:
        str: Normalized lowercase boundary string.

    Raises:
        InvalidNeighborhoodError: If boundary condition is unsupported.
    """
    if not isinstance(boundary, str):
        raise InvalidNeighborhoodError(f"Boundary condition must be a string, got {type(boundary).__name__}")

    norm = boundary.strip().lower()
    if norm not in VALID_BOUNDARIES:
        raise InvalidNeighborhoodError(
            f"Invalid boundary condition '{boundary}'. Supported boundaries: {sorted(VALID_BOUNDARIES)}"
        )
    return norm


def validate_radius(radius: Any) -> int:
    """Validate neighborhood radius.

    Args:
        radius: Radius integer (1 or 2).

    Returns:
        int: Validated radius.

    Raises:
        InvalidNeighborhoodError: If radius is not integer 1 or 2.
    """
    if isinstance(radius, bool) or not isinstance(radius, int):
        raise InvalidNeighborhoodError(f"Radius must be an integer, got {type(radius).__name__}")
    if radius not in VALID_RADII:
        raise InvalidNeighborhoodError(f"Unsupported radius {radius}. Supported radii: {sorted(VALID_RADII)}")
    return radius


# =========================================================
# ADAPTIVE NEIGHBORHOOD UTILITIES
# =========================================================
def get_neighborhood(
    state: List[int],
    index: int,
    radius: int = 1,
    boundary: str = BOUNDARY_PERIODIC,
    pad_value: int = 0,
) -> Tuple[int, ...]:
    """Extract neighborhood cells for a target cell index in a 1D state array.

    Args:
        state: Binary state list [0, 1, ...].
        index: Target cell index (0 to N-1).
        radius: Neighborhood radius (1 for 3-cell, 2 for 5-cell).
        boundary: Boundary condition ("periodic", "null", "reflective", "fixed").
        pad_value: Bit value (0 or 1) used for "fixed" boundary condition.

    Returns:
        Tuple[int, ...]: Extracted binary neighborhood tuple of length 2 * radius + 1.

    Raises:
        InvalidNeighborhoodError: If radius, boundary, or pad_value is invalid.
    """
    norm_radius = validate_radius(radius)
    norm_boundary = validate_boundary(boundary)
    if pad_value not in (0, 1):
        raise InvalidNeighborhoodError(f"pad_value must be 0 or 1, got {pad_value}")

    n = len(state)
    if n == 0:
        raise InvalidNeighborhoodError("State array cannot be empty")

    nh: List[int] = []
    for offset in range(-norm_radius, norm_radius + 1):
        pos = index + offset
        if 0 <= pos < n:
            nh.append(state[pos])
        else:
            if norm_boundary == BOUNDARY_PERIODIC:
                nh.append(state[pos % n])
            elif norm_boundary == BOUNDARY_NULL:
                nh.append(0)
            elif norm_boundary == BOUNDARY_FIXED:
                nh.append(pad_value)
            elif norm_boundary == BOUNDARY_REFLECTIVE:
                if pos < 0:
                    real_idx = -pos - 1
                    if real_idx >= n:
                        real_idx = n - 1
                else:  # pos >= n
                    real_idx = 2 * n - 1 - pos
                    if real_idx < 0:
                        real_idx = 0
                nh.append(state[real_idx])

    return tuple(nh)


# =========================================================
# RULE EVOLUTION SCHEDULER
# =========================================================
class RuleEvolutionScheduler:
    """Deterministic Rule Evolution Scheduler.

    Schedules cellular automata rules generation-by-generation using one of 5 modes:
    - "fixed": Uses a single rule for all generations.
    - "cyclic": Cycles through a sequence of rules periodically.
    - "random_seeded": Deterministically generates rules using an isolated random generator.
    - "key_dependent": Derives rules deterministically from input key bytes or integer seed.
    - "user_defined": Uses a custom list or callback function `Callable[[int], Union[int, str]]`.
    """

    MODE_FIXED: str = "fixed"
    MODE_CYCLIC: str = "cyclic"
    MODE_RANDOM_SEEDED: str = "random_seeded"
    MODE_KEY_DEPENDENT: str = "key_dependent"
    MODE_USER_DEFINED: str = "user_defined"

    VALID_MODES: Set[str] = {
        MODE_FIXED,
        MODE_CYCLIC,
        MODE_RANDOM_SEEDED,
        MODE_KEY_DEPENDENT,
        MODE_USER_DEFINED,
    }

    def __init__(
        self,
        mode: str = MODE_FIXED,
        rule: Optional[Union[int, str]] = 30,
        rules_sequence: Optional[List[Union[int, str]]] = None,
        seed_value: Optional[Union[int, bytes, str]] = None,
        candidate_rules: Optional[List[Union[int, str]]] = None,
        user_callback: Optional[Callable[[int], Union[int, str]]] = None,
    ) -> None:
        """Initialize RuleEvolutionScheduler.

        Args:
            mode: Scheduler mode ("fixed", "cyclic", "random_seeded", "key_dependent", "user_defined").
            rule: Rule ID for fixed mode (defaults to Rule 30).
            rules_sequence: List of rule IDs for cyclic mode or user_defined list mode.
            seed_value: Seed (int, bytes, str) for random_seeded or key_dependent mode.
            candidate_rules: Candidate list of rule IDs to sample from in random_seeded mode.
            user_callback: Callable taking step index -> rule ID for user_defined mode.
        """
        if mode not in self.VALID_MODES:
            raise InvalidSchedulerError(f"Invalid scheduler mode '{mode}'. Valid modes: {sorted(self.VALID_MODES)}")

        self._mode: str = mode
        self._step_counter: int = 0
        self._fixed_rule: Union[int, str] = rule if rule is not None else 30
        self._sequence: List[Union[int, str]] = list(rules_sequence) if rules_sequence else []
        self._candidate_rules: List[Union[int, str]] = list(candidate_rules) if candidate_rules else list(range(256))
        self._user_callback: Optional[Callable[[int], Union[int, str]]] = user_callback

        self._seed_value: Optional[Union[int, bytes, str]] = seed_value
        self._rng: random.Random = random.Random()
        self._derived_key_rules: List[Union[int, str]] = []

        if seed_value is not None:
            self.seed(seed_value)
        elif self._mode in (self.MODE_RANDOM_SEEDED, self.MODE_KEY_DEPENDENT):
            self.seed(42)

    def seed(self, seed_value: Union[int, bytes, str]) -> None:
        """Re-seed the deterministic generator or re-derive key-dependent rule schedule.

        Args:
            seed_value: Seed integer, byte sequence, or string.
        """
        self._seed_value = seed_value

        if isinstance(seed_value, bytes):
            # Convert bytes to deterministic integer seed
            seed_int = int.from_bytes(hashlib.sha256(seed_value).digest(), byteorder="big")
        elif isinstance(seed_value, str):
            seed_int = int.from_bytes(hashlib.sha256(seed_value.encode("utf-8")).digest(), byteorder="big")
        elif isinstance(seed_value, int):
            seed_int = seed_value
        else:
            raise InvalidSchedulerError(f"seed_value must be int, bytes, or str, got {type(seed_value).__name__}")

        self._rng = random.Random(seed_int)

        if self._mode == self.MODE_KEY_DEPENDENT:
            # Deterministically derive 256 rules from seed_value using SHA-256 stream expansion
            derived: List[Union[int, str]] = []
            block_idx = 0
            while len(derived) < 256:
                if isinstance(seed_value, bytes):
                    inp = seed_value + block_idx.to_bytes(4, byteorder="big")
                else:
                    inp = str(seed_value).encode("utf-8") + block_idx.to_bytes(4, byteorder="big")
                digest = hashlib.sha256(inp).digest()
                for byte_val in digest:
                    if self._candidate_rules:
                        derived.append(self._candidate_rules[byte_val % len(self._candidate_rules)])
                    else:
                        derived.append(byte_val)
                    if len(derived) >= 256:
                        break
                block_idx += 1
            self._derived_key_rules = derived

        self.reset()

    def reset(self) -> None:
        """Reset the step counter to 0."""
        self._step_counter = 0

    def next_rule(self) -> Union[int, str]:
        """Advance one generation and return the scheduled rule ID for that step.

        Returns:
            Union[int, str]: Scheduled rule ID.

        Raises:
            InvalidSchedulerError: If sequence is empty or user callback fails.
        """
        step = self._step_counter
        self._step_counter += 1

        if self._mode == self.MODE_FIXED:
            return self._fixed_rule

        elif self._mode == self.MODE_CYCLIC:
            if not self._sequence:
                raise InvalidSchedulerError("Cyclic scheduler requires a non-empty rules_sequence")
            return self._sequence[step % len(self._sequence)]

        elif self._mode == self.MODE_RANDOM_SEEDED:
            if not self._candidate_rules:
                raise InvalidSchedulerError("Random seeded scheduler requires non-empty candidate_rules")
            return self._rng.choice(self._candidate_rules)

        elif self._mode == self.MODE_KEY_DEPENDENT:
            if not self._derived_key_rules:
                raise InvalidSchedulerError("Key dependent scheduler has no derived rules")
            return self._derived_key_rules[step % len(self._derived_key_rules)]

        elif self._mode == self.MODE_USER_DEFINED:
            if self._user_callback is not None:
                try:
                    return self._user_callback(step)
                except Exception as err:
                    raise InvalidSchedulerError(f"User scheduler callback failed at step {step}: {err}") from err
            elif self._sequence:
                if step >= len(self._sequence):
                    raise InvalidSchedulerError(
                        f"User sequence exhausted at step {step} (len={len(self._sequence)})"
                    )
                return self._sequence[step]
            else:
                raise InvalidSchedulerError("User defined scheduler requires user_callback or non-empty rules_sequence")

        raise InvalidSchedulerError(f"Unknown scheduler mode '{self._mode}'")

    def export_schedule(self, length: int) -> List[Union[int, str]]:
        """Export the scheduled sequence of rule IDs for a given number of generations without mutating state.

        Args:
            length: Number of generations (>= 1).

        Returns:
            List[Union[int, str]]: List of rule IDs for steps 0 to length - 1.

        Raises:
            InvalidSchedulerError: If length < 1.
        """
        if length < 1:
            raise InvalidSchedulerError(f"Export schedule length must be >= 1, got {length}")

        saved_counter = self._step_counter
        # Save RNG state
        saved_rng_state = self._rng.getstate()

        try:
            schedule: List[Union[int, str]] = []
            for _ in range(length):
                schedule.append(self.next_rule())
            return schedule
        finally:
            self._step_counter = saved_counter
            self._rng.setstate(saved_rng_state)


# =========================================================
# DYNAMIC EVOLUTION ENGINE
# =========================================================
class DynamicEvolutionEngine:
    """Dynamic Cellular Automata Evolution Engine.

    Executes 1D cellular automata evolution supporting dynamic rule switching,
    rule schedulers, adaptive neighborhood models, and hybrid execution.
    """

    def __init__(
        self,
        rule_engine: Optional[DynamicRuleEngine] = None,
        scheduler: Optional[RuleEvolutionScheduler] = None,
        radius: int = 1,
        boundary: str = BOUNDARY_PERIODIC,
        pad_value: int = 0,
    ) -> None:
        """Initialize DynamicEvolutionEngine.

        Args:
            rule_engine: DynamicRuleEngine instance (creates default if None).
            scheduler: RuleEvolutionScheduler instance (creates default fixed Rule 30 if None).
            radius: Neighborhood radius (1 or 2).
            boundary: Boundary condition ("periodic", "null", "reflective", "fixed").
            pad_value: Bit value (0 or 1) for "fixed" boundary condition.
        """
        self.rule_engine: DynamicRuleEngine = rule_engine if rule_engine is not None else DynamicRuleEngine(preload_wolfram=True)
        self.scheduler: RuleEvolutionScheduler = scheduler if scheduler is not None else RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_FIXED, rule=30)
        self.radius: int = validate_radius(radius)
        self.boundary: str = validate_boundary(boundary)
        self.pad_value: int = pad_value

    def evolve_step(
        self,
        state: StateLike,
        rule_def: RuleDefinition,
        radius: Optional[int] = None,
        boundary: Optional[str] = None,
        pad_value: Optional[int] = None,
    ) -> List[int]:
        """Perform a single generation evolution step using a RuleDefinition.

        Args:
            state: Input state (list, tuple, or string of bits).
            rule_def: RuleDefinition object specifying rule and evaluation logic.
            radius: Optional override for neighborhood radius.
            boundary: Optional override for boundary condition.
            pad_value: Optional override for fixed boundary pad value.

        Returns:
            List[int]: New state array after 1 step of evolution.
        """
        if isinstance(state, str):
            curr_state = [int(c) for c in state]
        else:
            curr_state = list(state)

        if len(curr_state) == 0:
            raise InvalidNeighborhoodError("State array cannot be empty")

        rad = radius if radius is not None else rule_def.radius
        bound = boundary if boundary is not None else self.boundary
        pad = pad_value if pad_value is not None else self.pad_value

        n = len(curr_state)
        next_state: List[int] = [0] * n

        for i in range(n):
            nh = get_neighborhood(curr_state, i, radius=rad, boundary=bound, pad_value=pad)
            next_state[i] = rule_def.evaluate(nh)

        return next_state

    def evolve(
        self,
        state: StateLike,
        rule_or_scheduler: Optional[Union[int, str, RuleEvolutionScheduler]] = None,
        generations: int = 1,
        radius: Optional[int] = None,
        boundary: Optional[str] = None,
        pad_value: Optional[int] = None,
    ) -> List[int]:
        """Perform multi-generation dynamic evolution.

        Args:
            state: Initial binary state (list, tuple, or bit string).
            rule_or_scheduler: Optional rule ID, RuleEvolutionScheduler, or None (uses self.scheduler).
            generations: Number of generations to evolve (>= 1).
            radius: Optional neighborhood radius override.
            boundary: Optional boundary condition override.
            pad_value: Optional fixed boundary pad value override.

        Returns:
            List[int]: Final state array after evolution.

        Raises:
            EvolutionError: If generations < 1 or evolution fails.
        """
        if generations < 1:
            raise EvolutionError(f"Generations must be positive (>= 1), got {generations}")

        if isinstance(state, str):
            curr_state = [int(c) for c in state]
        else:
            curr_state = list(state)

        if len(curr_state) == 0:
            raise InvalidNeighborhoodError("State array cannot be empty")

        # Determine scheduler or single rule
        if isinstance(rule_or_scheduler, RuleEvolutionScheduler):
            sched = rule_or_scheduler
        elif rule_or_scheduler is not None and not isinstance(rule_or_scheduler, RuleEvolutionScheduler):
            sched = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_FIXED, rule=rule_or_scheduler)
        else:
            sched = self.scheduler

        for _ in range(generations):
            rule_id = sched.next_rule()
            rule_def = self.rule_engine.get_rule(rule_id)
            curr_state = self.evolve_step(curr_state, rule_def, radius=radius, boundary=boundary, pad_value=pad_value)

        return curr_state

    def evolve_hybrid(
        self,
        state: StateLike,
        hybrid_schedule: List[Tuple[Union[int, str], int]],
        radius: Optional[int] = None,
        boundary: Optional[str] = None,
        pad_value: Optional[int] = None,
    ) -> List[int]:
        """Perform hybrid rule execution using explicit rule transition intervals.

        Example hybrid_schedule: `[(30, 5), (90, 10), (150, 5)]`
        (Evolves Rule 30 for 5 steps, then Rule 90 for 10 steps, then Rule 150 for 5 steps).

        Args:
            state: Initial binary state.
            hybrid_schedule: List of (rule_id, step_count) tuples.
            radius: Optional neighborhood radius override.
            boundary: Optional boundary condition override.
            pad_value: Optional fixed boundary pad value override.

        Returns:
            List[int]: Final state array after hybrid execution.

        Raises:
            EvolutionError: If hybrid_schedule is empty or step_count < 1.
        """
        if not hybrid_schedule:
            raise EvolutionError("hybrid_schedule cannot be empty")

        if isinstance(state, str):
            curr_state = [int(c) for c in state]
        else:
            curr_state = list(state)

        for rule_id, step_count in hybrid_schedule:
            if step_count < 1:
                raise EvolutionError(f"Step count in hybrid schedule must be positive, got {step_count}")
            rule_def = self.rule_engine.get_rule(rule_id)
            for _ in range(step_count):
                curr_state = self.evolve_step(curr_state, rule_def, radius=radius, boundary=boundary, pad_value=pad_value)

        return curr_state
