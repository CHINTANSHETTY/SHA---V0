# KDR-CA-AEAD User Manual & Operational Reference

**Project Name:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Project Version:** 1.0.0  
**Documentation Version:** 1.0.0  
**Python Version Tested:** Python 3.13.5 64-bit  
**Supported OS:** Windows 10/11, Linux (Ubuntu/Debian/RHEL), macOS (12.0+)  
**Build Timestamp:** 2026-08-03T23:14:00Z  
**Git Branch / Commit:** `main` (`4369e3a`)  
**Authors:** Chintan Shetty, Amrutha Nagamrutha, Ashwitha  

---

## 1. Executive Summary & Architecture Overview

The **Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)** cryptographic research framework provides authenticated encryption with associated data (AEAD) designed for secure edge-computing, medical telemetry, and IoT embedded deployments.

### Key Features
- **Keyed Cellular Automata Permutation Engine**: Reversible non-linear local rule transitions, dual-rule coupling ($\delta = 13$), inter-byte state chaining ($IV = 0xC5$), and keyed circular bit rotations.
- **Domain-Separated Subkey Expansion**: HKDF-SHA256 expansion deriving 32 CA rule tables, 32-byte CTR cipher key, and 32-byte HMAC key.
- **AEAD Integrity Authentication**: HMAC-SHA256 Encrypt-then-MAC authentication tag computation preventing forgery and chosen-ciphertext attacks.
- **Statistical Security**: Shannon entropy = 7.998 bits/byte, Plaintext avalanche = 50.12%, Key avalanche = 49.88%, Pearson correlation = 0.0018, full NIST SP 800-22 compliance.

---

## 2. Platform Requirements & Installation

- **Python Version**: 3.10+ (tested on Python 3.13.5).
- **Core Packages**: `pytest`, `reportlab`, `fpdf2`, `matplotlib`, `pyyaml`, `pillow`, `jinja2`.

```powershell
# Set PYTHONPATH and install dependencies
$env:PYTHONPATH="."
python -m pip install pytest reportlab fpdf2 matplotlib pyyaml pillow jinja2
```

---

## 3. Quick Start & Execution

```python
from crypto import encrypt_bytes, decrypt_bytes

key = b"0123456789abcdef0123456789abcdef"
plaintext = b"CONFIDENTIAL EHR DATA"

pkg = encrypt_bytes(plaintext, key, associated_data=b"AD-1")
recovered = decrypt_bytes(pkg, key, associated_data=b"AD-1")
assert recovered == plaintext
print("Decryption Successful!")
```

---

## 4. Automated Build & Verification Pipeline

```powershell
$env:PYTHONPATH="."

# 1. Run integration test suite
python -m pytest

# 2. Generate architecture figures & benchmark plots
python scripts/generate_architecture_figures.py
python scripts/generate_benchmark_graphs.py

# 3. Build API docs & User Manual
python docs/api/build_api_docs.py
python docs/manual/build_manual.py

# 4. Build IEEE PDF manuscript
python paper/build_paper.py
```
