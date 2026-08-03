"""End-to-End Integration Tests for Phase 2.1 CA Subsystem Components.

Validates end-to-end interactions between:
- DynamicRuleEngine
- RuleEvolutionScheduler
- DynamicEvolutionEngine
- OptimizedCAEngine
- CABenchmark
"""

import pytest
from crypto.ca.benchmark import CABenchmark
from crypto.ca.dynamic_rules import DynamicRuleEngine, RuleDefinition
from crypto.ca.evolution import (
    BOUNDARY_NULL,
    BOUNDARY_PERIODIC,
    BOUNDARY_REFLECTIVE,
    DynamicEvolutionEngine,
    RuleEvolutionScheduler,
)
from crypto.ca.optimizer import OptimizedCAEngine, pack_bits, unpack_bits


class TestPhase2CAIntegration:
    """Integration test suite connecting all Phase 2.1 CA modules."""

    def test_full_pipeline_workflow(self):
        """Exercise full end-to-end workflow from rule registration to benchmark report."""
        # 1. Custom Rule Registration in DynamicRuleEngine
        rule_engine = DynamicRuleEngine(preload_wolfram=True)
        # Register custom rule: 3-cell majority rule
        rule_engine.register_rule(
            rule_id="majority_3",
            rule_definition=lambda nh: 1 if sum(nh) >= 2 else 0,
            name="3-cell Majority",
            radius=1,
        )

        assert "majority_3" in rule_engine.list_rules()
        rule_def = rule_engine.get_rule("majority_3")
        assert rule_def.evaluate((1, 1, 0)) == 1

        # 2. Configure RuleEvolutionScheduler with Cyclic mode
        scheduler = RuleEvolutionScheduler(
            mode=RuleEvolutionScheduler.MODE_CYCLIC,
            rules_sequence=[30, "majority_3", 90],
        )

        # 3. Initialize DynamicEvolutionEngine
        dyn_engine = DynamicEvolutionEngine(rule_engine=rule_engine, scheduler=scheduler, boundary=BOUNDARY_PERIODIC)

        init_state = [1, 0, 0, 1, 1, 0, 1, 0]

        # Evolve for 6 generations (cycles 30 -> majority_3 -> 90 -> 30 -> majority_3 -> 90)
        evolved_state = dyn_engine.evolve(init_state, generations=6)

        assert len(evolved_state) == 8
        assert set(evolved_state).issubset({0, 1})

        # 4. Compare standard wolfram steps against OptimizedCAEngine
        opt_engine = OptimizedCAEngine()
        opt_evolved = opt_engine.evolve_fast(init_state, rule=30, generations=5, boundary=BOUNDARY_PERIODIC)
        dyn_single = dyn_engine.evolve(init_state, rule_or_scheduler=30, generations=5)

        assert opt_evolved == dyn_single

        # 5. Bit packing verification
        packed = pack_bits(opt_evolved)
        unpacked = unpack_bits(packed, length=len(opt_evolved))
        assert unpacked == opt_evolved

        # 6. Benchmark execution & report generation
        benchmark = CABenchmark()
        res = benchmark.benchmark_rule(rule_id=30, state_size=500, generations=50, engine_type="optimized")
        report = benchmark.generate_report([res], format="markdown")

        assert "Cellular Automata Performance Benchmark Report" in report
        assert res.execution_time_seconds > 0

    def test_key_dependent_deterministic_reproducibility(self):
        """Verify key-dependent schedule produces 100% deterministic evolution output across runs."""
        secret_key = b"crypto_master_secret_key_2026"
        state = [0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0]

        # Run 1
        sched1 = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_KEY_DEPENDENT, seed_value=secret_key)
        eng1 = DynamicEvolutionEngine(scheduler=sched1)
        res1 = eng1.evolve(state, generations=20)

        # Run 2
        sched2 = RuleEvolutionScheduler(mode=RuleEvolutionScheduler.MODE_KEY_DEPENDENT, seed_value=secret_key)
        eng2 = DynamicEvolutionEngine(scheduler=sched2)
        res2 = eng2.evolve(state, generations=20)

        assert res1 == res2
