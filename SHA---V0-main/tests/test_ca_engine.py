"""
Unit tests for Cellular Automata Engine (crypto/ca/engine.py).
"""

import pytest
from crypto.ca.engine import CellularAutomataEngine


class TestCAEngine:
    """Test suite for CellularAutomataEngine class."""

    def test_default_initialization(self):
        """Verify default engine settings."""
        engine = CellularAutomataEngine()
        assert engine.rule == 30
        assert engine.boundary == "wrap"

    def test_custom_initialization(self):
        """Verify custom rule and boundary initialization."""
        engine = CellularAutomataEngine(rule=90, boundary="fixed_zero")
        assert engine.rule == 90
        assert engine.boundary == "fixed_zero"

    def test_rule_90_single_step_wrap(self):
        """
        Verify Rule 90 single step evolution with periodic boundary.
        State: [0, 0, 1, 0, 0] -> Left XOR Right for each cell.
        Cell 0: left=0 (from last), right=0 -> 0
        Cell 1: left=0, right=1 -> 1
        Cell 2: left=0, right=0 -> 0
        Cell 3: left=1, right=0 -> 1
        Cell 4: left=0, right=0 (from first) -> 0
        Expected: [0, 1, 0, 1, 0]
        """
        engine = CellularAutomataEngine(rule=90, boundary="wrap")
        initial = [0, 0, 1, 0, 0]
        evolved = engine.evolve(initial)
        assert evolved == [0, 1, 0, 1, 0]

    def test_rule_90_single_step_fixed_zero(self):
        """
        Verify Rule 90 single step evolution with fixed_zero boundary.
        State: [1, 0, 0, 0, 1]
        Cell 0: left=0, right=0 -> 0
        Cell 1: left=1, right=0 -> 1
        Cell 2: left=0, right=0 -> 0
        Cell 3: left=0, right=1 -> 1
        Cell 4: left=0, right=0 -> 0
        Expected: [0, 1, 0, 1, 0]
        """
        engine = CellularAutomataEngine(rule=90, boundary="fixed_zero")
        initial = [1, 0, 0, 0, 1]
        evolved = engine.evolve(initial)
        assert evolved == [0, 1, 0, 1, 0]

    def test_evolve_rounds(self):
        """Verify multi-round evolution matches repeated single evolutions."""
        engine = CellularAutomataEngine(rule=30, boundary="wrap")
        state = [0, 1, 0, 1, 1, 0, 0, 1]

        step1 = engine.evolve(state)
        step2 = engine.evolve(step1)
        step3 = engine.evolve(step2)

        multi = engine.evolve_rounds(state, 3)
        assert multi == step3

    def test_evolve_zero_rounds(self):
        """Verify 0 rounds returns unchanged state."""
        engine = CellularAutomataEngine(rule=110, boundary="wrap")
        state = [1, 0, 1, 1, 0]
        assert engine.evolve_rounds(state, 0) == state

    def test_rule_switching(self):
        """Verify changing active rule changes evolution behavior."""
        engine = CellularAutomataEngine(rule=90, boundary="wrap")
        state = [0, 0, 1, 0, 0]
        res_rule_90 = engine.evolve(state)

        engine.set_rule(150)
        assert engine.rule == 150
        res_rule_150 = engine.evolve(state)

        assert res_rule_90 != res_rule_150

    def test_boundary_switching(self):
        """Verify changing boundary mode changes evolution behavior."""
        engine = CellularAutomataEngine(rule=30, boundary="wrap")
        state = [1, 0, 0, 0, 1]
        res_wrap = engine.evolve(state)

        engine.set_boundary("fixed_zero")
        assert engine.boundary == "fixed_zero"
        res_fixed = engine.evolve(state)

        assert res_wrap != res_fixed

    def test_single_cell_state(self):
        """Verify single-cell state evolution for both boundary modes."""
        engine_wrap = CellularAutomataEngine(rule=30, boundary="wrap")
        assert len(engine_wrap.evolve([1])) == 1

        engine_fixed = CellularAutomataEngine(rule=30, boundary="fixed_zero")
        assert len(engine_fixed.evolve([1])) == 1

    def test_arbitrary_state_lengths(self):
        """Verify engine works for various state lengths."""
        engine = CellularAutomataEngine(rule=30, boundary="wrap")
        for size in (1, 3, 8, 16, 64, 128):
            state = [1] * size
            evolved = engine.evolve(state)
            assert len(evolved) == size

    def test_invalid_rule_handling(self):
        """Verify setting invalid rule raises expected errors."""
        engine = CellularAutomataEngine()
        with pytest.raises(ValueError):
            engine.set_rule(300)

        with pytest.raises(TypeError):
            engine.set_rule("30")  # type: ignore

    def test_invalid_boundary_handling(self):
        """Verify setting invalid boundary mode raises expected errors."""
        engine = CellularAutomataEngine()
        with pytest.raises(ValueError, match="Unsupported boundary mode"):
            engine.set_boundary("periodic_invalid")

        with pytest.raises(TypeError, match="Boundary mode must be a string"):
            engine.set_boundary(123)  # type: ignore

    def test_invalid_rounds_handling(self):
        """Verify invalid rounds parameter raises expected errors."""
        engine = CellularAutomataEngine()
        state = [1, 0, 1]
        with pytest.raises(ValueError, match="Rounds must be non-negative"):
            engine.evolve_rounds(state, -1)

        with pytest.raises(TypeError, match="Rounds must be an integer"):
            engine.evolve_rounds(state, 2.5)  # type: ignore
