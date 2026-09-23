# KDR-CA-AEAD User Guide

This user guide provides instructions for using **KDR-CA-AEAD** via the Python library API, Command-Line Interface (CLI), and Flask Web Application.

---

## 1. Using KDR-CA-AEAD in Python

The `crypto` package provides high-level functions for authenticated encryption and decryption.

### 1.1 Binary Data Encryption (`encrypt_bytes` & `decrypt_bytes`)

```python
from crypto import encrypt_bytes, decrypt_bytes, EncryptedPackage

# Master key must be a 32-byte secret (256 bits)
master_key = b"0123456789abcdef0123456789abcdef"
payload = b"Confidential payload requiring authenticated encryption."
associated_data = b"Header-Metadata-ID-99"

# 1. Encrypt payload
package: EncryptedPackage = encrypt_bytes(
    data=payload,
    key=master_key,
    associated_data=associated_data
)

print(f"Ciphertext Length: {len(package.ciphertext)} bytes")
print(f"MAC Tag: {package.mac.hex()}")

# 2. Decrypt payload
decrypted_payload = decrypt_bytes(
    package=package,
    key=master_key,
    associated_data=associated_data
)

assert decrypted_payload == payload
print("Decryption Successful!")
```

### 1.2 Serialization & Deserialization (`EncryptedPackage`)

The `EncryptedPackage` object contains salt, nonce, ciphertext, and MAC tag. It can be serialized to JSON or bytes for storage or transmission:

```python
# Convert to dictionary or JSON
package_dict = package.to_dict()
json_str = package.to_json()

# Reconstruct from JSON
restored_package = EncryptedPackage.from_json(json_str)
```

---

## 2. Command-Line Interface (CLI) Utilities

KDR-CA-AEAD includes convenient command-line scripts for encrypting and decrypting files or strings directly from the terminal.

### 2.1 File Encryption (`encrypt.py`)

```powershell
python encrypt.py --key "MySecretKey32BytesLong123456789" --input secret_data.txt --output secret_data.enc
```

### 2.2 File Decryption (`decrypt.py`)

```powershell
python decrypt.py --key "MySecretKey32BytesLong123456789" --input secret_data.enc --output restored_data.txt
```

---

## 3. Flask Web Application (`app.py`)

KDR-CA-AEAD includes a Web GUI and REST service for interactive encryption, record logging, and security metrics visualization.

### 3.1 Launching the Web Server

```powershell
$env:PYTHONPATH="."
python app.py
```

Output:
```text
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

### 3.2 Key Web Features
- **Encryption Panel**: Enter plain text messages and associated metadata to perform live encryption.
- **Decryption Panel**: Input ciphertext packages and keys for instant verification and decryption.
- **Records Log (`records.db`)**: View historical encryption jobs, MAC verification logs, and timestamped audit entries.
- **REST Endpoints**:
  - `POST /api/encrypt`: JSON payload encryption endpoint.
  - `POST /api/decrypt`: JSON payload decryption endpoint.
  - `GET /api/records`: Fetch audit record entries.
