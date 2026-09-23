"""Security Analysis, Performance Benchmarking, and IEEE Statistical Validation Subsystem (`crypto.analysis`).

Provides deterministic, reproducible security and statistical analysis tools for KDR-CA-AEAD:
1. Avalanche & SAC Analysis (`crypto.analysis.avalanche`): AvalancheAnalyzer & SACAnalyzer.
2. Entropy Analysis (`crypto.analysis.entropy`): EntropyAnalyzer.
3. Randomness Analysis (`crypto.analysis.randomness`): RandomnessAnalyzer & NIST SP 800-22 tests.
4. Differential & BIC Analysis (`crypto.analysis.differential`): BICAnalyzer & DifferentialAnalyzer.
5. Consolidated Security Metrics (`crypto.analysis.metrics`): SecurityMetrics.
6. Publication Reports (`crypto.analysis.report`): SecurityReport (Markdown, JSON, CSV).
"""

from crypto.analysis.avalanche import (
    AvalancheAnalyzer,
    SACAnalyzer,
    calculate_statistics,
    count_bit_flips,
)
from crypto.analysis.entropy import EntropyAnalyzer
from crypto.analysis.randomness import (
    RandomnessAnalyzer,
    bit_distribution_analysis,
    calculate_shannon_entropy,
    frequency_analysis,
    monobit_test,
    run_randomness_suite,
    runs_test,
    serial_test,
)
from crypto.analysis.differential import (
    BICAnalyzer,
    DifferentialAnalyzer,
)
from crypto.analysis.metrics import SecurityMetrics
from crypto.analysis.report import SecurityReport

from crypto.analysis.statistics import (
    calculate_correlation_coefficients,
    calculate_histogram_uniformity,
    calculate_key_sensitivity,
    compare_with_reference_ciphers,
    measure_key_avalanche,
    measure_plaintext_avalanche,
)
from crypto.analysis.attack_analysis import (
    evaluate_brute_force_complexity,
    evaluate_differential_resistance,
    evaluate_linear_resistance,
    evaluate_performance_tradeoffs,
    evaluate_related_key_resistance,
    evaluate_replay_protection,
)
from crypto.analysis.visualization import (
    generate_all_benchmark_plots,
    generate_all_security_plots,
)
from crypto.analysis.security_analysis import run_full_security_analysis

from crypto.analysis.benchmark_utils import (
    MemoryTracker,
    PrecisionTimer,
    compute_statistics,
    get_system_metadata,
)
from crypto.analysis.benchmark import (
    benchmark_function,
    run_algorithm_benchmark,
)
from crypto.analysis.benchmark_runner import run_full_benchmark_suite
from crypto.analysis.benchmark_export import (
    export_results_to_csv,
    export_results_to_json,
)

from crypto.analysis.final_validation import (
    generate_consolidated_tables,
    generate_experiment_configuration,
    generate_final_evaluation_report,
    generate_publication_figures,
    generate_reproducibility_markdown,
    run_final_validation_pipeline,
    verify_end_to_end_pipeline,
)

__all__ = [
    # Phase 2.4 New Analyzers & Framework Classes
    "AvalancheAnalyzer",
    "SACAnalyzer",
    "EntropyAnalyzer",
    "RandomnessAnalyzer",
    "BICAnalyzer",
    "DifferentialAnalyzer",
    "SecurityMetrics",
    "SecurityReport",
    "count_bit_flips",
    "calculate_statistics",
    "serial_test",
    "run_randomness_suite",
    # Existing Phase 1 & 2 Exports (Preserved 100%)
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
