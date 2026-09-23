# KDR-CA-AEAD Implementation & Developer Guide

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**IEEE Mapping:** Section IV & VII  

---

## 1. System Requirements & Installation

### Prerequisites
- **Python**: Python 3.10+ (Tested on Python 3.13.5)
- **OS**: Windows, Linux, macOS
- **Dependencies**: Listed in `requirements.txt`

### Environment Setup

```powershell
# Clone workspace repository
cd SHA---V0-main

# Install dependencies via pip
python -m pip install -r requirements.txt
```

### Dependencies Overview
- `argon2-cffi`: Argon2id password hashing interface for database user authentication.
- `matplotlib`: Publication graph renderer (300 DPI PNG & SVG).
- `pytest`: Automated test runner framework.

---

## 2. Project Directory Structure

```
SHA---V0-main/
├── crypto/                 # Core Cryptographic Package
│   ├── __init__.py         # Unified public API exports
│   ├── constants.py        # Version labels, buffer sizes
│   ├── engine/             # Encrypt, Decrypt, KeySchedule, Dynamic CA
│   ├── ca/                 # 1D Cellular Automata Engine & Wolfram Rules
│   ├── primitives/         # HKDF, HMAC-SHA256, CSPRNG Random
│   ├── models/             # EncryptedPackage, CryptoError
│   └── analysis/           # Security, Benchmarking, Visualization
├── database/               # SQLite & Argon2id Authentication Interface
├── tests/                  # Automated Pytest Suites
│   ├── unit/               # Unit tests for primitives and modules
│   └── integration/        # End-to-end integration & Phase 2.5 tests
├── docs/                   # IEEE Documentation & Specifications
│   ├── api/                # API reference manuals
│   ├── architecture/       # System architecture & Mermaid diagrams
│   ├── research/           # IEEE paper draft sections
│   └── algorithms/         # IEEE pseudocode specifications
├── scripts/                # Reproducibility & Execution Scripts
│   ├── run_phase2_5_reproducibility.py
│   └── run_all_tests.py
├── results/                # Benchmarks, CSV Tables & Graph Plots
│   ├── tables/             # Master CSV & Markdown comparison tables
│   └── security_graphs/    # 300 DPI PNG & vector SVG figures
├── pytest.ini              # Pytest configuration
├── README.md               # GitHub README documentation
├── CHANGELOG.md            # Release changelog
├── LICENSE                 # Apache 2.0 open-source license
└── CITATION.cff            # IEEE BibTeX citation metadata
```

---

## 3. Execution Commands

### Running Automated Test Suite

```powershell
# Set PYTHONPATH and execute pytest
$env:PYTHONPATH="."
python -m pytest

# Run dedicated Phase 2.5 integration suite with verbose logging
$env:PYTHONPATH="."
python -m pytest tests/integration/test_phase2_5_integration.py -v
```

### Running Unified Master Reproducibility Pipeline

```powershell
# Executes full test suite, security analysis, benchmarks, tables & graphs
$env:PYTHONPATH="."
python scripts/run_phase2_5_reproducibility.py
```

---

## 4. Troubleshooting & Common Issues

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'crypto'` | `PYTHONPATH` not set | Set `$env:PYTHONPATH="."` in PowerShell or `export PYTHONPATH=.` in Bash. |
| `ImportError: cannot import name 'InvalidHashError'` | Argon2 version mismatch | Handled automatically in `database/db_manager.py` via fallback import. |
| `Pytest collection errors` | Duplicate directory discovery | Configured in `pytest.ini` (`norecursedirs = SHA---V0-main`). |
