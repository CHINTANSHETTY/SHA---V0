# Research Artifact Description

This artifact package accompanies the research paper **"Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)"**.

---

## 1. Project Overview

**KDR-CA-AEAD** is an authenticated encryption framework built upon reversible 1D cellular automata permutations, dynamically reconfigured via HKDF sub-key expansion, and authenticated with HMAC-SHA256 Encrypt-then-MAC (EtM).

The research artifact provides complete source code, automated test suites, performance benchmarking engines, statistical avalanche evaluators, and visualization scripts to replicate all empirical results reported in the publication.

---

## 2. Research Objectives

1. **Dynamic CA Permutation Security**: Evaluate the cryptographic strength and avalanche behavior of key-dependent 1D Wolfram rule selection.
2. **Authenticated Encryption Bounds**: Verify IND-CCA2 security guarantees and integrity protections provided by EtM domain separation.
3. **Reproducible Benchmarking**: Compare throughput, memory consumption, latency, and SAC against industry standards (AES-128-GCM, ChaCha20-Poly1305).

---

## 3. Repository Overview

- **Repository Name**: `KDR-CA-AEAD` (`SHA---V0`)
- **Version**: `1.0.0`
- **License**: Apache License 2.0 (`LICENSE`)
- **Main Languages**: Python 3.10+ (Core crypto engine, evaluation, web interface)

---

## 4. Programming Language & Core Dependencies

- **Python Version**: Python 3.10 or higher.
- **Core Cryptographic Library**: `cryptography` (used strictly for standard primitives HKDF-SHA256 and HMAC-SHA256).
- **Web Interface**: `Flask` (for GUI demonstration server `app.py`).
- **Data & Plotting**: `numpy`, `matplotlib` (for visual rendering of avalanche matrices and performance charts).
- **Testing**: `pytest`, `pytest-cov` (for 465+ unit/integration tests).

---

## 5. Hardware Requirements

- **Processor**: x86_64 or ARM64 modern CPU (Intel Core i5/i7/i9, AMD Ryzen, Apple M1/M2/M3).
- **RAM**: 4 GB minimum (8 GB recommended for large dataset benchmarking).
- **Disk Space**: 500 MB available storage for repository, generated benchmark logs, and reports.

---

## 6. Operating System Support

Fully tested and validated across:
- **Windows**: Windows 10 / 11 (PowerShell / Command Prompt).
- **Linux**: Ubuntu 20.04 / 22.04 LTS, Debian, Fedora, Arch Linux.
- **macOS**: macOS Monterey, Ventura, Sonoma, Sequoia (Intel & Apple Silicon).

---

## 7. License

Distributed under the **Apache License 2.0**. See `LICENSE` for details.
