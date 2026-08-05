# Open Science & Scientific Transparency Statement

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Effective Date:** August 5, 2026  
**License:** Apache License 2.0  

---

## 1. Commitment to Open Science & Transparency

The **KDR-CA-AEAD** project is committed to the principles of **Open Science, Scientific Transparency, and Empirical Reproducibility**. 

We believe that cryptographic research must be open, verifiable, and free of proprietary black boxes or hidden assumptions. All algorithms, key derivation schedules, empirical evaluation scripts, raw benchmark datasets, and LaTeX camera-ready paper sources developed in this project are fully open to the global scientific community.

---

## 2. Open Access Statements

### 2.1 Code Availability
The complete reference implementation of KDR-CA-AEAD is hosted publicly on GitHub:
- **Repository URL**: [https://github.com/CHINTANSHETTY/SHA---V0](https://github.com/CHINTANSHETTY/SHA---V0)
- **Programming Language**: Pure Python (Python 3.10+ Standard Library).
- **No Proprietary Dependencies**: Core encryption (`crypto/`, `encrypt.py`, `decrypt.py`) uses standard modules (`hashlib`, `hmac`, `secrets`).

### 2.2 Documentation Availability
Comprehensive documentation is publicly accessible within the repository:
- **Documentation Index**: `docs/index.md`
- **Navigation Map**: `docs/navigation.md`
- **Architecture & API Guides**: `docs/architecture.md`, `docs/api_reference.md`
- **Security & Threat Model**: `docs/security_guide.md`, `SECURITY.md`

### 2.3 Empirical Data Availability
All raw evaluation datasets backing our publication claims are version-controlled and included in the repository:
- **Strict Avalanche Criterion (SAC)**: `evaluation_results/sac_matrix.json` (Bit-flip frequencies across $10^6$ trials).
- **NIST SP 800-22 Randomness Tests**: `evaluation_results/nist_pvalues.json` (p-values for all 15 statistical tests).
- **Benchmark CSV Tables**: `results/tables/benchmark_summary.csv`.

---

## 3. Encouragement of Independent Peer Verification

We actively encourage independent peer review, artifact evaluation committees, security researchers, and cryptanalysts to audit, challenge, and verify our research:

```powershell
# Clone and verify full test suite (500+ tests)
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
$env:PYTHONPATH="."
python -m pytest

# Re-run master reproducibility pipeline
python scripts/run_phase2_5_reproducibility.py
```

---

## 4. Ethical Research & Responsible Disclosure

- **Dual-Use & Safety**: KDR-CA-AEAD is designed strictly for defensive authenticated encryption, secure telemetry, and cryptographic research.
- **Responsible Security Disclosure**: Security researchers discovering potential vulnerabilities are requested to follow our private disclosure workflow defined in `SECURITY.md`.

---

## 5. Software Preservation & Archival

To guarantee long-term digital preservation beyond GitHub:
- **Zenodo Archival DOI**: *To be assigned upon Zenodo archival snapshot (`10.5281/zenodo.<reserved-doi>`)*
- **Software Heritage Identifier (SWHID)**: `swh:1:dir:ebfa1b308199f4f61c0dac6a7fc7ada5c1f22fdd`
- **Metadata Standards**: Standard `CITATION.cff` and `codemeta.json` manifests are maintained.
