"""Dynamic Rule Mapping and Configuration Subsystem for KDR-CA-AEAD.

This module manages Cellular Automata rule selection, indexing lookups, bijective
rule transformations, sequence rotation/cycling, configuration load/export,
and JSON serialization.

Determinism & Security:
    - All mapping and sequence operations are strictly deterministic and pure.
    - Configuration schema versioning ("version": 1) is enforced on serialization.
    - Bijective mappings enforce unique target rules to ensure deterministic inversions.

Time Complexity:
    - validate_rule_sequence: O(N) where N is sequence length.
    - build_rule_lookup: O(N).
    - get_rule: O(1).
    - map_rules & invert_rule_mapping: O(N).
    - serialize_rule_sequence & deserialize_rule_sequence: O(N).
"""

import json
from typing import Any, Dict, List, Optional, Sequence, Set

from .rules import MAX_RULE, MIN_RULE, validate_rule

# =========================================================
# MODULE CONSTANTS
# =========================================================
CURRENT_SCHEMA_VERSION: int = 1
ALLOWED_CONFIG_KEYS: Set[str] = {
    "version",
    "rules",
    "default_rule",
    "active_rule",
    "metadata",
}

# =========================================================
# TYPE ALIASES
# =========================================================
Rule = int
RuleSequence = List[int]
RuleLookup = Dict[int, int]
RuleMapping = Dict[int, int]


# =========================================================
# RULE VALIDATION
# =========================================================
def validate_rule_sequence(rules: Any, allow_duplicates: bool = True) -> RuleSequence:
    """Validate a sequence of integer Cellular Automata rules (0-255).

    Args:
        rules: Sequence of rule integers.
        allow_duplicates: If False, raises ValueError if duplicate rules exist.

    Returns:
        RuleSequence: Validated list of integer rules.

    Raises:
        TypeError: If rules is not a list or tuple.
        ValueError: If rules is empty, contains invalid rule values, or has duplicates when forbidden.
    """
    if not isinstance(rules, (list, tuple)):
        raise TypeError(f"Rule sequence must be a list or tuple, got {type(rules).__name__}")

    if len(rules) == 0:
        raise ValueError("Rule sequence cannot be empty")

    validated: RuleSequence = []
    for idx, rule in enumerate(rules):
        try:
            val_rule = validate_rule(rule)
            validated.append(val_rule)
        except (TypeError, ValueError) as err:
            raise type(err)(f"Invalid rule at index {idx}: {err}") from err

    if not allow_duplicates and len(set(validated)) != len(validated):
        raise ValueError("Rule sequence contains duplicate rules")

    return validated


# =========================================================
# RULE LOOKUP
# =========================================================
def build_rule_lookup(rules: Sequence[int]) -> RuleLookup:
    """Build a deterministic lookup dictionary mapping index integers to rule values.

    Example:
        [30, 90, 110] -> {0: 30, 1: 90, 2: 110}

    Args:
        rules: Sequence of rule integers.

    Returns:
        RuleLookup: Dictionary mapping integer index -> rule.
    """
    validated = validate_rule_sequence(rules)
    return {idx: rule for idx, rule in enumerate(validated)}


def get_rule(index: Any, lookup: Any) -> int:
    """Retrieve a rule integer from a lookup dictionary by index.

    Args:
        index: Target integer index.
        lookup: Rule lookup dictionary.

    Returns:
        int: Rule integer at specified index.

    Raises:
        TypeError: If lookup is not a dict or index is not an integer.
        IndexError: If index is not found in lookup.
    """
    if not isinstance(lookup, dict):
        raise TypeError(f"Lookup must be a dictionary, got {type(lookup).__name__}")

    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError(f"Index must be an integer, got {type(index).__name__}")

    if index not in lookup:
        raise IndexError(f"Rule index {index} out of bounds for lookup table of size {len(lookup)}")

    rule = lookup[index]
    return validate_rule(rule)


# =========================================================
# RULE SEQUENCE GENERATION
# =========================================================
def generate_rule_sequence(start_rule: Any, count: Any, step: Any = 1) -> RuleSequence:
    """Generate a deterministic sequence of rules starting at start_rule.

    Args:
        start_rule: Starting Wolfram rule (0-255).
        count: Length of sequence to generate (>= 1).
        step: Increment step per iteration (defaults to 1).

    Returns:
        RuleSequence: Generated list of rule integers.

    Raises:
        TypeError: If arguments are not integers.
        ValueError: If start_rule is invalid or count < 1.
    """
    val_start = validate_rule(start_rule)

    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError(f"Count must be an integer, got {type(count).__name__}")
    if count < 1:
        raise ValueError(f"Count must be positive (>= 1), got {count}")

    if isinstance(step, bool) or not isinstance(step, int):
        raise TypeError(f"Step must be an integer, got {type(step).__name__}")

    return [(val_start + i * step) % (MAX_RULE + 1) for i in range(count)]


# =========================================================
# RULE MAPPING & INVERSION
# =========================================================
def map_rules(
    source: Sequence[int], target: Sequence[int], bijective: bool = False
) -> RuleMapping:
    """Generate a deterministic rule mapping dictionary from source rules to target rules.

    Args:
        source: Sequence of source rules.
        target: Sequence of target rules.
        bijective: If True, enforces that target rules must also be unique.

    Returns:
        RuleMapping: Dictionary mapping source_rule -> target_rule.

    Raises:
        ValueError: If sequence lengths differ or duplicate source (or target) rules exist.
    """
    norm_source = validate_rule_sequence(source)
    norm_target = validate_rule_sequence(target)

    if len(norm_source) != len(norm_target):
        raise ValueError(
            f"Source and target sequences must have equal length, got {len(norm_source)} and {len(norm_target)}"
        )

    if len(set(norm_source)) != len(norm_source):
        raise ValueError("Source rules must be unique for deterministic mapping")

    if bijective and len(set(norm_target)) != len(norm_target):
        raise ValueError("Target rules must be unique for bijective mapping")

    return {src: tgt for src, tgt in zip(norm_source, norm_target)}


def invert_rule_mapping(mapping: Any) -> RuleMapping:
    """Invert a rule mapping dictionary (target -> source).

    Args:
        mapping: Rule mapping dictionary to invert.

    Returns:
        RuleMapping: Inverted dictionary mapping target_rule -> source_rule.

    Raises:
        TypeError: If mapping is not a dict.
        ValueError: If mapping has duplicate target rules preventing bijective inversion.
    """
    if not isinstance(mapping, dict):
        raise TypeError(f"Mapping must be a dictionary, got {type(mapping).__name__}")

    if len(mapping) == 0:
        raise ValueError("Mapping dictionary cannot be empty")

    inverted: RuleMapping = {}
    seen_targets: Set[int] = set()

    for src, tgt in mapping.items():
        val_src = validate_rule(src)
        val_tgt = validate_rule(tgt)

        if val_tgt in seen_targets:
            raise ValueError(
                f"Cannot invert rule mapping: duplicate target rule {val_tgt} prevents 1-to-1 inversion"
            )

        seen_targets.add(val_tgt)
        inverted[val_tgt] = val_src

    return inverted


# =========================================================
# CONFIGURATION SUPPORT
# =========================================================
def load_rule_configuration(config: Any) -> Dict[str, Any]:
    """Load and validate a rule configuration dictionary.

    Args:
        config: Configuration dictionary to load.

    Returns:
        Dict[str, Any]: Validated configuration dictionary with versioning and rules.

    Raises:
        TypeError: If config is not a dict.
        ValueError: If version is missing/unsupported, rules are missing/invalid, or default/active rules are invalid.
    """
    if not isinstance(config, dict):
        raise TypeError(f"Configuration must be a dictionary, got {type(config).__name__}")

    # Check for unknown keys
    unknown_keys = set(config.keys()) - ALLOWED_CONFIG_KEYS
    if unknown_keys:
        raise ValueError(f"Unknown configuration key(s): {sorted(unknown_keys)}")

    # Check version
    if "version" not in config:
        raise ValueError("Configuration missing required 'version' key")
    version = config["version"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise TypeError(f"Version must be an integer, got {type(version).__name__}")
    if version != CURRENT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported configuration schema version {version}. Expected version {CURRENT_SCHEMA_VERSION}"
        )

    # Check rules
    if "rules" not in config:
        raise ValueError("Configuration missing required 'rules' key")
    norm_rules = validate_rule_sequence(config["rules"])

    default_rule: Optional[int] = None
    if config.get("default_rule") is not None:
        default_rule = validate_rule(config["default_rule"])
        if default_rule not in norm_rules:
            raise ValueError(f"Default rule {default_rule} must be present in rules list")

    active_rule: Optional[int] = None
    if config.get("active_rule") is not None:
        active_rule = validate_rule(config["active_rule"])
        if active_rule not in norm_rules:
            raise ValueError(f"Active rule {active_rule} must be present in rules list")

    metadata: Dict[str, Any] = config.get("metadata", {})
    if not isinstance(metadata, dict):
        raise TypeError(f"Metadata must be a dictionary, got {type(metadata).__name__}")

    return {
        "version": CURRENT_SCHEMA_VERSION,
        "rules": norm_rules,
        "default_rule": default_rule,
        "active_rule": active_rule,
        "metadata": metadata,
    }


def export_rule_configuration(
    rules: Sequence[int],
    default_rule: Optional[int] = None,
    active_rule: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Export rule configuration parameters into a standardized dictionary format.

    Args:
        rules: Sequence of rule integers.
        default_rule: Optional default rule integer.
        active_rule: Optional active rule integer.
        metadata: Optional metadata dictionary.

    Returns:
        Dict[str, Any]: Validated, serializable rule configuration dictionary.
    """
    raw_config = {
        "version": CURRENT_SCHEMA_VERSION,
        "rules": list(rules),
        "default_rule": default_rule,
        "active_rule": active_rule,
        "metadata": metadata or {},
    }
    return load_rule_configuration(raw_config)


# =========================================================
# SERIALIZATION
# =========================================================
def serialize_rule_sequence(
    rules: Sequence[int],
    default_rule: Optional[int] = None,
    active_rule: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    indent: Optional[int] = None,
) -> str:
    """Serialize a rule sequence configuration into a deterministic JSON string.

    Args:
        rules: Sequence of rule integers.
        default_rule: Optional default rule.
        active_rule: Optional active rule.
        metadata: Optional metadata dict.
        indent: Optional JSON indentation level.

    Returns:
        str: Deterministic JSON string representation.
    """
    config = export_rule_configuration(
        rules=rules,
        default_rule=default_rule,
        active_rule=active_rule,
        metadata=metadata,
    )
    return json.dumps(config, indent=indent, sort_keys=True)


def deserialize_rule_sequence(data: Any) -> Dict[str, Any]:
    """Deserialize a JSON string into a validated rule configuration dictionary.

    Args:
        data: JSON string to deserialize.

    Returns:
        Dict[str, Any]: Validated rule configuration dictionary.

    Raises:
        TypeError: If data is not a string.
        ValueError: If JSON is malformed or configuration fails validation.
    """
    if not isinstance(data, str):
        raise TypeError(f"Serialized data must be a string, got {type(data).__name__}")

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON string: {err}") from err

    return load_rule_configuration(parsed)


# =========================================================
# MAPPING UTILITIES
# =========================================================
def compare_rule_sequences(a: Any, b: Any) -> bool:
    """Compare two rule sequences for exact equality.

    Args:
        a: First sequence to compare.
        b: Second sequence to compare.

    Returns:
        bool: True if sequences are valid and identical in order, False otherwise.
    """
    try:
        norm_a = validate_rule_sequence(a)
        norm_b = validate_rule_sequence(b)
        return norm_a == norm_b
    except (TypeError, ValueError):
        return False


def merge_rule_sequences(
    a: Sequence[int], b: Sequence[int], unique_only: bool = False
) -> RuleSequence:
    """Merge two rule sequences into a single sequence.

    Args:
        a: First rule sequence.
        b: Second rule sequence.
        unique_only: If True, preserves only first occurrences of each rule.

    Returns:
        RuleSequence: Merged sequence of rules.
    """
    norm_a = validate_rule_sequence(a)
    norm_b = validate_rule_sequence(b)
    combined = norm_a + norm_b

    if unique_only:
        return unique_rules(combined)
    return combined


def unique_rules(sequence: Sequence[int]) -> RuleSequence:
    """Return ordered unique rules from a sequence preserving first insertion order.

    Args:
        sequence: Sequence of rules.

    Returns:
        RuleSequence: Ordered list of unique rule integers.
    """
    norm_seq = validate_rule_sequence(sequence)
    seen: Set[int] = set()
    result: RuleSequence = []

    for rule in norm_seq:
        if rule not in seen:
            seen.add(rule)
            result.append(rule)

    return result


def rule_exists(rule: Any, sequence: Sequence[int]) -> bool:
    """Check whether a specific rule exists within a rule sequence.

    Args:
        rule: Rule integer to search for.
        sequence: Rule sequence to search.

    Returns:
        bool: True if rule is present in sequence, False otherwise.
    """
    val_rule = validate_rule(rule)
    norm_seq = validate_rule_sequence(sequence)
    return val_rule in norm_seq


def rule_index(rule: Any, sequence: Sequence[int]) -> int:
    """Return the first 0-based index of a rule in a sequence.

    Args:
        rule: Target rule integer.
        sequence: Rule sequence.

    Returns:
        int: Index of rule in sequence.

    Raises:
        ValueError: If rule is not found in sequence.
    """
    val_rule = validate_rule(rule)
    norm_seq = validate_rule_sequence(sequence)

    if val_rule not in norm_seq:
        raise ValueError(f"Rule {val_rule} not found in rule sequence")

    return norm_seq.index(val_rule)


def rotate_rule_sequence(sequence: Sequence[int], shift: Any) -> RuleSequence:
    """Rotate a rule sequence to the left by shift positions.

    Args:
        sequence: Rule sequence to rotate.
        shift: Number of positions to shift (can be negative or > len).

    Returns:
        RuleSequence: Rotated rule sequence.
    """
    norm_seq = validate_rule_sequence(sequence)

    if isinstance(shift, bool) or not isinstance(shift, int):
        raise TypeError(f"Shift must be an integer, got {type(shift).__name__}")

    n = len(norm_seq)
    effective_shift = shift % n
    return norm_seq[effective_shift:] + norm_seq[:effective_shift]


def cycle_rule(sequence: Sequence[int], index: Any) -> int:
    """Retrieve the rule at index mod len(sequence) for modular cyclic access.

    Args:
        sequence: Rule sequence to cycle through.
        index: Iteration index integer.

    Returns:
        int: Rule integer at index % len(sequence).
    """
    norm_seq = validate_rule_sequence(sequence)

    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError(f"Index must be an integer, got {type(index).__name__}")

    return norm_seq[index % len(norm_seq)]
