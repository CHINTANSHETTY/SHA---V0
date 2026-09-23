# `crypto.engine` API Reference

**Subsystem:** High-Level Authenticated Encryption, Decryption, Key Scheduling, and Dynamic CA Permutation  
**IEEE Mapping:** Section IV-B, IV-C, IV-D, IV-E  

---

## Overview

The `crypto.engine` package integrates HKDF key derivation, Candidate A-Chain Dynamic Cellular Automata permutations, HMAC-SHA256 CTR-PRNG keystream generation, and constant-time HMAC tag computation.

---

## Public Functions & Classes

### 1. `crypto.engine.encrypt.encrypt_bytes`

```python
def encrypt_bytes(
    data: BytesLike,
    master_key: BytesLike,
    salt: BytesLike | None = None,
    nonce: BytesLike | None = None,
    associated_data: BytesLike = b""
) -> EncryptedPackage
```

Encrypts raw binary data bytes using KDR-CA-AEAD authenticated cipher.

- **Parameters:**
  - `data`: Raw binary payload bytes or bytearray.
  - `master_key`: Secret master key or password bytes.
  - `salt`: Optional 16-byte salt override.
  - `nonce`: Optional 12-byte nonce override.
  - `associated_data`: Optional associated authenticated data bytes.
- **Returns:** `EncryptedPackage` containing salt, nonce, ciphertext, and HMAC AEAD tag.
- **Raises:** `CryptoError` if payload data is `None` or `master_key` is empty/invalid.

---

### 2. `crypto.engine.decrypt.decrypt_bytes`

```python
def decrypt_bytes(
    package: EncryptedPackage,
    master_key: BytesLike,
    associated_data: BytesLike = b""
) -> bytes
```

Decrypts and authenticates an `EncryptedPackage` returning raw payload bytes.

- **Parameters:**
  - `package`: `EncryptedPackage` object containing salt, nonce, ciphertext, and tag.
  - `master_key`: Secret master key or password bytes.
  - `associated_data`: Optional associated authenticated data bytes.
- **Returns:** Original plaintext raw bytes.
- **Raises:** `CryptoError` if package or master key is invalid; `AuthenticationError` if tag verification fails.

---

### 3. `crypto.engine.key_schedule.KeySchedule`

```python
class KeySchedule:
    @classmethod
    def from_master_key(
        cls,
        master_key: BytesLike,
        salt: BytesLike,
        nonce: BytesLike
    ) -> KeySchedule:
        ...

    def export_key_material(self) -> KeyMaterial:
        ...
```

Manages domain-separated HKDF-SHA256 expansion into:
- `rule_seed` ($K_r$): 32-byte seed deriving 32 uint8 CA transition rules.
- `cipher_key` ($K_c$): 32-byte key for CTR keystream PRNG.
- `mac_key` ($K_a$): 32-byte key for HMAC-SHA256 AEAD tag calculation.

---

### 4. `crypto.engine.dynamic_ca.DynamicCAEngine`

```python
class DynamicCAEngine:
    def __init__(self, rule_table: Sequence[int], delta: int = 13) -> None: ...

    @classmethod
    def from_key_material(cls, key_material: KeyMaterial, delta: int = 13) -> DynamicCAEngine: ...

    def transform_forward(self, data: BytesLike) -> bytes: ...

    def transform_inverse(self, data: BytesLike) -> bytes: ...
```

Executes Candidate A-Chain non-linear permutation-substitution state evolution over input byte streams.
