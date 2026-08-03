"""
Master Reproducibility Automation Script for Phase 2.5.

Executes:
1. Full Automated Test Suite (Unit + Integration + Regression + Phase 2.5 Tests).
2. End-to-End Pipeline Validation & Security Analysis.
3. Performance Benchmarking across payload sizes.
4. Export of structured CSV/JSON datasets into results/ and results/tables/.
5. Generation of 300 DPI IEEE camera-ready figures in results/security_graphs/.

Usage:
    python scripts/run_phase2_5_reproducibility.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import subprocess
from typing import Dict, Any

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crypto.analysis.final_validation import (
    verify_end_to_end_pipeline,
    generate_consolidated_tables,
    generate_publication_figures,
)
from crypto.analysis.security_analysis import run_full_security_analysis
from crypto.analysis.benchmark_runner import run_full_benchmark_suite
from crypto.analysis.benchmark_utils import get_system_metadata


def run_tests() -> bool:
    """Executes the full pytest suite and returns True if all tests pass."""
    print("=" * 70)
    print("STEP 1: RUNNING FULL AUTOMATED TEST SUITE (pytest)")
    print("=" * 70)

    cmd = [sys.executable, "-m", "pytest", "-v"]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode == 0:
        print("[SUCCESS] All automated tests passed successfully!\n")
        return True
    else:
        print("[FAILURE] Automated test suite encountered failures.\n")
        return False


def run_reproducibility_pipeline() -> Dict[str, Any]:
    """Executes end-to-end pipeline validation, security analysis, and benchmarking."""
    print("=" * 70)
    print("STEP 2: EXECUTING END-TO-END PIPELINE & SECURITY VALIDATION")
    print("=" * 70)

    # 1. Pipeline verification
    pipeline_res = verify_end_to_end_pipeline()
    print(f"Pipeline Verification: {pipeline_res['status']}")

    # 2. Full Security Analysis
    print("Running Security Analysis Suite (Entropy, Monobit, Avalanche, Correlation, Attacks)...")
    sec_res = run_full_security_analysis()
    print("[SUCCESS] Security Analysis completed.")

    # 3. Full Benchmarking Suite
    print("\n" + "=" * 70)
    print("STEP 3: RUNNING PERFORMANCE BENCHMARKING SUITE")
    print("=" * 70)
    bm_res = run_full_benchmark_suite()
    print("[SUCCESS] Benchmarking Suite completed.")

    # Consolidate master results
    master_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "system_metadata": get_system_metadata(),
        "pipeline_verification": pipeline_res,
        "security": sec_res,
        "benchmark": bm_res,
    }

    # Output directories
    results_dir = os.path.join(PROJECT_ROOT, "results")
    tables_dir = os.path.join(results_dir, "tables")
    figures_dir = os.path.join(results_dir, "security_graphs")
    os.makedirs(results_dir, exist_ok=True)

    # Export master JSON
    master_json_path = os.path.join(results_dir, "master_results.json")
    with open(master_json_path, "w", encoding="utf-8") as f:
        json.dump(master_results, f, indent=2)
    print(f"\n[EXPORT] Master JSON saved to: {master_json_path}")

    # Generate consolidated IEEE CSV tables
    table_paths = generate_consolidated_tables(master_results, tables_dir)
    print(f"[EXPORT] Generated {len(table_paths)} IEEE CSV tables in: {tables_dir}")

    # Generate 300 DPI publication figures
    fig_paths = generate_publication_figures(master_results, figures_dir)
    print(f"[EXPORT] Generated {len(fig_paths)} IEEE figures in: {figures_dir}")

    return master_results


def main():
    start_time = time.time()
    print("Starting KDR-CA-AEAD Phase 2.5 Master Reproducibility Pipeline...\n")

    # Step 1: Run pytest
    test_success = run_tests()

    # Step 2 & 3: Run pipeline, security & benchmarks
    master_results = run_reproducibility_pipeline()

    elapsed = time.time() - start_time
    print("=" * 70)
    print(f"PHASE 2.5 REPRODUCIBILITY PIPELINE COMPLETED IN {elapsed:.2f} SECONDS")
    print(f"Overall Test Status: {'PASSED' if test_success else 'FAILED'}")
    print("=" * 70)

    if not test_success:
        sys.exit(1)


if __name__ == "__main__":
    main()
