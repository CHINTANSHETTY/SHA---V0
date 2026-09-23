# KDR-CA-AEAD Troubleshooting & Diagnostics Guide

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Version:** 1.0.0  

---

## 1. Common Issues & Solutions

### 1. ModuleNotFoundError: No module named 'crypto'
- **Root Cause**: Python cannot locate the project root in `sys.path`.
- **Solution**: Set `PYTHONPATH` explicitly before executing scripts:
  ```powershell
  $env:PYTHONPATH="."
  ```

### 2. AuthenticationError: AEAD Tag Verification Failed
- **Root Cause**: The ciphertext or associated data was tampered with, or the wrong key/nonce was supplied.
- **Solution**: Ensure the key (32 bytes), nonce (12 bytes), and associated data match the values used during encryption.

### 3. Matplotlib Figure Export Error / Font Missing
- **Root Cause**: Standard sans-serif fonts (`DejaVu Sans`, `Arial`) missing from System.
- **Solution**: Matplotlib automatically falls back to `DejaVu Sans`. Re-run graph generation:
  ```powershell
  python scripts/generate_benchmark_graphs.py
  ```

### 4. PDF Build Warning: pdflatex not on PATH
- **Root Cause**: System does not have MiKTeX or TeXLive installed.
- **Solution**: `paper/build_paper.py` automatically uses ReportLab to generate `paper/final.pdf` in 2-column IEEE format.
