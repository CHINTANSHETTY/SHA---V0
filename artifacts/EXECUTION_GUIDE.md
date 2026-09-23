# Research Artifact Execution Guide

This document provides step-by-step terminal instructions to clone, install, execute, benchmark, and verify all components of the **KDR-CA-AEAD** research artifact.

---

## Step 1: Clone Repository

```bash
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
```

---

## Step 2: Set Up Environment & Install Dependencies

It is recommended to use a clean Python virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Linux/macOS
source venv/bin/activate

# Install required dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Step 3: Build & Install Project

Verify setup and package metadata:

```bash
python setup.py develop
```

---

## Step 4: Execute Basic Usage Examples

Run the high-level Python API examples:

```bash
# Execute standalone CLI encryption example
python encrypt.py --input "Hello World" --key "32_Byte_Master_Key_For_KDR_CA_AEAD" --output package.json

# Execute standalone CLI decryption example
python decrypt.py --input package.json --key "32_Byte_Master_Key_For_KDR_CA_AEAD"
```

---

## Step 5: Run Unit and Integration Test Suite

Run the full test suite (465+ tests):

```bash
pytest tests/ -v --cov=crypto
```

All tests should output `PASSED` with 0 failures.

---

## Step 6: Run Benchmarks

Execute performance and avalanche analysis:

```bash
# Execute throughput and latency benchmarks
python crypto/benchmarking/benchmark_report.py

# Run master reproducibility script
python scripts/run_phase2_5_reproducibility.py
```

---

## Step 7: Launch Interactive Web GUI Application

Launch the Flask Web Application to test via GUI:

```bash
python app.py
```
Open `http://127.0.0.1:5000` in your web browser to perform interactive encryption, decryption, and tag validation.

---

## Step 8: Verify Generated Reports and Outputs

Check that output files have been written to `reports/` and `evaluation_results/`:
- `reports/benchmark_summary.md`
- `reports/avalanche_analysis.csv`
- `reports/throughput_comparison.png`
