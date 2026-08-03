"""
Unified Test Execution Automation Script.

Executes all pytest test suites (unit, integration, Phase 1, Phase 2, Phase 2.5)
and prints a formatted summary report.

Usage:
    python scripts/run_all_tests.py
"""

from __future__ import annotations

import os
import sys
import time
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    start_time = time.time()
    print("=" * 70)
    print("EXECUTING KDR-CA-AEAD UNIFIED AUTOMATED TEST SUITE")
    print("=" * 70)

    cmd = [sys.executable, "-m", "pytest", "-v"]
    env = dict(os.environ)
    env["PYTHONPATH"] = PROJECT_ROOT

    res = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print(f"TEST SUITE EXECUTED IN {elapsed:.2f} SECONDS")
    print(f"RESULT: {'PASS' if res.returncode == 0 else 'FAIL (Exit Code: ' + str(res.returncode) + ')'}")
    print("=" * 70)

    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
