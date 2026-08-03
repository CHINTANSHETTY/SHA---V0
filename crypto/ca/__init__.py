"""Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)
Cellular Automata Subsystem (`crypto.ca`).

This package establishes the deterministic 1D Elementary Cellular Automata (ECA) foundation
used for key scheduling, state transformations, and authenticated encryption across the
KDR-CA-AEAD cryptographic research engine.

Subsystems:
    1. Rule Engine (`crypto.ca.rules`):
       Parses, validates, and memoizes Wolfram rules (0–255) into immutable 8-bit binary
       lookup tables mapping 3-cell neighborhoods (111 to 000) to output bits.

    2. Evolution Engine (`crypto.ca.engine`):
       Executes deterministic 1D cellular automata evolution supporting arbitrary binary state
       lengths, configurable boundary conditions ("periodic" wrap-around and "null" zero-padded),
       and multi-generation step iteration.

    3. Utility Module (`crypto.ca.utils`):
       Provides binary state conversions (string, int, list), state initializations (zero, one,
       reproducible seeded random), distance/population metrics (Hamming distance, population count),
       state transformations (invert, XOR), matrix generation, and slicing operations.

    4. Dynamic Rule Mapping (`crypto.ca.mapping`):
       Manages rule sequence lookups, bijective rule set mappings, 1-to-1 inverse transformations,
       sequence rotation/cycling, schema-versioned configuration loading/export ("version": 1),
       and deterministic JSON serialization.

Wolfram Rule Representation:
    Neighborhood:  111  110  101  100  011  010  001  000
    Rule Bit:        7    6    5    4    3    2    1    0

Boundary Conditions:
    - "periodic": Wraps cell array ends (cell 0 left neighbor = cell N-1).
    - "null": Zero-pads cell array boundaries (cell 0 left neighbor = 0).

Determinism & Security:
    All functions are strictly pure and deterministic. Random state generation uses isolated
    `random.Random(seed)` instances to ensure 100% reproducibility without modifying Python's
    global `random` state.

Example Usage:
    >>> import crypto.ca as ca
    >>> initial_state = ca.state_from_string("0001000")
    >>> evolved = ca.evolve(initial_state, rule=30, generations=2, boundary="periodic")
    >>> ca.state_to_string(evolved)
    '0110010'
    >>> dist = ca.hamming_distance(initial_state, evolved)
    >>> dist
    4

References:
    Wolfram, S. (1983). "Statistical mechanics of cellular automata". Reviews of Modern Physics, 55(3), 601.
    Wolfram, S. (2002). "A New Kind of Science". Wolfram Media.
"""

__version__: str = "1.0.0"
__author__: str = "KDR-CA-AEAD Project"

# =========================================================
# RE-EXPORTS: RULE ENGINE
# =========================================================
from .rules import (
    MAX_RULE,
    MIN_RULE,
    LookupTable,
    Neighborhood,
    State,
    VALID_BITS,
    get_neighborhood_output,
    parse_rule,
    rule_to_binary,
    validate_rule,
)

# =========================================================
# RE-EXPORTS: EVOLUTION ENGINE
# =========================================================
from .engine import (
    BOUNDARY_NULL,
    BOUNDARY_PERIODIC,
    VALID_BOUNDARIES,
    evolve,
    evolve_step,
    validate_boundary,
    validate_generations,
    validate_state,
)

# =========================================================
# RE-EXPORTS: UTILITIES & METRICS
# =========================================================
from .utils import (
    DEFAULT_PAD_VALUE,
    MIN_STATE_LENGTH,
    Bit,
    Matrix,
    StateLike,
    chunk_state,
    compare_states,
    copy_state,
    flatten_states,
    hamming_distance,
    int_to_state,
    invert_state,
    matrix_to_states,
    one_state,
    pad_state,
    population_count,
    random_state,
    state_from_string,
    state_to_int,
    state_to_string,
    states_to_matrix,
    trim_state,
    validate_bit,
    validate_state_length,
    validate_width,
    xor_states,
    zero_state,
)

# =========================================================
# RE-EXPORTS: DYNAMIC RULE MAPPING & CONFIGURATION
# =========================================================
from .mapping import (
    CURRENT_SCHEMA_VERSION,
    Rule,
    RuleLookup,
    RuleMapping,
    RuleSequence,
    build_rule_lookup,
    compare_rule_sequences,
    cycle_rule,
    deserialize_rule_sequence,
    export_rule_configuration,
    generate_rule_sequence,
    get_rule,
    invert_rule_mapping,
    load_rule_configuration,
    map_rules,
    merge_rule_sequences,
    rotate_rule_sequence,
    rule_exists,
    rule_index,
    serialize_rule_sequence,
    unique_rules,
    validate_rule_sequence,
)

# =========================================================
# EXPLICIT PUBLIC API
# =========================================================
__all__ = [
    # Package Metadata
    "__version__",
    "__author__",
    # Rule Engine
    "MIN_RULE",
    "MAX_RULE",
    "VALID_BITS",
    "Neighborhood",
    "LookupTable",
    "State",
    "validate_rule",
    "parse_rule",
    "rule_to_binary",
    "get_neighborhood_output",
    # Evolution Engine
    "BOUNDARY_PERIODIC",
    "BOUNDARY_NULL",
    "VALID_BOUNDARIES",
    "validate_boundary",
    "validate_generations",
    "validate_state",
    "evolve_step",
    "evolve",
    # Utilities & Metrics
    "Bit",
    "StateLike",
    "Matrix",
    "DEFAULT_PAD_VALUE",
    "MIN_STATE_LENGTH",
    "validate_bit",
    "validate_state_length",
    "validate_width",
    "state_from_string",
    "state_to_string",
    "int_to_state",
    "state_to_int",
    "zero_state",
    "one_state",
    "random_state",
    "copy_state",
    "population_count",
    "hamming_distance",
    "compare_states",
    "invert_state",
    "xor_states",
    "states_to_matrix",
    "matrix_to_states",
    "chunk_state",
    "flatten_states",
    "pad_state",
    "trim_state",
    # Dynamic Rule Mapping & Configuration
    "CURRENT_SCHEMA_VERSION",
    "Rule",
    "RuleSequence",
    "RuleLookup",
    "RuleMapping",
    "validate_rule_sequence",
    "build_rule_lookup",
    "get_rule",
    "generate_rule_sequence",
    "map_rules",
    "invert_rule_mapping",
    "load_rule_configuration",
    "export_rule_configuration",
    "serialize_rule_sequence",
    "deserialize_rule_sequence",
    "compare_rule_sequences",
    "merge_rule_sequences",
    "unique_rules",
    "rule_exists",
    "rule_index",
    "rotate_rule_sequence",
    "cycle_rule",
]
