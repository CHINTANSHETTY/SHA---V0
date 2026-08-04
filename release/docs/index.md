# KDR-CA-AEAD Documentation Hub

Welcome to the official documentation for **KDR-CA-AEAD** (Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption), version **1.0.0**.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)
[![Test Suite: 100% Pass](https://img.shields.io/badge/tests-passed-brightgreen.svg)](../tests/)
[![IEEE Publication Ready](https://img.shields.io/badge/IEEE-Publication%20Ready-gold.svg)](research/ieee_paper_draft_phase2_6.md)

---

## Executive Summary

**KDR-CA-AEAD** is a production-ready, lightweight authenticated encryption framework designed for secure data transmission, IoT edge security, and high-assurance cryptographic applications. It combines:
1. **HKDF-SHA256**: Domain-separated key expansion (RFC 5869 / NIST SP 800-56C compliant) generating rule seeds ($K_r$), keystream cipher keys ($K_c$), and authentication keys ($K_a$).
2. **Dynamic 1D Cellular Automata (K-DCA)**: Reversible Wolfram rule permutations dynamically mutated based on cryptographic key schedules.
3. **Encrypt-then-MAC AEAD**: Constant-time HMAC-SHA256 authentication tag verification securing ciphertext, salt, nonces, and associated authenticated data (AD).

---

## Documentation Directory Index

| Document | Description | Target Audience |
| :--- | :--- | :--- |
| **[Navigation Map](navigation.md)** | Complete index of all guides, papers, scripts, and API docs | All Users & Reviewers |
| **[Installation Guide](installation.md)** | Prerequisites, setup instructions, virtual environment, dependencies | Developers & Users |
| **[User Guide](user_guide.md)** | Python API, CLI utilities (`encrypt.py`/`decrypt.py`), and Web Application (`app.py`) | End Users & Integrators |
| **[Developer Guide](developer_guide.md)** | Codebase layout, development setup, test execution, and contributing workflow | Developers & Maintainers |
| **[API Reference](api_reference.md)** | Complete module API documentation (`crypto.engine`, `crypto.ca`, `crypto.key`, `crypto.analysis`) | Developers & Integrators |
| **[Architecture Specification](architecture.md)** | High-level component architecture, key schedule, CA mutation engine, and pipeline diagrams | Cryptographers & Architects |
| **[Benchmark Guide](benchmark_guide.md)** | Performance throughput, latency, SAC avalanche, entropy, and comparative benchmarks vs AES-GCM | Performance Researchers |
| **[Security Guide](security_guide.md)** | Threat model, AEAD security bounds (IND-CCA2), SAC bounds, constant-time checks, vulnerability disclosures | Security Auditors |
| **[Reproducibility Guide](reproducibility.md)** | Master evaluation pipeline (`run_phase2_5_reproducibility.py`), datasets, 300 DPI figures, and IEEE paper build | IEEE Reviewers & Scientists |
| **[Troubleshooting & FAQ](troubleshooting.md)** | Common issues, environment fixes, database locking, MAC failures, and FAQs | All Users |

---

## IEEE Publication & Archival Package

- **IEEE Paper Source**: [`paper/ieee_paper.tex`](../paper/ieee_paper.tex)
- **Camera-Ready Draft**: [`docs/research/ieee_paper_draft_phase2_6.md`](research/ieee_paper_draft_phase2_6.md)
- **Master Reproducibility Script**: [`scripts/run_phase2_5_reproducibility.py`](../scripts/run_phase2_5_reproducibility.py)
- **FAIR Archival Verification**: [`docs/release/publication_readiness.md`](release/publication_readiness.md)

---

## Citation

If you use KDR-CA-AEAD in your research or publication, please cite:

```bibtex
@article{shetty2026kdrcaaead,
  title={Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)},
  author={Shetty, Chintan and Nagamrutha},
  journal={IEEE Transactions on Information Forensics and Security},
  year={2026}
}
```
