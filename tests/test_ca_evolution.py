"""Unit tests for Dynamic Cellular Automata Evolution & Scheduler (crypto/ca/evolution.py)."""

import pytest
from crypto.ca.dynamic_rules import DynamicRuleEngine
from crypto.ca.evolution import (
    BOUNDARY_FIXED,
    BOUNDARY_NULL,
    BOUNDARY_PERIODIC,
    BOUNDARY_REFLECTIVE,
    DynamicEvolutionEngine,
    EvolutionError,
    InvalidNeighborhoodError,
    InvalidSchedulerError,
    RuleEvolutionScheduler,
    get_neighborhood,
)


class TestAdaptiveNeighborhoods:
    """Tests for adaptive neighborhood extraction and boundary conditions."""

    def test_radius1_periodic_boundary(self):
        """Verify Radius 1 periodic boundary wrapping."""
        state = [1, 0, 0, 1]  # len=4
        # index 0: left=1 (state[3]), center=1, right=0 -> (1, 1, 0)
        assert get_neighborhood(state, 0, radius=1, boundary=BOUNDARY_PERIODIC) == (1, 1, 0)
        # index 3: left=0, center=1, right=1 (state[0]) -> (0, 1, 1)
        assert get_neighborhood(state, 3, radius=1, boundary=BOUNDARY_PERIODIC) == (0, 1, 1)

    def test_radius1_null_boundary(self):
        """Verify Radius 1 null boundary zero-padding."""
        state = [1, 0, 0, 1]
        assert get_neighborhood(state, 0, radius=1, boundary=BOUNDARY_NULL) == (0, 1, 0)
        assert get_neighborhood(state, 3, radius=1, boundary=BOUNDARY_NULL) == (0, 1, 0)

    def test_radius1_fixed_boundary(self):
        """Verify Radius 1 fixed boundary padding value (0 or 1)."""
        state = [1, 0, 0, 1]
        assert get_neighborhood(state, 0, radius=1, boundary=BOUNDARY_FIXED, pad_value=1) == (1, 1, 0)

    def test_radius1_reflective_boundary(self):
        """Verify Radius 1 reflective boundary mirroring."""
        state = [1, 0, 0, 1]
        # index 0: pos=-1 mirrors to index 0 (val=1) -> (1, 1, 0)
        assert get_neighborhood(state, 0, radius=1, boundary=BOUNDARY_REFLECTIVE) == (1, 1, 0)
        # index 3: pos=4 mirrors to index 3 (val=1) -> (0, 1, 1)
        assert get_neighborhood(state, 3, radius=1, boundary=BOUNDARY_REFLECTIVE) == (0, 1, 1)

    def test_radius2_periodic_boundary(self):
        """Verify Radius 2 (5-cell) periodic boundary wrapping."""
        state = [1, 0, 1, 0, 0]  # len=5
        # index 0: offset -2 -> index 3 (0), offset -1 -> index 4 (0), 0, 1, 2 -> (0, 0, 1, 0, 1)
        assert get_neighborhood(state, 0, radius=2, boundary=BOUNDARY_PERIODIC) == (0, 0, 1, 0, 1)

    def test_invalid_boundary_or_radius(self):
        """Verify invalid boundary name or radius raises InvalidNeighborhoodError."""
        state = [1, 0, 1]
        with pytest.raises(InvalidNeighborhoodError):
            get_neighborhood(state, 0, radius=3)
        with pytest.raises(InvalidNeighborhoodError):
            get_neighborhood(state, 0, radius=1, boundary="invalid_boundary")


class TestRuleEvolutionScheduler:
    """Tests for RuleEvolutionScheduler modes and deterministic behavior."""

    def test_fixed_scheduler(self):
        """Verify fixed mode returns constant rule ID."""
        sched = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_FIXED, rule=90)
        assert [sched.next_rule() for _ in range(5)] == [90, 90, 90, 90, 90]

    def test_cyclic_scheduler(self):
        """Verify cyclic mode loops through rule sequence."""
        seq = [30, 90, 150]
        sched = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_CYCLIC, rules_sequence=seq)
        assert [sched.next_rule() for _ in range(7)] == [30, 90, 150, 30, 90, 150, 30]

    def test_random_seeded_scheduler_determinism(self):
        """Verify random seeded mode produces 100% reproducible sequence."""
        sched1 = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_RANDOM_SEEDED, seed_value=12345)
        sched2 = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_RANDOM_SEEDED, seed_value=12345)

        res1 = [sched1.next_rule() for _ in range(10)]
        res2 = [sched2.next_rule() for _ in range(10)]

        assert res1 == res2

    def test_key_dependent_scheduler_determinism(self):
        """Verify key dependent mode derives reproducible rule schedule from key bytes."""
        key = b"secret_key_bytes_12345"
        sched1 = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_KEY_DEPENDENT, seed_value=key)
        sched2 = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_KEY_DEPENDENT, seed_value=key)

        res1 = [sched1.next_rule() for _ in range(20)]
        res2 = [sched2.next_rule() for _ in range(20)]

        assert res1 == res2
        assert len(res1) == 20

    def test_user_defined_callback_scheduler(self):
        """Verify user defined mode with custom callback function."""
        # Rule 30 for even steps, Rule 90 for odd steps
        cb = lambda step: 30 if step % 2 == 0 else 90
        sched = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_USER_DEFINED, user_callback=cb)

        assert [sched.next_rule() for _ in range(4)] == [30, 90, 30, 90]

    def test_export_schedule_non_destructive(self):
        """Verify export_schedule returns schedule without advancing internal counter."""
        seq = [30, 90, 150]
        sched = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_CYCLIC, rules_sequence=seq)

        exported = sched.export_schedule(5)
        assert exported == [30, 90, 150, 30, 90]

        # Verify next_rule starts from step 0
        assert sched.next_rule() == 30


class TestDynamicEvolutionEngine:
    """Tests for DynamicEvolutionEngine execution and hybrid evolutions."""

    def test_single_rule_evolution(self):
        """Verify single rule evolution matches expected Rule 30 behavior."""
        engine = DynamicEvolutionEngine()
        init_state = [0, 0, 0, 1, 0, 0, 0]
        evolved = engine.evolve(init_state, rule_or_scheduler=30, generations=1)
        # Rule 30 on single 1 bit in 7 cells (periodic): [0, 0, 1, 1, 1, 0, 0]
        assert evolved == [0, 0, 1, 1, 1, 0, 0]

    def test_hybrid_rule_execution(self):
        """Verify hybrid rule transition sequence (Rule 30 -> Rule 90 -> Rule 150)."""
        engine = DynamicEvolutionEngine()
        init_state = [0, 0, 1, 0, 0]

        # Evolve Rule 30 for 2 steps, then Rule 90 for 2 steps
        hybrid_seq = [(30, 2), (90, 2)]
        res_hybrid = engine.evolve_hybrid(init_state, hybrid_schedule=hybrid_seq)

        # Step manual evolution for validation
        s = engine.evolve(init_state, rule_or_scheduler=30, generations=2)
        s_expected = engine.evolve(s, rule_or_scheduler=90, generations=2)

        assert res_hybrid == s_expected

    def test_empty_state_raises_error(self):
        """Verify empty state input raises InvalidNeighborhoodError."""
        engine = DynamicEvolutionEngine()
        with pytest.raises(InvalidNeighborhoodError):
            engine.evolve([])

    def test_invalid_generations_raises_error(self):
        """Verify generations < 1 raises EvolutionError."""
        engine = DynamicEvolutionEngine()
        with pytest.raises(EvolutionError):
            engine.evolve([1, 0, 1], generations=0)
