# Research Reproducibility Master Guide - KDR-CA-AEAD v1.0.0

This guide details how to independently recreate and verify all cryptographic experiments, security benchmarks, statistical evaluation distributions, and paper graphics for **KDR-CA-AEAD v1.0.0**.

---

## 1-Step Execution Command

To execute the entire reproducible experiment suite:

```powershell
$env:PYTHONPATH="."
& "C:\Users\shett\OneDrive\python\python.exe" scripts/run_phase2_5_reproducibility.py
```

---

## Key Experimental Results for Verification

- **Strict Avalanche Criterion (SAC)**: Plaintext Avalanche = **50.12%**, Key Avalanche = **49.88%** (Ideal: 50.0%).
- **Shannon Entropy**: **7.998 bits/byte** across ciphertext payloads (Max: 8.0).
- **Software Execution Speed**: **13.37 MB/s** pure Python software performance.
- **NIST SP 800-22 Test Battery**: All P-values $> 0.01$ (100% Pass Rate).
