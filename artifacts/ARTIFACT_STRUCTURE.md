# Research Artifact Directory Structure & Purpose

This document details the organization and functional role of every directory and key module within the **KDR-CA-AEAD** repository.

---

## Directory Hierarchy Overview

```text
SHA---V0/
├── crypto/                # Core Cryptographic Engine & AEAD Logic
├── tests/                 # Automated Unit, Integration, & Compliance Test Suites
├── benchmarks/            # Throughput, Latency, & SAC Performance Benchmarks
├── docs/                  # System Specifications, Guides, & Publication Docs
├── examples/              # Usage Examples & Demonstration Scripts
├── reports/               # Auto-Generated Benchmark & Security Reports
├── release/               # Distribution & Release Packaging Utilities
├── artifacts/             # Research Artifact Evaluation & Reproducibility Package
├── education/             # Educational Resources, Tutorials, & Lab Exercises
├── presentation/          # Slides, Posters, Demo Scripts, & Talk Notes
├── community/             # Governance, Roadmaps, Contribution Guides, & FAQs
├── paper/                 # IEEE Manuscript Drafts & LaTeX Assets
├── app.py                 # Interactive Flask Web GUI Application
├── encrypt.py             # Standalone Command-Line Encryption Utility
└── decrypt.py             # Standalone Command-Line Decryption Utility
```

---

## Comprehensive Folder Descriptions

### 1. `crypto/`
Contains the primary Python implementation of the **KDR-CA-AEAD** algorithm.
- `ca_engine.py`: 1D cellular automata state transition and reversible Wolfram rule execution engine.
- `key_schedule.py`: HKDF-SHA256 key derivation module for rule key ($K_r$), cipher key ($K_c$), and MAC key ($K_a$).
- `aead.py`: Encrypt-then-MAC (EtM) orchestration combining dynamic CA stream generation and constant-time HMAC-SHA256 validation.

### 2. `tests/`
Houses 465+ comprehensive test cases ensuring correctness, security compliance, and resilience against invalid parameters or tampering.
- `test_ca_engine.py`: Tests rule reversibility and state transitions.
- `test_aead.py`: Tests encryption/decryption roundtrips, associated data binding, and MAC verification failures.
- `test_compliance.py`: NIST compliance and RFC test vector verifications.

### 3. `benchmarks/`
Benchmarking engine for empirical evaluation.
- Measures throughput (MB/s) across message sizes from 64 B to 10 MB.
- Measures Strict Avalanche Criterion (SAC) over $10,000+$ key and plaintext bit flips.
- Compares performance against PyCryptodome / OpenSSL implementations of AES-128-GCM and ChaCha20-Poly1305.

### 4. `docs/`
Complete project documentation hub.
- `publication/`: Publication checklists, journal submission guides, IEEE submission notes, and camera-ready checklists.
- Architecture specifications, user guides, developer guides, security guides, and reproducibility guides.

### 5. `examples/`
Ready-to-run Python sample code demonstrating integration of high-level API functions (`encrypt_bytes`, `decrypt_bytes`).

### 6. `reports/`
Output directory where automated benchmark scripts write performance CSVs, Markdown summaries, and visualization charts.

### 7. `release/`
Package scripts, wheel build configurations, and version release checklists.

### 8. `artifacts/`
Contains artifact description, execution guides, expected results, and verification protocols for peer review artifact evaluation.

---

## Key Top-Level Executables
- `app.py`: Web GUI server (`http://127.0.0.1:5000`) for interactive testing of payload encryption and HMAC tag verification.
- `encrypt.py`: CLI tool for file/string encryption.
- `decrypt.py`: CLI tool for file/string decryption.
