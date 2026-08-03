"""Unit tests for Dynamic Cellular Automata Rule Engine (crypto/ca/dynamic_rules.py)."""

import pytest
from crypto.ca.dynamic_rules import (
    CAError,
    DynamicRuleEngine,
    EvolutionError,
    InvalidNeighborhoodError,
    InvalidRuleError,
    RuleDefinition,
    RuleNotFoundError,
)


class TestRuleDefinition:
    """Tests for RuleDefinition class."""

    def test_wolfram_rule_definition(self):
        """Verify standard Wolfram rule initialization and neighborhood evaluation."""
        table = {(0, 0, 0): 0, (0, 0, 1): 1, (0, 1, 0): 1, (0, 1, 1): 1,
                 (1, 0, 0): 1, (1, 0, 1): 0, (1, 1, 0): 0, (1, 1, 1): 0}
        rule30 = RuleDefinition(id=30, name="Rule 30", radius=1, lookup_table=table)

        assert rule30.id == 30
        assert rule30.name == "Rule 30"
        assert rule30.radius == 1
        assert rule30.evaluate((0, 0, 1)) == 1
        assert rule30.evaluate((1, 1, 1)) == 0
        assert rule30.to_dict()["has_lookup_table"] is True

    def test_custom_callable_rule(self):
        """Verify custom transition function in RuleDefinition."""
        # Simple parity rule for radius 1: sum(neighborhood) mod 2
        rule_parity = RuleDefinition(
            id="parity",
            name="Parity Rule",
            radius=1,
            transition_func=lambda nh: sum(nh) % 2,
        )

        assert rule_parity.evaluate((1, 0, 0)) == 1
        assert rule_parity.evaluate((1, 1, 0)) == 0
        assert rule_parity.evaluate((1, 1, 1)) == 1

    def test_invalid_radius(self):
        """Verify invalid radius raises InvalidNeighborhoodError."""
        with pytest.raises(InvalidNeighborhoodError):
            RuleDefinition(id=1, name="BadRadius", radius=0, lookup_table={})

    def test_missing_definition(self):
        """Verify missing lookup table and transition function raises InvalidRuleError."""
        with pytest.raises(InvalidRuleError):
            RuleDefinition(id=1, name="Empty")

    def test_mismatched_neighborhood_length(self):
        """Verify neighborhood length mismatch raises InvalidNeighborhoodError."""
        rule = RuleDefinition(id=30, name="Rule 30", radius=1, lookup_table={(0, 0, 0): 0})
        with pytest.raises(InvalidNeighborhoodError):
            rule.evaluate((0, 1))  # length 2 instead of 3


class TestDynamicRuleEngine:
    """Tests for DynamicRuleEngine class."""

    def test_preload_wolfram_rules(self):
        """Verify engine preloads all 256 Wolfram rules."""
        engine = DynamicRuleEngine(preload_wolfram=True)
        rules = engine.list_rules()
        assert len(rules) == 256
        assert 0 in rules
        assert 30 in rules
        assert 255 in rules

    def test_load_and_get_rule(self):
        """Verify loading and retrieving rule definitions."""
        engine = DynamicRuleEngine(preload_wolfram=True)
        rule30 = engine.load_rule(30)
        assert rule30.id == 30
        assert engine.active_rule == rule30
        assert engine.get_rule(30) == rule30

    def test_register_custom_dict_rule(self):
        """Verify registering custom dictionary rule."""
        engine = DynamicRuleEngine(preload_wolfram=False)
        table = {(0, 0, 0): 0, (0, 0, 1): 1, (0, 1, 0): 0, (0, 1, 1): 1,
                 (1, 0, 0): 0, (1, 0, 1): 1, (1, 1, 0): 0, (1, 1, 1): 1}
        engine.register_rule("custom_copy", table, name="Copy Right Neighbor", radius=1)

        rule = engine.load_rule("custom_copy")
        assert rule.name == "Copy Right Neighbor"
        assert rule.evaluate((0, 0, 1)) == 1

    def test_register_custom_callable_rule(self):
        """Verify registering custom function rule."""
        engine = DynamicRuleEngine(preload_wolfram=False)
        engine.register_rule("majority", lambda nh: 1 if sum(nh) >= 2 else 0, name="Majority Rule", radius=1)

        rule = engine.get_rule("majority")
        assert rule.evaluate((1, 1, 0)) == 1
        assert rule.evaluate((0, 0, 1)) == 0

    def test_remove_rule(self):
        """Verify removing registered rule."""
        engine = DynamicRuleEngine(preload_wolfram=False)
        engine.register_rule(90, 90)
        assert 90 in engine.list_rules()

        engine.remove_rule(90)
        assert 90 not in engine.list_rules()
        with pytest.raises(RuleNotFoundError):
            engine.get_rule(90)

    def test_unregistered_rule_raises_error(self):
        """Verify loading or removing unregistered rule raises RuleNotFoundError."""
        engine = DynamicRuleEngine(preload_wolfram=False)
        with pytest.raises(RuleNotFoundError):
            engine.load_rule(30)
        with pytest.raises(RuleNotFoundError):
            engine.remove_rule(30)

    def test_invalid_rule_identifier_type(self):
        """Verify invalid rule ID type raises InvalidRuleError."""
        engine = DynamicRuleEngine(preload_wolfram=True)
        with pytest.raises(InvalidRuleError):
            engine.validate_rule(3.14)
        with pytest.raises(InvalidRuleError):
            engine.validate_rule(None)
