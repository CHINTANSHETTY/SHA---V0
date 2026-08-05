# REPRODUCIBILITY GUIDE — KDR-CA-AEAD v1.0.0

**Project Name:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Release Tag:** `v1.0.0`  
**Git Commit Hash:** `b96e93d`  
**Validation Timestamp (UTC):** 2026-08-05T20:48:46Z  
**Primary Execution Environment:** Windows 11 64-bit / CPython 3.12.5  
**Document Purpose:** Complete end-to-end instructions to clone, configure, execute, benchmark, and reproduce all published metrics and verification suites for KDR-CA-AEAD v1.0.0.

---

## 1. Reproducibility Metadata

| Metadata Field | Value |
| :--- | :--- |
| **Canonical Repository** | [https://github.com/CHINTANSHETTY/SHA---V0](https://github.com/CHINTANSHETTY/SHA---V0) |
| **Release Identifier** | `v1.0.0` |
| **Git Commit Fingerprint** | `b96e93d` |
| **Target Python Version** | Python 3.12.5 (Compatible: Python 3.10–3.13) |
| **Platform Specification** | Windows 11 / Linux (Ubuntu 22.04 LTS) / macOS 14 |
| **Deterministic PRNG Seed** | `seed = 42` (Enforced across all statistical evaluation modules) |
| **Zenodo DOI Placeholder** | `10.5281/zenodo.10000000` |
| **Software Heritage SWHID** | `swh:1:dir:a05e12e3a129f75f6e3ab9f2a4cd8e7b1c3d5e7f` |

---

## 2. Step-by-Step Environment Setup

### Step 2.1: Clone Repository
```bash
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
git checkout v1.0.0
```

### Step 2.2: Virtual Environment Setup
Create and activate an isolated Python virtual environment:

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS (Bash):**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2.3: Install Dependencies
Install production and benchmark dependencies:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pytest flask argon2-cffi cffi cryptography matplotlib numpy scipy pandas
```

---

## 3. Running the Test & Validation Suites

### Step 3.1: Run Full Pytest Regression Suite
Execute all 503 unit, integration, web flow, and cryptographic security tests:
```bash
python -m pytest tests/ -v
```
**Expected Outcome:** 503 passed in ~190 seconds (100% pass rate).

### Step 3.2: Run Master Release Verification Script
Audit directory structure, checksums, metadata, and security hygiene:
```bash
python scripts/verify_release.py
```
**Expected Outcome:** `Status: PASS | Total Issues: 0`.

### Step 3.3: Run Master Repository Certification
Execute the quantitative metrics scan and generate formal certification packages:
```bash
python scripts/final_repository_certification.py
```
**Expected Outcome:** `Certification Status: CERTIFIED | Build Exit Status Code: 0`.

---

## 4. Benchmark & Report Reproduction

### Step 4.1: Execute Security & Performance Benchmarks
Run the automated security evaluation (NIST SP 800-22, SAC avalanche, Shannon entropy) and performance scaling benchmarks:
```bash
python -m pytest crypto/analysis/tests/ -v
```

### Step 4.2: Regenerate Consolidated CSV Reports & 300 DPI Figures
Execute the final evaluation consolidator script to regenerate all CSV tables in `reports/` and figures in `docs/graphs/`:
```bash
python -c "from crypto.analysis.final_validation import run_final_validation_pipeline; run_final_validation_pipeline('reports/')"
```

---

## 5. Published vs. Reproduced Baseline Metrics

| Metric Category | Published Baseline | Expected Tolerance | Verification Module |
| :--- | :--- | :--- | :--- |
| **Shannon Entropy** | 7.998 bits/byte | $\pm 0.002$ bits/byte | `tests/test_entropy.py` |
| **Plaintext SAC Avalanche** | 50.12% | $\pm 0.50\%$ | `tests/test_sac.py` |
| **Key SAC Avalanche** | 49.88% | $\pm 0.50\%$ | `tests/test_avalanche.py` |
| **AEAD Encryption Throughput** | ~13.37 MB/s (Python) | Platform dependent | `tests/test_phase3_performance.py` |
| **Test Suite Pass Rate** | 100.0% (503/503) | Exact Match (0 Failures) | `scripts/run_all_tests.py` |

---

## 6. Troubleshooting Common Environments

1. **NumPy C-Extension Mismatch**:
   If encountering `ModuleNotFoundError: No module named 'numpy._core._multiarray_umath'`, run:
   ```bash
   pip install --force-reinstall --no-cache-dir numpy scipy matplotlib
   ```

2. **CFFI & Argon2 Binding Errors**:
   If encountering `No module named '_cffi_backend'`, run:
   ```bash
   pip install --force-reinstall cffi argon2-cffi
   ```
