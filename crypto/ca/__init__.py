"""Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)
Cellular Automata Subsystem (`crypto.ca`).

This package establishes the deterministic 1D Elementary Cellular Automata (ECA) and Dynamic
Evolution Engine foundation used across the KDR-CA-AEAD cryptographic research system.

Subsystems:
    1. Rule Engine (`crypto.ca.rules`):
       Parses, validates, and memoizes Wolfram rules (0–255) into immutable binary lookup tables.

    2. Evolution Engine (`crypto.ca.engine`):
       Executes deterministic 1D cellular automata evolution with periodic/null boundary conditions.

    3. Dynamic Rule Engine (`crypto.ca.dynamic_rules`):
       Provides `RuleDefinition` abstraction, dynamic rule switching, custom rule registration,
       and unified CA exception hierarchy (`CAError`).

    4. Dynamic Evolution & Schedulers (`crypto.ca.evolution`):
       Implements `RuleEvolutionScheduler` (fixed, cyclic, seeded random, key-dependent, user-defined),
       adaptive neighborhood models (Radius 1 & 2; periodic, null, reflective, fixed boundaries),
       and `DynamicEvolutionEngine` with hybrid multi-rule transitions.

    5. Optimized Evolution Engine (`crypto.ca.optimizer`):
       High-performance bitwise and buffer-reusing evolution routines (`OptimizedCAEngine`),
       and bit packing utilities (`pack_bits`, `unpack_bits`).

    6. Performance Benchmark Framework (`crypto.ca.benchmark`):
       Standalone benchmark suite (`CABenchmark`) measuring timing, peak memory, throughput, and system metadata.

    7. Utility Module (`crypto.ca.utils`):
       Binary state conversions, state initializations, distance/population metrics, and transformations.

    8. Dynamic Rule Mapping (`crypto.ca.mapping`):
       Rule sequence lookups, bijective mappings, inverse transformations, and configuration exports.
"""

__version__: str = "1.0.0"
__author__: str = "KDR-CA-AEAD Project"

# =========================================================
# RE-EXPORTS: RULE ENGINE (PHASE 1)
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
# RE-EXPORTS: EVOLUTION ENGINE (PHASE 1)
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
# RE-EXPORTS: DYNAMIC RULE ENGINE & EXCEPTIONS (PHASE 2.1)
# =========================================================
from .dynamic_rules import (
    CAError,
    DynamicRuleEngine,
    EvolutionError,
    InvalidNeighborhoodError,
    InvalidRuleError,
    InvalidSchedulerError,
    RuleDefinition,
    RuleNotFoundError,
)

# =========================================================
# RE-EXPORTS: DYNAMIC EVOLUTION & SCHEDULERS (PHASE 2.1)
# =========================================================
from .evolution import (
    BOUNDARY_FIXED,
    BOUNDARY_REFLECTIVE,
    VALID_RADII,
    DynamicEvolutionEngine,
    RuleEvolutionScheduler,
    get_neighborhood,
    validate_radius,
)

# =========================================================
# RE-EXPORTS: OPTIMIZER (PHASE 2.1)
# =========================================================
from .optimizer import (
    OptimizedCAEngine,
    pack_bits,
    unpack_bits,
)

# =========================================================
# RE-EXPORTS: BENCHMARK (PHASE 2.1)
# =========================================================
from .benchmark import (
    BenchmarkMetadata,
    BenchmarkResult,
    CABenchmark,
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
    # Exceptions
    "CAError",
    "InvalidRuleError",
    "RuleNotFoundError",
    "InvalidNeighborhoodError",
    "InvalidSchedulerError",
    "EvolutionError",
    # Rule Engine & Definitions
    "MIN_RULE",
    "MAX_RULE",
    "VALID_BITS",
    "Neighborhood",
    "LookupTable",
    "State",
    "RuleDefinition",
    "DynamicRuleEngine",
    "validate_rule",
    "parse_rule",
    "rule_to_binary",
    "get_neighborhood_output",
    # Evolution Engine & Dynamic Evolution
    "BOUNDARY_PERIODIC",
    "BOUNDARY_NULL",
    "BOUNDARY_REFLECTIVE",
    "BOUNDARY_FIXED",
    "VALID_BOUNDARIES",
    "VALID_RADII",
    "validate_boundary",
    "validate_radius",
    "validate_generations",
    "validate_state",
    "get_neighborhood",
    "evolve_step",
    "evolve",
    "RuleEvolutionScheduler",
    "DynamicEvolutionEngine",
    # Optimizer
    "OptimizedCAEngine",
    "pack_bits",
    "unpack_bits",
    # Benchmark
    "CABenchmark",
    "BenchmarkResult",
    "BenchmarkMetadata",
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
