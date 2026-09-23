# KDR-CA-AEAD Operations Guide

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Version:** 1.0.0  

---

## 1. Cryptographic Operations

### 1. Generating Keys & Nonces
```python
from crypto.primitives.random import generate_secure_random_bytes
from crypto.constants import DEFAULT_KEY_LENGTH, DEFAULT_SALT_LENGTH, DEFAULT_NONCE_LENGTH

master_key = generate_secure_random_bytes(DEFAULT_KEY_LENGTH)  # 32 Bytes
salt = generate_secure_random_bytes(DEFAULT_SALT_LENGTH)        # 16 Bytes
nonce = generate_secure_random_bytes(DEFAULT_NONCE_LENGTH)      # 12 Bytes
```

### 2. Encrypting & Decrypting Bytes
```python
from crypto import encrypt_bytes, decrypt_bytes

key = b"0123456789abcdef0123456789abcdef"
plaintext = b"CONFIDENTIAL PATIENT DATA"
associated_data = b"AD-Header-v1"

# Encrypt
pkg = encrypt_bytes(plaintext, key, associated_data=associated_data)

# Decrypt
recovered = decrypt_bytes(pkg, key, associated_data=associated_data)
assert recovered == plaintext
```

---

## 2. Framework Execution & Build Operations

### 1. Run Integration Test Suite
```powershell
$env:PYTHONPATH="."
python -m pytest
```

### 2. Run Full Security & Randomness Analysis
```powershell
$env:PYTHONPATH="."
python -c "from crypto.analysis.final_validation import run_full_security_analysis; run_full_security_analysis()"
```

### 3. Generate Architecture Vector Figures (Phase 3.2.2)
```powershell
$env:PYTHONPATH="."
python scripts/generate_architecture_figures.py
```

### 4. Generate Benchmark Visualizations & Analytics (Phase 3.2.3)
```powershell
$env:PYTHONPATH="."
python scripts/generate_benchmark_graphs.py
```

### 5. Generate API Documentation (Phase 3.2.4)
```powershell
$env:PYTHONPATH="."
python docs/api/build_api_docs.py
```

### 6. Build IEEE PDF Manuscript (Phase 3.2.1)
```powershell
$env:PYTHONPATH="."
python paper/build_paper.py
```
