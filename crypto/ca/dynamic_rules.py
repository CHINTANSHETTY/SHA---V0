"""Dynamic Cellular Automata Rule Engine and Rule Representation.

This module provides the Dynamic Rule Engine for managing, registering, validating,
and evaluating Elementary Cellular Automata (ECA) rules and custom neighborhood rules.
It introduces the `RuleDefinition` class to decouple rule representations from execution logic.

Hierarchy of Exceptions:
    CAError
     ├── InvalidRuleError
     ├── RuleNotFoundError
     ├── InvalidNeighborhoodError
     ├── InvalidSchedulerError
     └── EvolutionError

Time Complexity:
    - Rule lookup / evaluation: O(1)
    - Wolfram rule parsing: O(2^n) where n = 2*radius + 1 (O(8) for radius 1).
"""

import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Import Phase 1 rule parsing utilities for backward compatibility & Wolfram rules
from .rules import MIN_RULE, MAX_RULE, parse_rule, validate_rule as parse_validate_wolfram_rule


# =========================================================
# EXCEPTION HIERARCHY
# =========================================================
class CAError(Exception):
    """Base exception for all Cellular Automata subsystem errors."""
    pass


class InvalidRuleError(CAError, ValueError):
    """Raised when a rule ID, specification, or transition function is invalid."""
    pass


class RuleNotFoundError(CAError, KeyError):
    """Raised when requesting or loading a rule ID that is not registered."""
    pass


class InvalidNeighborhoodError(CAError, ValueError):
    """Raised when an invalid neighborhood radius or boundary condition is specified."""
    pass


class InvalidSchedulerError(CAError, ValueError):
    """Raised when a rule evolution scheduler is misconfigured or depleted."""
    pass


class EvolutionError(CAError, RuntimeError):
    """Raised when cellular automata evolution fails during execution."""
    pass


# =========================================================
# RULE DEFINITION ABSTRACTION
# =========================================================
@dataclass
class RuleDefinition:
    """Encapsulates a Cellular Automaton rule definition, metadata, and transition function.

    Attributes:
        id: Unique identifier for the rule (e.g. integer 30 or string "CustomRule1").
        name: Human-readable descriptive name.
        radius: Neighborhood radius (e.g. 1 for 3-cell, 2 for 5-cell).
        lookup_table: Immutable or dict mapping neighborhood tuple to output bit (0 or 1).
        transition_func: Optional custom transition function taking neighborhood tuple -> int.
        metadata: Optional dictionary containing additional research or configuration metadata.
    """

    id: Union[int, str]
    name: str
    radius: int = 1
    lookup_table: Optional[Dict[Tuple[int, ...], int]] = None
    transition_func: Optional[Callable[[Tuple[int, ...]], int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate rule parameters after initialization."""
        if not isinstance(self.radius, int) or self.radius < 1:
            raise InvalidNeighborhoodError(f"Radius must be a positive integer (>= 1), got {self.radius}")

        if self.lookup_table is None and self.transition_func is None:
            raise InvalidRuleError("RuleDefinition must provide either a lookup_table or a transition_func")

    def evaluate(self, neighborhood: Tuple[int, ...]) -> int:
        """Evaluate a neighborhood tuple and return the resulting bit (0 or 1).

        Args:
            neighborhood: Tuple of binary cell states representing the neighborhood.

        Returns:
            int: Output bit (0 or 1).

        Raises:
            InvalidNeighborhoodError: If neighborhood length does not match 2 * radius + 1.
            InvalidRuleError: If neighborhood evaluation yields non-binary output.
        """
        expected_len = 2 * self.radius + 1
        if len(neighborhood) != expected_len:
            raise InvalidNeighborhoodError(
                f"Expected neighborhood of length {expected_len} for radius {self.radius}, "
                f"got length {len(neighborhood)}: {neighborhood}"
            )

        if self.lookup_table is not None and neighborhood in self.lookup_table:
            out_bit = self.lookup_table[neighborhood]
        elif self.transition_func is not None:
            try:
                out_bit = self.transition_func(neighborhood)
            except Exception as err:
                raise EvolutionError(f"Error executing custom transition_func for rule '{self.id}': {err}") from err
        else:
            raise InvalidRuleError(f"Neighborhood {neighborhood} not found in lookup table for rule '{self.id}'")

        if isinstance(out_bit, bool) or not isinstance(out_bit, int) or out_bit not in (0, 1):
            raise InvalidRuleError(f"Rule '{self.id}' output must be integer 0 or 1, got {out_bit}")

        return out_bit

    def to_dict(self) -> Dict[str, Any]:
        """Export rule metadata and representation dictionary.

        Returns:
            Dict[str, Any]: Dictionary containing rule specifications.
        """
        return {
            "id": self.id,
            "name": self.name,
            "radius": self.radius,
            "has_lookup_table": self.lookup_table is not None,
            "has_transition_func": self.transition_func is not None,
            "metadata": self.metadata.copy(),
        }


# =========================================================
# DYNAMIC RULE ENGINE
# =========================================================
class DynamicRuleEngine:
    """Dynamic Cellular Automata Rule Engine.

    Manages runtime registration, validation, switching, and metadata export for
    standard Wolfram elementary rules and custom neighborhood rules.
    """

    def __init__(self, preload_wolfram: bool = True) -> None:
        """Initialize DynamicRuleEngine.

        Args:
            preload_wolfram: If True, pre-registers all 256 Wolfram Elementary Rules (0-255).
        """
        self._rules: Dict[Union[int, str], RuleDefinition] = {}
        self._active_rule_id: Optional[Union[int, str]] = None

        if preload_wolfram:
            self._preload_wolfram_rules()

    def _preload_wolfram_rules(self) -> None:
        """Pre-register all standard Wolfram Elementary Rules (0 through 255)."""
        for rule_num in range(MIN_RULE, MAX_RULE + 1):
            table = dict(parse_rule(rule_num))
            rule_def = RuleDefinition(
                id=rule_num,
                name=f"Wolfram Rule {rule_num}",
                radius=1,
                lookup_table=table,
                metadata={"binary_representation": f"{rule_num:08b}", "type": "wolfram_elementary"},
            )
            self._rules[rule_num] = rule_def

    def validate_rule(self, rule: Any) -> Union[int, str]:
        """Validate if a rule identifier is valid and registered.

        Args:
            rule: Rule ID (int or str) to validate.

        Returns:
            Union[int, str]: Validated rule ID.

        Raises:
            InvalidRuleError: If rule input type is invalid.
            RuleNotFoundError: If rule ID is not registered in the engine.
        """
        if isinstance(rule, bool) or not isinstance(rule, (int, str)):
            raise InvalidRuleError(f"Rule identifier must be an int or str, got {type(rule).__name__}")

        if isinstance(rule, int):
            if not (MIN_RULE <= rule <= MAX_RULE) and rule not in self._rules:
                raise InvalidRuleError(f"Integer rule out of bounds [{MIN_RULE}, {MAX_RULE}], got {rule}")

        if rule not in self._rules:
            raise RuleNotFoundError(f"Rule ID '{rule}' is not registered in DynamicRuleEngine")

        return rule

    def register_rule(
        self,
        rule_id: Union[int, str],
        rule_definition: Union[int, RuleDefinition, Dict[Tuple[int, ...], int], Callable[[Tuple[int, ...]], int]],
        name: Optional[str] = None,
        radius: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuleDefinition:
        """Register a new rule or custom transition in the engine.

        Args:
            rule_id: Unique rule identifier (int or str).
            rule_definition: Integer Wolfram rule, RuleDefinition instance, lookup dict, or callable.
            name: Optional human-readable name.
            radius: Neighborhood radius (defaults to 1).
            metadata: Optional dictionary of metadata.

        Returns:
            RuleDefinition: The newly registered rule definition.

        Raises:
            InvalidRuleError: If rule_id or rule_definition is invalid.
        """
        if isinstance(rule_id, bool) or not isinstance(rule_id, (int, str)):
            raise InvalidRuleError(f"rule_id must be an int or str, got {type(rule_id).__name__}")

        rule_name = name or f"Rule_{rule_id}"
        meta = metadata.copy() if metadata else {}

        if isinstance(rule_definition, RuleDefinition):
            definition = rule_definition
        elif isinstance(rule_definition, int):
            wolfram_val = parse_validate_wolfram_rule(rule_definition)
            table = dict(parse_rule(wolfram_val))
            definition = RuleDefinition(
                id=rule_id,
                name=name or f"Wolfram Rule {wolfram_val}",
                radius=1,
                lookup_table=table,
                metadata={"binary_representation": f"{wolfram_val:08b}", **meta},
            )
        elif isinstance(rule_definition, dict):
            definition = RuleDefinition(
                id=rule_id,
                name=rule_name,
                radius=radius,
                lookup_table=dict(rule_definition),
                metadata=meta,
            )
        elif callable(rule_definition):
            definition = RuleDefinition(
                id=rule_id,
                name=rule_name,
                radius=radius,
                transition_func=rule_definition,
                metadata=meta,
            )
        else:
            raise InvalidRuleError(f"Unsupported rule_definition type: {type(rule_definition).__name__}")

        self._rules[rule_id] = definition
        return definition

    def remove_rule(self, rule_id: Union[int, str]) -> None:
        """Remove a registered rule from the engine.

        Args:
            rule_id: Rule ID to remove.

        Raises:
            RuleNotFoundError: If rule_id is not registered.
        """
        if rule_id not in self._rules:
            raise RuleNotFoundError(f"Cannot remove rule '{rule_id}': not registered")

        del self._rules[rule_id]
        if self._active_rule_id == rule_id:
            self._active_rule_id = None

    def load_rule(self, rule_id: Union[int, str]) -> RuleDefinition:
        """Set the active rule for the engine and return its definition.

        Args:
            rule_id: Rule ID to set as active.

        Returns:
            RuleDefinition: Active rule definition.

        Raises:
            RuleNotFoundError: If rule_id is not registered.
        """
        valid_id = self.validate_rule(rule_id)
        self._active_rule_id = valid_id
        return self._rules[valid_id]

    def get_rule(self, rule_id: Union[int, str]) -> RuleDefinition:
        """Retrieve a registered rule definition without changing the active rule.

        Args:
            rule_id: Rule ID to retrieve.

        Returns:
            RuleDefinition: Rule definition object.

        Raises:
            RuleNotFoundError: If rule_id is not registered.
        """
        valid_id = self.validate_rule(rule_id)
        return self._rules[valid_id]

    def list_rules(self) -> List[Union[int, str]]:
        """Return a list of all currently registered rule IDs.

        Returns:
            List[Union[int, str]]: List of registered rule IDs.
        """
        return list(self._rules.keys())

    @property
    def active_rule(self) -> Optional[RuleDefinition]:
        """Return the currently loaded active rule definition, if any."""
        if self._active_rule_id is not None:
            return self._rules[self._active_rule_id]
        return None
