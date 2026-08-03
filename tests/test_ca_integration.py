"""Integration tests for Cellular Automata Subsystem (crypto/ca).

Tests public API completeness, cross-module integration workflows, determinism,
error propagation, and performance smoke tests across rules, engine, utils, and mapping.
"""

import pytest

import crypto.ca as ca


class TestPublicAPI:
    """Tests for package exports, metadata, and public API surface."""

    def test_metadata(self):
        """Verify package version and author metadata."""
        assert hasattr(ca, "__version__")
        assert ca.__version__ == "1.0.0"
        assert hasattr(ca, "__author__")
        assert ca.__author__ == "KDR-CA-AEAD Project"

    def test_all_exports_exist(self):
        """Verify that every symbol in __all__ exists as an attribute on crypto.ca."""
        assert hasattr(ca, "__all__")
        assert len(ca.__all__) > 0
        for symbol in ca.__all__:
            assert hasattr(ca, symbol), f"Exported symbol '{symbol}' not found in crypto.ca"

    def test_no_private_symbols_in_all(self):
        """Verify that no private functions (starting with single '_') are exposed in __all__."""
        for symbol in ca.__all__:
            if symbol.startswith("__") and symbol.endswith("__"):
                continue
            assert not symbol.startswith("_"), f"Private symbol '{symbol}' should not be in __all__"
        assert "_validate_state" not in ca.__all__
        assert "_get_rule_table_proxy" not in ca.__all__


class TestCrossModuleIntegration:
    """Tests for end-to-end multi-module Cellular Automata pipelines."""

    def test_end_to_end_evolution_pipeline(self):
        """Test complete pipeline: int_to_state -> parse_rule -> evolve -> metrics -> state_to_string -> state_to_int."""
        # 1. State creation
        initial_val = 42
        width = 8
        state = ca.int_to_state(initial_val, width=width)
        assert state == [0, 0, 1, 0, 1, 0, 1, 0]

        # 2. Rule parsing & validation
        rule = 30
        table = ca.parse_rule(rule)
        assert len(table) == 8

        # 3. Evolution
        generations = 5
        evolved_state = ca.evolve(state, rule=rule, generations=generations, boundary="periodic")
        assert len(evolved_state) == width

        # 4. Metrics & Conversions
        pop_count = ca.population_count(evolved_state)
        h_dist = ca.hamming_distance(state, evolved_state)
        state_str = ca.state_to_string(evolved_state)
        final_val = ca.state_to_int(evolved_state)

        assert isinstance(pop_count, int)
        assert isinstance(h_dist, int)
        assert isinstance(state_str, str)
        assert isinstance(final_val, int)
        assert len(state_str) == width

    def test_mapping_and_dynamic_evolution_pipeline(self):
        """Test pipeline combining rule sequence generation, bijective mapping, lookup, and evolution."""
        # Generate source and target rule sequences
        source_rules = ca.generate_rule_sequence(start_rule=30, count=3, step=30)
        target_rules = ca.generate_rule_sequence(start_rule=100, count=3, step=20)
        assert source_rules == [30, 60, 90]
        assert target_rules == [100, 120, 140]

        # Build lookup and mapping
        lookup = ca.build_rule_lookup(source_rules)
        mapping = ca.map_rules(source_rules, target_rules, bijective=True)
        inverted = ca.invert_rule_mapping(mapping)
        assert inverted[100] == 30

        # Evolve state step-by-step using mapped rules
        current_state = ca.state_from_string("0001000")
        for idx in range(len(source_rules)):
            r = ca.get_rule(idx, lookup)
            current_state = ca.evolve(current_state, rule=r, generations=1, boundary="periodic")

        assert len(current_state) == 7
        assert ca.population_count(current_state) > 0

    def test_matrix_history_and_serialization_pipeline(self):
        """Test pipeline combining seeded random state, multi-gen evolution history matrix, and JSON serialization."""
        initial_state = ca.random_state(length=16, seed=98765)
        rule = 90  # Sierpinski rule

        history = [initial_state]
        curr = initial_state
        for _ in range(4):
            curr = ca.evolve(curr, rule=rule, generations=1, boundary="periodic")
            history.append(curr)

        matrix = ca.states_to_matrix(history)
        assert len(matrix) == 5
        for row in matrix:
            assert len(row) == 16

        # Serialize rule configuration
        rules = [30, 90, 110]
        json_data = ca.serialize_rule_sequence(
            rules=rules,
            default_rule=30,
            active_rule=90,
            metadata={"experiment": "KDR-CA-Phase1"},
            indent=2,
        )

        # Deserialize back
        deserialized = ca.deserialize_rule_sequence(json_data)
        assert deserialized["rules"] == rules
        assert deserialized["active_rule"] == 90
        assert deserialized["metadata"]["experiment"] == "KDR-CA-Phase1"


class TestDeterminismAndSmoke:
    """Tests for 100-run determinism and large state performance smoke tests."""

    def test_workflow_determinism_100_runs(self):
        """Verify identical results across 100 repeated executions of complex workflow."""
        seed_val = 123456
        ref_state = ca.random_state(32, seed=seed_val)
        ref_result = ca.evolve(ref_state, rule=30, generations=10, boundary="periodic")
        ref_str = ca.state_to_string(ref_result)

        for _ in range(100):
            st = ca.random_state(32, seed=seed_val)
            res = ca.evolve(st, rule=30, generations=10, boundary="periodic")
            res_str = ca.state_to_string(res)
            assert res == ref_result
            assert res_str == ref_str

    def test_performance_smoke_test_10k_cells(self):
        """Smoke test: Evolve 10,000 cells over 100 generations without errors."""
        large_state = ca.zero_state(10000)
        large_state[5000] = 1

        final_state = ca.evolve(large_state, rule=30, generations=100, boundary="periodic")
        assert len(final_state) == 10000
        assert ca.population_count(final_state) > 1


class TestErrorPropagation:
    """Tests for error propagation across module boundaries."""

    def test_invalid_rule_propagation(self):
        """Verify invalid rule raises ValueError when passed to evolve."""
        with pytest.raises(ValueError, match="Rule must be between 0 and 255"):
            ca.evolve([0, 1, 0], rule=300)

    def test_invalid_state_propagation(self):
        """Verify invalid state raises ValueError or TypeError when passed to evolve."""
        with pytest.raises(ValueError, match="must be 0 or 1"):
            ca.evolve([0, 2, 0], rule=30)
        with pytest.raises(TypeError, match="State cannot be None"):
            ca.evolve(None, rule=30)

    def test_invalid_mapping_propagation(self):
        """Verify duplicate targets raise ValueError in invert_rule_mapping."""
        with pytest.raises(ValueError, match="duplicate target rule"):
            ca.invert_rule_mapping({30: 100, 90: 100})

    def test_malformed_json_propagation(self):
        """Verify malformed JSON raises ValueError in deserialize_rule_sequence."""
        with pytest.raises(ValueError, match="Invalid JSON string"):
            ca.deserialize_rule_sequence("not_valid_json")
