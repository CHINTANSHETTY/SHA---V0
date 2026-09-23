# Long-Term Sustainability & Preservation Plan

This document details the long-term software maintenance strategy, versioning policy, dependency management protocols, institutional archiving plan, reproducibility guarantees, and end-of-life (EOL) policy for the **KDR-CA-AEAD** research artifact.

---

## 1. Long-Term Maintenance Strategy

- **Core Stability**: The primary cryptographic API (`crypto/`) is frozen for major version 1.x to ensure backward compatibility for research citations.
- **Maintenance Horizon**: The core maintainers commit to providing security updates, bug fixes, and environment compatibility updates (e.g., supporting newer Python releases) for a minimum of **5 years** post-publication (through 2030).
- **Community Stewardship**: The repository structure and governance models (`CONTRIBUTING.md`, `community/`) enable transparent community takeover if primary maintainers step back.

---

## 2. Software Versioning Policy

KDR-CA-AEAD adheres strictly to **Semantic Versioning 2.0.0 (MAJOR.MINOR.PATCH)**:

- **MAJOR (`X.0.0`)**: Incompatible API changes, algorithm structural modifications, or security model revisions.
- **MINOR (`1.X.0`)**: Backward-compatible functionality additions (e.g., C/C++ bindings, GPU acceleration, new CLI flags).
- **PATCH (`1.0.X`)**: Backward-compatible bug fixes, security patches, and documentation updates.

---

## 3. Dependency Management & Supply Chain Security

- **Minimal External Footprint**: The core cryptographic engine relies solely on Python's standard library and the audited `cryptography` package (for HKDF-SHA256 and HMAC-SHA256).
- **Pinned Requirements**: All build and benchmark dependencies are pinned with exact version specifications in `requirements.txt`.
- **Dependabot Monitoring**: GitHub Dependabot is enabled to detect and patch upstream supply-chain vulnerabilities automatically.

---

## 4. Institutional Archiving & Preservation Strategy

To prevent digital decay and link rot:
1. **Zenodo Archiving**: Every major release tag is automatically assigned a Digital Object Identifier (DOI) via Zenodo integration.
2. **Software Heritage Foundation**: Complete repository history and commit trees are archived on [Software Heritage](https://www.softwareheritage.org/).
3. **Institutional Archive Copies**: Raw benchmark CSVs, test logs, generated figure graphics, and LaTeX paper packages are mirrored in `institutional_archive/`.

---

## 5. Reproducibility Strategy

- **Self-Contained Artifact**: All benchmark scripts, test vectors, and figure generators run out-of-the-box without requiring external proprietary software.
- **Deterministic Evaluation**: Master reproducibility script `run_phase2_5_reproducibility.py` validates output SHA-256 hashes against published baselines.
- **Containerization Support**: Docker container configurations (`Dockerfile`) are provided to guarantee reproducible execution on future hardware architectures.

---

## 6. End-of-Life (EOL) Policy

In the event that KDR-CA-AEAD transitions to End-of-Life:
1. A formal EOL announcement will be published in `README.md` and `CHANGELOG.md` 6 months in advance.
2. Final static source snapshots, test vector bundles, and PDF documentation will be archived permanently on Zenodo and Software Heritage.
3. The repository will be placed in read-only public archive mode, preserving access for future academic citation.
