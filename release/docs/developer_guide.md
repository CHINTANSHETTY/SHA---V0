# Developer Guide

Welcome to the **KDR-CA-AEAD** developer guide. This document provides technical instructions for contributing code, extending cryptographic engines, maintaining test suites, and understanding project standards.

---

## Codebase Architecture & Directory Layout

```text
SHA---V0/
├── crypto/                       # Core Cryptographic Library
│   ├── engine.py                 # Encrypt-then-MAC High-Level AEAD Engine
│   ├── key/
│   │   ├── derivation.py         # HKDF-SHA256 Key Schedule & Sub-Key Expansion
│   │   └── scheduler.py          # Key State Lifecycle & Forward Secrecy
│   ├── ca/
│   │   ├── engine.py             # 1D Reversible Wolfram Cellular Automata Engine
│   │   └── rules.py              # Reversible DCA Rule Mutation Logic
│   └── analysis/                 # Cryptanalysis & Evaluation Suite
│       ├── avalanche.py          # Strict Avalanche Criterion (SAC) Tester
│       ├── entropy.py            # Shannon Entropy & Frequency Analysis
│       └── visualization.py      # Matplotlib/Seaborn Figure Generator
├── tests/                        # Automated Pytest Suite (400+ Tests)
│   ├── integration/              # End-to-end System Integration Tests
│   ├── unit/                     # Unit Tests for Engine, CA, HKDF
│   └── property/                 # Property-Based Differential & SAC Tests
├── benchmarks/                   # Performance & Comparative Benchmarks
├── scripts/                      # Automation & Reproducibility Pipelines
│   └── run_phase2_5_reproducibility.py  # Master Reproducibility Pipeline
├── app.py                        # Flask Web Management Server
├── encrypt.py                    # Command-Line Encryption Utility
├── decrypt.py                    # Command-Line Decryption Utility
├── requirements.txt              # Production Dependencies
└── setup.py                      # Package Build Configuration
```

---

## Development Environment Setup

### 1. Clone & Initialize Environment

```bash
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
python -m venv venv
```

Activate environment:
- **Windows**: `.\venv\Scripts\Activate.ps1`
- **Linux/macOS**: `source venv/bin/activate`

### 2. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

---

## Coding & Cryptographic Standards

To maintain high security and academic quality suitable for IEEE release:

1. **Constant-Time Verification**: Always use `hmac.compare_digest()` for MAC tag comparison to prevent timing side-channel attacks.
2. **Explicit Type Annotations**: All public module functions must use explicit PEP 484 type hints.
3. **Immutability of Key Material**: Zeroize sensitive key variables (`bytearray`) or discard reference pointers post-derivation where possible.
4. **Clean Code & Formatting**: Follow PEP 8 guidelines. Use 4 spaces per indent level.
5. **Docstrings**: All public classes, methods, and functions must include Google-style or Sphinx-style docstrings describing parameters, return types, and exceptions.

---

## Test Suite Execution & Guidelines

### Running Tests

Run all unit, integration, and security evaluation tests:
```bash
$env:PYTHONPATH="."
python -m pytest
```

Run tests with code coverage report:
```bash
python -m pytest --cov=crypto tests/
```

### Test Organization
- **Unit Tests (`tests/unit/`)**: Verify isolated functions in `crypto.ca`, `crypto.key`, `crypto.engine`.
- **Integration Tests (`tests/integration/`)**: Test end-to-end package encryption/decryption, database logging, and web endpoints.
- **Property/Security Tests (`tests/property/`)**: Test avalanche ratios, ciphertext entropy distributions, and bit randomness.

---

## Adding New Features

1. Create a descriptive branch: `git checkout -b feat/your-feature-name`.
2. Implement your changes within `crypto/` or `scripts/`.
3. Add corresponding tests under `tests/`.
4. Ensure 100% pass rate across the full test suite.
5. Refer to **[CONTRIBUTING.md](../CONTRIBUTING.md)** before submitting a pull request.
