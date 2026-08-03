# Phase 2.5 – System Integration Architecture Specification

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**IEEE Mapping:** Section IV – System Architecture & Module Integration  
**Version:** 1.0.0 (Integrated Phase 2.5 Candidate)  

---

## 1. Overview

This document specifies the public API surfaces, inter-module data flow, and architectural boundaries of the integrated **KDR-CA-AEAD** cryptographic framework.

All Phase 2 modules have been unified into `crypto`:
- `crypto.engine.encrypt` / `crypto.engine.decrypt`
- `crypto.engine.key_schedule`
- `crypto.engine.dynamic_ca`
- `crypto.ca.engine` / `crypto.ca.rules` / `crypto.ca.mapping`
- `crypto.primitives.hkdf` / `crypto.primitives.hmac` / `crypto.primitives.random`
- `crypto.analysis`

---

## 2. Public API Surface

### 2.1 Authenticated Encryption

```python
from crypto import encrypt_bytes, encrypt_payload

# Raw Binary Encryption
package = encrypt_bytes(
    data=b"Raw Binary Buffer",
    master_key=b"MasterSecretKey32BytesLong!",
    salt=None,             # Optional 16-byte salt override
    nonce=None,            # Optional 12-byte nonce override
    associated_data=b""    # Optional associated authenticated data
)

# String Payload Encryption
package = encrypt_payload(
    plaintext="Patient EHR Medical Telemetry Record",
    password="SecureUserPassword123"
)
```

### 2.2 Authenticated Decryption

```python
from crypto import decrypt_bytes, decrypt_payload

# Raw Binary Decryption
plaintext_bytes = decrypt_bytes(
    package=package,
    master_key=b"MasterSecretKey32BytesLong!",
    associated_data=b""
)

# String Payload Decryption
plaintext_str = decrypt_payload(
    package=package,
    password="SecureUserPassword123"
)
```

---

## 3. Data Flow & Subsystem Interfaces

```
+--------------------------------------------------------------------------+
|                          encrypt_bytes(data, key)                        |
+--------------------------------------------------------------------------+
                                     |
                                     v
                  KeySchedule.from_master_key(key, salt, nonce)
                                     |
                                     v
                           Derived Key Material
                  +-----------------------------------+
                  | rule_seed | cipher_key | mac_key  |
                  +-----------------------------------+
                                     |
              +----------------------+----------------------+
              |                                             |
              v                                             v
apply_keyed_ca_forward(data, rule_table)          _generate_keystream(cipher_key, nonce, len)
              |                                             |
              +----------------------+----------------------+
                                     |
                                     v
                        Ciphertext = Transformed ^ Keystream
                                     |
                                     v
                    HMAC-SHA256(mac_key, Nonce || Salt || AD || Ciphertext)
                                     |
                                     v
                             EncryptedPackage
```

---

## 4. Error Handling & Exception Hierarchy

- `CryptoError`: Base exception class for all cryptographic pipeline errors.
  - `KeyDerivationError`: Raised during invalid parameter validation in HKDF key expansion.
  - `AuthenticationError`: Raised when AEAD tag verification fails or ciphertext/AD/nonce has been tampered with.
