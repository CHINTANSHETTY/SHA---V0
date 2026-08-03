# Master Changelog - KDR-CA-AEAD Framework

All notable changes to the Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD) research framework are documented in this file.

---

## [Phase 2.6] - 2026-08-03
### Added
- **API Documentation (`docs/api/`)**:
  - `overview.md`: Package overview, exception hierarchy, module relationships.
  - `crypto_ca.md`: 1D Elementary Cellular Automata evolution, Wolfram rules, state mapping reference.
  - `crypto_engine.md`: Encryption, Decryption, KeySchedule, Dynamic CA Engine reference.
  - `crypto_analysis.md`: Statistical analysis, benchmark runner, validation, visualization reference.
- **Architecture Specifications (`docs/architecture/`)**:
  - `system_architecture.md`: Detailed component interactions and Mermaid workflow diagrams for Encryption, Decryption, and System Architecture.
- **Visualization Enhancements**:
  - Updated `crypto/analysis/visualization.py` to generate both **300 DPI PNG** and **SVG vector** figures in `results/security_graphs/`.
  - Added `cipher_comparison.md` table export in `crypto/analysis/final_validation.py`.
- **Implementation & Reproducibility Package**:
  - `docs/implementation_guide.md`: Developer guide for building, testing, benchmarking, and troubleshooting.
  - `docs/reproducibility.md`: Formal IEEE reproducibility guide, random seed policy, and dataset verification instructions.
  - `docs/algorithms/pseudocode.md`: IEEE camera-ready algorithmic pseudocode.
- **IEEE Paper Materials**:
  - `docs/research/ieee_paper_draft_phase2_6.md`: Complete camera-ready draft sections (Abstract, Intro, Method, Setup, Results, Discussion, Conclusion).
- **Release Materials**:
  - Production `README.md` with badges, system diagram, and benchmark comparison table.
  - `LICENSE` (Apache 2.0 open-source license).
  - `CITATION.cff` (IEEE BibTeX software citation metadata).

---

## [Phase 2.5] - 2026-08-03
### Added
- Comprehensive end-to-end integration test suite `tests/integration/test_phase2_5_integration.py`.
- Unified top-level public API surface in `crypto/__init__.py`.
- Support for Associated Authenticated Data (`associated_data: BytesLike = b""`) and empty payload bytes (`b""`) in `encrypt_bytes` and `decrypt_bytes`.
- Master reproducibility script `scripts/run_phase2_5_reproducibility.py`.

---

## [Phase 2.0 - 2.4] - 2026-08-02
### Added
- Candidate A-Chain Dynamic CA non-linear state engine (`crypto.engine.dynamic_ca`).
- Domain-separated HKDF-SHA256 key schedule (`crypto.engine.key_schedule`).
- NIST SP 800-22 statistical randomness test suite (`crypto.analysis.randomness`).
- Security assessment & comparative benchmark framework (`crypto.analysis`).
