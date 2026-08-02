"""
Integration Pipeline Module for KDR-CA-AEAD.

Combines Key Expansion (Phase 1.3), Dynamic Rule Scheduler (Phase 1.2),
Cellular Automata Engine (Phase 1.1), and Statistical Analysis Toolkit (Phase 1.4)
into a unified deterministic cryptographic simulation pipeline.
"""

from typing import Any, Dict, List, Union

from crypto.analysis.report import AnalysisReport
from crypto.ca.engine import CellularAutomataEngine
from crypto.ca.utils import random_binary_state
from crypto.key.expansion import KeyExpansion
from crypto.scheduler.scheduler import DynamicRuleScheduler


class KDRPipeline:
    """
    Unified Cryptographic Integration Pipeline.

    Workflow:
    Key -> KeyExpansion -> RoundKeys -> DynamicRuleScheduler -> CA Engine -> AnalysisReport
    """

    def __init__(
        self,
        key: Union[str, bytes, bytearray],
        encoding: str = "utf-8",
        rounds: int = 100,
        state_size: int = 512,
        boundary: str = "wrap",
        seed: Union[int, None] = None,
    ) -> None:
        """
        Initializes the KDR-CA-AEAD integration pipeline.

        Args:
            key: Secret key material as str, bytes, or bytearray.
            encoding: Key encoding format ('utf-8', 'hex', 'raw'). Default is 'utf-8'.
            rounds: Number of CA evolution rounds. Default is 100.
            state_size: Length of binary CA lattice state in bits. Default is 512.
            boundary: CA lattice boundary condition ('wrap' or 'fixed_zero'). Default is 'wrap'.
            seed: Optional integer seed for reproducible initial state generation.

        Raises:
            TypeError: If input types are invalid.
            ValueError: If rounds or state_size <= 0.
        """
        if isinstance(rounds, bool) or not isinstance(rounds, int) or rounds <= 0:
            raise ValueError(f"Rounds must be a positive integer, got {rounds}")
        if isinstance(state_size, bool) or not isinstance(state_size, int) or state_size <= 0:
            raise ValueError(f"State size must be a positive integer, got {state_size}")

        self._key = key
        self._encoding = encoding
        self._rounds = rounds
        self._state_size = state_size
        self._boundary = boundary
        self._seed = seed

        self._initial_state: List[int] = []
        self._final_state: List[int] = []
        self._rule_schedule: List[int] = []
        self._round_keys: List[bytes] = []
        self._analysis_data: Dict[str, Any] = {}

    def run(self) -> Dict[str, Any]:
        """
        Executes the end-to-end cryptographic pipeline.

        Returns:
            Dictionary containing 'initial_state', 'final_state', 'rule_schedule', 'round_keys', 'analysis'.
        """
        # Step 1: Key Expansion
        expansion = KeyExpansion(self._key, encoding=self._encoding, rounds=self._rounds, key_size=32)
        self._round_keys = expansion.all_round_keys()

        # Step 2: Dynamic Rule Scheduler
        scheduler = DynamicRuleScheduler(self._round_keys[0], rounds=self._rounds)
        self._rule_schedule = scheduler.generate_schedule(self._rounds)

        # Step 3: Initial State Generation & CA Engine Evolution
        self._initial_state = random_binary_state(self._state_size, seed=self._seed)
        engine = CellularAutomataEngine(boundary=self._boundary)
        current_state = list(self._initial_state)

        for rule in self._rule_schedule:
            engine.set_rule(rule)
            current_state = engine.evolve(current_state)

        self._final_state = current_state

        # Step 4: Statistical Analysis Report
        report_gen = AnalysisReport()
        self._analysis_data = report_gen.generate(self._final_state)

        return {
            "initial_state": list(self._initial_state),
            "final_state": list(self._final_state),
            "rule_schedule": list(self._rule_schedule),
            "round_keys": list(self._round_keys),
            "analysis": dict(self._analysis_data),
        }

    def initial_state(self) -> List[int]:
        """Returns a copy of the initial binary state."""
        return list(self._initial_state)

    def final_state(self) -> List[int]:
        """Returns a copy of the final evolved binary state."""
        return list(self._final_state)

    def rule_schedule(self) -> List[int]:
        """Returns a copy of the generated rule schedule."""
        return list(self._rule_schedule)

    def round_keys(self) -> List[bytes]:
        """Returns a copy of the generated round keys."""
        return list(self._round_keys)

    def analysis(self) -> Dict[str, Any]:
        """Returns a copy of the analysis report dictionary."""
        return dict(self._analysis_data)
