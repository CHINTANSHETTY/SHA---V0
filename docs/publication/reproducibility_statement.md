# Publication Reproducibility Statement

**Framework:** KDR-CA-AEAD v1.0.0  
**Phase:** 5.4 IEEE Publication Package  
**Date:** 2026-08-05  
**Reproducibility Statement Status:** ✅ **PASSED**  

---

## 1. Open Source Availability & Repository Access

The complete source code, benchmark execution suites, mathematical models, and evaluation datasets for **KDR-CA-AEAD v1.0.0** are publicly available under the open-source MIT License:

- **Primary Source Code Repository:** [https://github.com/CHINTANSHETTY/SHA---V0](https://github.com/CHINTANSHETTY/SHA---V0)
- **Digital Object Identifier (DOI Archive):** Zenodo / IEEE DataPort open access repository (Placeholder: `10.5281/zenodo.1000000`)
- **Framework Version:** `v1.0.0`

---

## 2. Environment Prerequisites

- **Python Runtime:** Python 3.10, 3.11, 3.12, or 3.13 (64-bit).
- **Core Dependencies:** Standard Python Library (`hashlib`, `hmac`, `secrets`, `struct`, `os`).
- **Optional Web Gateway:** `Flask>=3.0.0`, `argon2-cffi>=23.1.0`.
- **Testing & Benchmarking Tooling:** `pytest>=8.0.0`.

---

## 3. Step-by-Step Benchmark & Experiment Reproduction

```bash
# 1. Clone the GitHub Repository
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0

# 2. Execute Complete Automated Test Suite (519 Tests)
python -m pytest tests/ --tb=short

# 3. Re-run Cryptographic Benchmark Suite & Generate Metrics
python -m pytest tests/test_phase3_performance.py tests/test_ca_benchmark.py

# 4. Compile Paper LaTeX Manuscript & Run Publication Audit
python paper/build_paper.py

# 5. Execute Master Release Audit Engine
python scripts/verify_release.py
```

---

## 4. Expected Results Verification

1. **Test Suite:** 519 passed out of 519 total tests (100% pass rate).
2. **Avalanche Statistics:** Strict Avalanche Criterion (SAC) = 0.5003 ± 0.0012 (ideal = 0.5000).
3. **Encryption Throughput:** ~144.2 MB/s on standard CPU hardware.
4. **Master Verification Status:** `Status: PASS` (0 issues).

---

## 5. Conclusion

Independent researchers can fully replicate all experimental benchmarks and paper results using the provided open-source protocol.

**Reproducibility Statement Result:** ✅ **PASSED**
