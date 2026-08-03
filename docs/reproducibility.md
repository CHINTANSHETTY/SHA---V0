# IEEE Reproducibility Package & Guidelines

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**IEEE Mapping:** Section VII – Final Experimental Validation & Reproducibility Package  

---

## 1. Environment & Software Requirements

| Environment Property | Verified Value |
| :--- | :--- |
| **Python Version** | Python 3.10 to Python 3.13 (Tested on 3.13.5) |
| **Operating System** | Windows 10/11 64-bit, Ubuntu 22.04 LTS, macOS 14 |
| **Pytest Version** | 8.3.4 |
| **Matplotlib Version** | 3.8.0+ |
| **Argon2-cffi Version** | 23.1.0+ |

---

## 2. Deterministic Execution & Random Seed Policy

- **Deterministic Mode**: When fixed `salt` (16 bytes) and `nonce` (12 bytes) parameters are provided to `encrypt_bytes(data, key, salt=..., nonce=...)`, output sub-keys, Cellular Automata rule tables, keystream, ciphertext, and HMAC tags are **100% bit-identical and reproducible** across all execution platforms.
- **Random Mode**: In standard operation, CSPRNG nonces and salts are generated via `os.urandom()` (`crypto.primitives.random`), ensuring fresh nonces per message.
- **Benchmarking Seeds**: Benchmark suites use static evaluation payloads and seeds to ensure consistent statistical measurements across test runs.

---

## 3. Step-by-Step Reproducibility Procedure

### Step 1: Clone Repository & Install Dependencies
```powershell
cd SHA---V0-main
python -m pip install -r requirements.txt
```

### Step 2: Execute Master Reproducibility Script
```powershell
$env:PYTHONPATH="."
python scripts/run_phase2_5_reproducibility.py
```

### Step 3: Verify Output Data Artifacts
Upon successful execution, confirm the presence of generated artifacts:

1. **Master Results JSON**: `results/master_results.json`
2. **IEEE Tables**:
   - `results/tables/master_results_table.csv`
   - `results/tables/security_summary.csv`
   - `results/tables/benchmark_summary.csv`
   - `results/tables/cipher_comparison.csv`
   - `results/tables/cipher_comparison.md`
3. **Publication Figures (300 DPI PNG & Vector SVG)**:
   - `results/security_graphs/avalanche.png` & `.svg`
   - `results/security_graphs/entropy.png` & `.svg`
   - `results/security_graphs/histogram.png` & `.svg`
   - `results/security_graphs/correlation.png` & `.svg`
   - `results/security_graphs/comparison.png` & `.svg`
   - `results/security_graphs/throughput_scaling.png` & `.svg`
   - `results/security_graphs/memory_usage.png` & `.svg`
   - `results/security_graphs/cpu_utilization.png` & `.svg`
   - `results/security_graphs/comparative_performance.png` & `.svg`
   - `results/security_graphs/scalability_curve.png` & `.svg`
