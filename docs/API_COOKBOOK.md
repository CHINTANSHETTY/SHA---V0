# KDR-CA-AEAD Practical API Cookbook

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Document Version:** 1.0.0  

---

## 1. Recipe 1: Basic Encryption & Decryption

```python
from crypto import encrypt_bytes, decrypt_bytes

# Master key must be exactly 32 bytes (256 bits)
master_key = b"Nagamrutha_Research_Master_Key_32B"
message = b"Secret Payload"

# Encrypt
encrypted = encrypt_bytes(message, master_key)

# Decrypt
decrypted = decrypt_bytes(encrypted, master_key)
assert decrypted == message
```

---

## 2. Recipe 2: Associated Data (AD) Header Authentication

```python
from crypto import encrypt_bytes, decrypt_bytes

master_key = b"Nagamrutha_Research_Master_Key_32B"
payload = b"ECG Sensor Reading Data"
header = b"TelemetryHeader: Node=7"

# Encrypt with Associated Data
pkg = encrypt_bytes(payload, master_key, associated_data=header)

# Decrypt with Associated Data
decrypted = decrypt_bytes(pkg, master_key, associated_data=header)
assert decrypted == payload
```

---

## 3. Recipe 3: Robust Exception Handling

```python
from crypto import encrypt_bytes, decrypt_bytes

master_key = b"Nagamrutha_Research_Master_Key_32B"
pkg = encrypt_bytes(b"Sensitive Data", master_key)

# Tamper with ciphertext
tampered_ciphertext = bytearray(pkg.ciphertext)
tampered_ciphertext[0] ^= 0xFF
pkg.ciphertext = bytes(tampered_ciphertext)

try:
    decrypt_bytes(pkg, master_key)
except Exception as err:
    print(f"Decryption rejected corrupted package: {err}")
```

---

## 4. Recipe 4: Batch Processing Multiple Payloads

```python
from crypto import encrypt_bytes, decrypt_bytes

master_key = b"Nagamrutha_Research_Master_Key_32B"
messages = [b"Payload 1", b"Payload 2", b"Payload 3"]

# Batch Encrypt
packages = [encrypt_bytes(msg, master_key) for msg in messages]

# Batch Decrypt
results = [decrypt_bytes(pkg, master_key) for pkg in packages]
assert results == messages
print(f"Successfully processed {len(results)} items in batch.")
```

---

## 5. Recipe 5: Pytest Integration Fixtures

```python
import pytest
from crypto import encrypt_bytes, decrypt_bytes

@pytest.fixture
def crypto_key():
    return b"Nagamrutha_Research_Master_Key_32B"

def test_aead_roundtrip(crypto_key):
    payload = b"Unit test payload"
    pkg = encrypt_bytes(payload, crypto_key)
    assert decrypt_bytes(pkg, crypto_key) == payload
```
