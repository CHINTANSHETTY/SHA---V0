# KDR-CA-AEAD Step-by-Step User Tutorial

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Target Audience:** Software Developers, Students, Integration Engineers  
**Document Version:** 1.0.0  

---

## Overview

Welcome to the **KDR-CA-AEAD Tutorial**. This guide takes you through installing the framework, encrypting payloads, authenticating telemetry with Associated Data (AD), running performance benchmarks, and executing statistical validation tests.

---

## 1. Installation & Environment Setup

### 1.1 Clone Repository & Setup Virtual Environment

```powershell
# Clone repository
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0

# Create and activate Python virtual environment
python -m venv venv
venv\Scripts\activate
```

### 1.2 Install Dependencies

Core encryption logic relies exclusively on the Python Standard Library. To run tests and benchmarks, install development dependencies:

```powershell
pip install -r requirements.txt
```

---

## 2. Quick Start: Encryption & Decryption

### 2.1 Basic Byte Encryption

```python
from crypto import encrypt_bytes, decrypt_bytes

# 1. Define a 32-byte (256-bit) Master Key
master_key = b"Nagamrutha_Research_Master_Key_32B"
payload = b"Confidential Medical Telemetry Payload"

# 2. Encrypt Payload
encrypted_pkg = encrypt_bytes(payload, master_key)
print(f"Ciphertext (hex): {encrypted_pkg.ciphertext.hex()[:32]}...")
print(f"MAC Tag (hex):    {encrypted_pkg.mac_tag.hex()[:32]}...")

# 3. Decrypt Payload
decrypted_payload = decrypt_bytes(encrypted_pkg, master_key)
assert decrypted_payload == payload
print("Decryption successful!")
```

---

## 3. Authenticated Encryption with Associated Data (AD)

Associated Data (AD) is authenticated by the HMAC-SHA256 tag without being encrypted (e.g. cleartext network headers).

```python
from crypto import encrypt_bytes, decrypt_bytes

master_key = b"Nagamrutha_Research_Master_Key_32B"
payload = b"Sensor Reading: 37.5 C"
associated_data = b"Header: Device-ID=IoT-Node-44"

# Encrypt with Associated Data
pkg = encrypt_bytes(payload, master_key, associated_data=associated_data)

# Decrypt with matching Associated Data
result = decrypt_bytes(pkg, master_key, associated_data=associated_data)
assert result == payload

# Attempting to decrypt with altered AD fails
try:
    decrypt_bytes(pkg, master_key, associated_data=b"Header: Device-ID=TAMPERED")
except Exception as e:
    print(f"Authentication Failed as expected: {e}")
```

---

## 4. Benchmark Execution & Security Validation

### 4.1 Run Test Suite (500+ Tests)

```powershell
$env:PYTHONPATH="."
python -m pytest
```

### 4.2 Run Master Reproducibility Pipeline

```powershell
python scripts/run_phase2_5_reproducibility.py
```

---

## 5. Troubleshooting Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ImportError: No module named 'crypto'` | `PYTHONPATH` not set | Set `$env:PYTHONPATH="."` before executing python scripts. |
| `AuthenticationError: Invalid MAC tag` | Altered ciphertext, salt, or AD | Verify master key, associated data, and ciphertext integrity. |
| `ValueError: Master key must be 32 bytes` | Incorrect key length | Ensure key is exactly 32 bytes (256 bits). |
