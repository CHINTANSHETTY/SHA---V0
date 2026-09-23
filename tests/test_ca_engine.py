"""Unit tests for Cellular Automata Evolution Engine (crypto/ca/engine.py)."""

import time
import pytest

import crypto.ca as ca
from crypto.ca.engine import (
    BOUNDARY_PERIODIC,
    BOUNDARY_NULL,
    VALID_BOUNDARIES,
    validate_boundary,
    validate_generations,
    validate_state,
    evolve_step,
    evolve,
)


class TestStateValidation:
    """Tests for validate_state function."""

    def test_valid_states(self):
        """Verify valid binary list, tuple, and string inputs are correctly normalized."""
        assert validate_state([0, 1, 0, 1]) == [0, 1, 0, 1]
        assert validate_state((1, 0, 1, 0)) == [1, 0, 1, 0]
        assert validate_state("1101") == [1, 1, 0, 1]
        assert validate_state("0") == [0]

    def test_empty_states(self):
        """Verify empty state inputs raise ValueError."""
        with pytest.raises(ValueError, match="State cannot be empty"):
            validate_state([])
        with pytest.raises(ValueError, match="State cannot be empty"):
            validate_state(())
        with pytest.raises(ValueError, match="State cannot be empty"):
            validate_state("")

    @pytest.mark.parametrize("invalid_state", [None, 123, 45.6, True])
    def test_invalid_state_types(self, invalid_state):
        """Verify unsupported state types raise TypeError."""
        with pytest.raises(TypeError):
            validate_state(invalid_state)

    def test_invalid_binary_values(self):
        """Verify non-binary values raise ValueError or TypeError."""
        with pytest.raises(ValueError, match="must be 0 or 1"):
            validate_state([0, 2, 1])
        with pytest.raises(ValueError, match="must be 0 or 1"):
            validate_state([0, -1, 1])
        with pytest.raises(ValueError, match="Invalid binary character"):
            validate_state("012")
        with pytest.raises(TypeError, match="must be an integer bit"):
            validate_state([True, False])
        with pytest.raises(TypeError, match="must be an integer bit"):
            validate_state([0.5, 1.0])


class TestBoundaryValidation:
    """Tests for validate_boundary function."""

    def test_valid_boundaries(self):
        """Verify periodic and null boundary names are accepted and normalized."""
        assert validate_boundary("periodic") == "periodic"
        assert validate_boundary("PERIODIC") == "periodic"
        assert validate_boundary(" Periodic ") == "periodic"
        assert validate_boundary("null") == "null"
        assert validate_boundary("NULL") == "null"

    def test_invalid_boundary_names(self):
        """Verify unsupported boundary names raise ValueError."""
        with pytest.raises(ValueError, match="Invalid boundary condition"):
            validate_boundary("toroidal")
        with pytest.raises(ValueError, match="Invalid boundary condition"):
            validate_boundary("fixed")

    @pytest.mark.parametrize("invalid_type", [123, None, True, ["periodic"]])
    def test_invalid_boundary_types(self, invalid_type):
        """Verify non-string boundary types raise TypeError."""
        with pytest.raises(TypeError, match="must be a string"):
            validate_boundary(invalid_type)


class TestGenerationsValidation:
    """Tests for validate_generations function."""

    @pytest.mark.parametrize("valid_gen", [1, 5, 100, 10000])
    def test_valid_generations(self, valid_gen):
        """Verify positive generation integers are accepted."""
        assert validate_generations(valid_gen) == valid_gen

    @pytest.mark.parametrize("invalid_gen", [0, -1, -100])
    def test_out_of_bounds_generations(self, invalid_gen):
        """Verify non-positive generation integers raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            validate_generations(invalid_gen)

    @pytest.mark.parametrize("invalid_type", [1.5, "10", None, True, False])
    def test_invalid_generation_types(self, invalid_type):
        """Verify non-integer generation types raise TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            validate_generations(invalid_type)


class TestEvolvingEngine:
    """Tests for evolve_step and evolve functions."""

    def test_rule_30_evolution(self):
        """Verify Rule 30 evolution across multiple generations."""
        # Initial state with a single 1 cell in center
        initial = [0, 0, 0, 1, 0, 0, 0]
        # Rule 30 periodic step 1:
        # [0, 0, 0, 1, 0, 0, 0] -> [0, 0, 1, 1, 1, 0, 0]
        gen1 = evolve(initial, 30, generations=1, boundary="periodic")
        assert gen1 == [0, 0, 1, 1, 1, 0, 0]

        # Step 2:
        # [0, 0, 1, 1, 1, 0, 0] -> [0, 1, 1, 0, 0, 1, 0]
        gen2 = evolve(initial, 30, generations=2, boundary="periodic")
        assert gen2 == [0, 1, 1, 0, 0, 1, 0]

    def test_rule_90_sierpinski_evolution(self):
        """Verify Rule 90 symmetric XOR evolution (Sierpinski pattern)."""
        initial = [0, 0, 0, 0, 1, 0, 0, 0, 0]
        gen1 = evolve(initial, 90, generations=1, boundary="periodic")
        assert gen1 == [0, 0, 0, 1, 0, 1, 0, 0, 0]

        gen2 = evolve(initial, 90, generations=2, boundary="periodic")
        assert gen2 == [0, 0, 1, 0, 0, 0, 1, 0, 0]

    def test_boundary_conditions_comparison(self):
        """Verify differences between periodic and null boundary conditions."""
        initial = [1, 0, 0, 0, 0]
        # Rule 30 binary 00011110:
        # Periodic boundary: cell 0 left neighbor is cell 4 (0). Right is cell 1 (0). (0,1,0) -> 1.
        # Cell 4 left is cell 3 (0). Right is cell 0 (1). (0,0,1) -> 1.
        periodic_res = evolve(initial, 30, generations=1, boundary="periodic")
        assert periodic_res == [1, 1, 0, 0, 1]

        # Null boundary: cell 0 left neighbor is 0. Right is cell 1 (0). (0,1,0) -> 1.
        # Cell 4 left is cell 3 (0). Right is 0. (0,0,0) -> 0.
        null_res = evolve(initial, 30, generations=1, boundary="null")
        assert null_res == [1, 1, 0, 0, 0]

    def test_single_cell_automata(self):
        """Verify single cell state (N=1) evolution."""
        # Periodic: (1,1,1) -> for Rule 30, (1,1,1) -> 0
        res_periodic = evolve([1], 30, generations=1, boundary="periodic")
        assert res_periodic == [0]

        # Null: (0,1,0) -> for Rule 30, (0,1,0) -> 1
        res_null = evolve([1], 30, generations=1, boundary="null")
        assert res_null == [1]

    def test_evolution_determinism(self):
        """Verify identical outputs across 100 repeated runs (no non-determinism)."""
        state = [0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0]
        reference = evolve(state, 30, generations=10, boundary="periodic")
        for _ in range(100):
            res = evolve(state, 30, generations=10, boundary="periodic")
            assert res == reference

    def test_public_api_imports(self):
        """Verify importing directly from package crypto.ca."""
        assert hasattr(ca, "evolve")
        assert hasattr(ca, "parse_rule")
        assert hasattr(ca, "validate_rule")
        assert ca.evolve("101", 30, generations=1) == [0, 0, 1]

    def test_large_state_benchmark(self):
        """Benchmark performance for 10,000 cells across 100 generations."""
        large_state = [0] * 10000
        large_state[5000] = 1
        start_time = time.perf_counter()
        result = evolve(large_state, 30, generations=100, boundary="periodic")
        elapsed = time.perf_counter() - start_time

        assert len(result) == 10000
        # Sanity assertion that evolution occurred
        assert sum(result) > 1
        print(f"\n[BENCHMARK] 10,000 cells x 100 generations (Rule 30): {elapsed:.4f} seconds")
