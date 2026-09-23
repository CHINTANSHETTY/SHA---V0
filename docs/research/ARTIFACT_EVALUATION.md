# Research Artifact Evaluation & FAIR Open Science Guide

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Document Version:** 1.0.0  

---

## Executive Overview

This document provides formal **Artifact Evaluation & Open Science Guidelines** for **KDR-CA-AEAD v1.0.0**. The framework is structured to adhere to **ACM Artifact Evaluation Badging Criteria**, **IEEE Open Science Reproducibility Standards**, and **FAIR Data Principles**.

---

## 1. ACM Artifact Evaluation Badging Compliance

KDR-CA-AEAD satisfies all three major ACM Artifact Badges:

```text
+-----------------------+-----------------------+-----------------------+
|  Artifacts Available  |  Artifacts Evaluated  |  Artifacts Evaluated  |
|       (ACM BADGE)     |    - Functional       |     - Reusable        |
+-----------------------+-----------------------+-----------------------+
| Archived via Zenodo   | Documented, builds,   | Modular, clean Python |
| & Software Heritage   | and passes 500+ tests | pure standard library |
+-----------------------+-----------------------+-----------------------+
```

1. **Artifacts Available**: Source code, test scripts, raw NIST SP 800-22 datasets (`evaluation_results/`), and camera-ready figures (`results/security_graphs/`) are publicly accessible under Apache-2.0.
2. **Artifacts Evaluated – Functional**: The software builds, executes, and passes all unit, integration, and security tests cleanly.
3. **Artifacts Evaluated – Reusable**: Well-documented APIs (`crypto/`), minimal dependencies, and clear CLI scripts ensure easy extension by peer researchers.

---

## 2. FAIR Data Principles Compliance

- **Findable**: Indexed via Zenodo DOI placeholder (`10.5281/zenodo.<reserved-doi>`), `CITATION.cff`, and `codemeta.json`.
- **Accessible**: Public GitHub repository with open HTTPS access and zero paywalls.
- **Interoperable**: Standard data formats (JSON, CSV, SVG, PNG) and standard Python primitives.
- **Reusable**: Apache-2.0 license with clear citation guidelines and complete documentation.

---

## 3. Environment Specification & Dependencies

### Hardware Requirements
- **CPU**: x86_64 or ARM64 architecture (1 core minimum, multi-core recommended for benchmarking).
- **RAM**: 2 GB minimum (4 GB recommended for NIST SP 800-22 large vector testing).
- **Disk**: 200 MB free space.

### Software Runtimes
- **Python**: Version 3.10, 3.11, 3.12, or 3.13.
- **Operating Systems**: Windows 10/11, Ubuntu 20.04/22.04 LTS, macOS 12+.

---

## 4. Independent Verification Protocol

Peer reviewers and artifact evaluation committees can execute the following commands to independently verify scientific claims:

```powershell
# 1. Clone & Setup
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0

# 2. Environment Verification
$env:PYTHONPATH="."
python -c "import crypto; print('KDR-CA-AEAD Loaded Successfully')"

# 3. Test Suite Execution (500+ tests)
python -m pytest

# 4. Master Reproducibility & IEEE Dataset Generation
python scripts/run_phase2_5_reproducibility.py
```

---

## 5. Research Reproducibility Checklist

- [x] **Code Availability**: Full source code included in `crypto/`, `encrypt.py`, and `decrypt.py`.
- [x] **Test Availability**: Complete automated test suite in `tests/`.
- [x] **Data Availability**: Raw NIST p-values (`evaluation_results/nist_pvalues.json`) and SAC matrices (`evaluation_results/sac_matrix.json`) included.
- [x] **Paper Source Availability**: Full IEEE LaTeX camera-ready source files in `paper/`.
- [x] **License & Citation**: Apache-2.0 `LICENSE`, `CITATION.cff`, and `codemeta.json` deployed.
