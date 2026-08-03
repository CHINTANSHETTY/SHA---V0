"""
Module:
    __init__.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Security Analysis, Performance Benchmarking, and Final IEEE Validation Subsystem
    (Phase 2.3, Phase 2.4, & Phase 2.5 - Nagamrutha/Amrutha).
"""

from crypto.analysis.randomness import (
    calculate_shannon_entropy,
    monobit_test,
    runs_test,
    frequency_analysis,
    bit_distribution_analysis,
)
from crypto.analysis.statistics import (
    measure_plaintext_avalanche,
    measure_key_avalanche,
    calculate_key_sensitivity,
    calculate_correlation_coefficients,
    calculate_histogram_uniformity,
    compare_with_reference_ciphers,
)
from crypto.analysis.attack_analysis import (
    evaluate_brute_force_complexity,
    evaluate_differential_resistance,
    evaluate_linear_resistance,
    evaluate_related_key_resistance,
    evaluate_replay_protection,
    evaluate_performance_tradeoffs,
)
from crypto.analysis.visualization import (
    generate_all_security_plots,
    generate_all_benchmark_plots,
)
from crypto.analysis.security_analysis import run_full_security_analysis

from crypto.analysis.benchmark_utils import (
    get_system_metadata,
    compute_statistics,
    PrecisionTimer,
    MemoryTracker,
)
from crypto.analysis.benchmark import (
    benchmark_function,
    run_algorithm_benchmark,
)
from crypto.analysis.benchmark_runner import run_full_benchmark_suite
from crypto.analysis.benchmark_export import (
    export_results_to_json,
    export_results_to_csv,
)

from crypto.analysis.final_validation import (
    verify_end_to_end_pipeline,
    generate_consolidated_tables,
    generate_publication_figures,
    generate_experiment_configuration,
    generate_reproducibility_markdown,
    generate_final_evaluation_report,
    run_final_validation_pipeline,
)

__all__ = [
    "calculate_shannon_entropy",
    "monobit_test",
    "runs_test",
    "frequency_analysis",
    "bit_distribution_analysis",
    "measure_plaintext_avalanche",
    "measure_key_avalanche",
    "calculate_key_sensitivity",
    "calculate_correlation_coefficients",
    "calculate_histogram_uniformity",
    "compare_with_reference_ciphers",
    "evaluate_brute_force_complexity",
    "evaluate_differential_resistance",
    "evaluate_linear_resistance",
    "evaluate_related_key_resistance",
    "evaluate_replay_protection",
    "evaluate_performance_tradeoffs",
    "generate_all_security_plots",
    "generate_all_benchmark_plots",
    "run_full_security_analysis",
    "get_system_metadata",
    "compute_statistics",
    "PrecisionTimer",
    "MemoryTracker",
    "benchmark_function",
    "run_algorithm_benchmark",
    "run_full_benchmark_suite",
    "export_results_to_json",
    "export_results_to_csv",
    "verify_end_to_end_pipeline",
    "generate_consolidated_tables",
    "generate_publication_figures",
    "generate_experiment_configuration",
    "generate_reproducibility_markdown",
    "generate_final_evaluation_report",
    "run_final_validation_pipeline",
]
