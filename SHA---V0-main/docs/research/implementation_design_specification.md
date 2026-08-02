# Implementation Design Specification (IDS): KDR-CA-AEAD System

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Role:** Principal Software Architect, Cryptography Engineer, & IEEE Systems Designer  
**Target Repository:** `https://github.com/CHINTANSHETTY/SHA---V0`  
**Primary Output Artifact:** `implementation_design_specification.md`  

---

## 1. System Architecture & Dependency Graph

The KDR-CA-AEAD system is structured into a modular 4-tier architecture:
1. **Cryptographic Core Tier (`crypto/`)**: Implements HKDF-SHA256 key derivation, dynamic key-dependent CA transition rules, block permutations, and HMAC-SHA256 authenticated encryption.
2. **Persistence Tier (`database/`)**: Manages SQLite storage, Argon2id password hashing, and encrypted payload serialization.
3. **Presentation & API Tier (`web/`)**: Flask controller handling HTTP routing, user session authentication, and Jinja2 interface templates.
4. **Validation & Benchmark Tier (`tests/`, `benchmarks/`)**: Automated unit tests, integration tests, SAC matrix calculations, and NIST SP 800-22 statistical test suite execution.

```
                                      ┌─────────────────────────────────┐
                                      │        Web Layer (web/)         │
                                      │   app.py (Flask Controller)     │
                                      └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │    Database Tier (database/)    │
                                      │   db_manager.py (Argon2id + SQL)│
                                      └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │    Crypto Tier (crypto/)        │
                                      │  encrypt.py / decrypt.py AEAD   │
                                      └────────────────┬────────────────┘
                                                       │
                           ┌───────────────────────────┴───────────────────────────┐
                           ▼                                                       ▼
              ┌─────────────────────────┐                             ┌─────────────────────────┐
              │   key_schedule.py       │                             │    dynamic_ca.py        │
              │  (HKDF Expansion)       │                             │  (Keyed CA Transitions) │
              └────────────┬────────────┘                             └────────────┬────────────┘
                           │                                                       │
                           └───────────────────────────┬───────────────────────────┘
                                                       ▼
                                          ┌─────────────────────────┐
                                          │   authentication.py     │
                                          │  (HMAC-SHA256 AEAD Tag) │
                                          └─────────────────────────┘
```

---

## 2. Directory & File Structure

```text
SHA/
├── crypto/
│   ├── __init__.py
│   ├── hkdf.py               # HKDF-SHA256 Key Derivation Function (NIST SP 800-56C)
│   ├── key_schedule.py       # Key Expansion (K_r rule keys, K_c cipher key, K_a MAC key)
│   ├── dynamic_ca.py         # Keyed Dynamic Cellular Automata Local Rule Engine
│   ├── authentication.py     # HMAC-SHA256 AEAD Tag Generation & Constant-Time Verification
│   ├── encrypt.py            # High-level AEAD Payload Encryptor
│   └── decrypt.py            # High-level AEAD Payload Decryptor & Verification
├── database/
│   ├── __init__.py
│   ├── db_manager.py         # SQLite Persistence & Argon2id Password Hashing
│   └── models.py             # Data Access Objects (DAO) & Schema Definitions
├── web/
│   ├── __init__.py
│   ├── app.py                # Flask Web Controller
│   ├── static/
│   │   ├── style.css         # Styling CSS
│   │   └── script.js         # Frontend Logic
│   └── templates/
│       ├── login.html
│       ├── dashboard.html
│       ├── encrypt.html
│       ├── decrypt.html
│       ├── records.html
│       ├── editPatient.html
│       └── patient.html
├── tests/
│   ├── __init__.py
│   ├── test_hkdf.py          # Unit tests for HKDF-SHA256
│   ├── test_ca_engine.py     # Unit tests for Keyed Dynamic CA transitions
│   ├── test_auth.py          # Unit tests for HMAC-SHA256 AEAD tag
│   ├── test_crypto_pipeline.py # End-to-end encryption/decryption integration tests
│   └── test_database.py      # Unit tests for database & Argon2id password hashing
├── benchmarks/
│   ├── __init__.py
│   ├── avalanche_test.py     # Strict Avalanche Criterion (SAC) & BIC Heatmaps
│   ├── nist_sp800_22.py      # NIST SP 800-22 Randomness Test Suite
│   └── performance.py        # Throughput (MB/s), Memory & CPU Benchmarking vs AES-GCM
├── docs/
│   ├── ieee_paper.tex        # IEEE Double-Column LaTeX Manuscript
│   └── architecture.png      # Architecture Diagrams
├── requirements.txt          # Python Dependencies (Flask, argon2-cffi, pytest, etc.)
└── .gitignore                # Git Exclusions
```

---

## 3. Module API Specification

### 3.1 `crypto/hkdf.py`
- **Purpose**: Derives cryptographically strong keying material from low-entropy master keys using HMAC-SHA256.
- **Functions**:
  ```python
  def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
      """
      Extracts a pseudorandom key (PRK) from Input Keying Material (IKM).
      Inputs: salt (16 bytes), ikm (master password/key bytes)
      Outputs: PRK (32 bytes)
      Exceptions: ValueError if ikm is empty.
      """

  def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
      """
      Expands PRK to output keying material (OKM) of desired length.
      Inputs: prk (32 bytes), info (context string bytes), length (bytes requested)
      Outputs: okm (length bytes)
      Exceptions: ValueError if length > 255 * 32.
      """
  ```

---

### 3.2 `crypto/key_schedule.py`
- **Purpose**: Generates sub-keys ($K_r, K_c, K_a$) and dynamic CA local rule mappings from master keys.
- **Classes**:
  ```python
  class KeySchedule:
      def __init__(self, master_password: str, salt: bytes, nonce: bytes):
          """
          Derives sub-keys for CA rules (K_r: 32 bytes), Cipher (K_c: 32 bytes), and MAC (K_a: 32 bytes).
          """
      def get_ca_rule_table(self) -> list[int]:
          """Returns array of 8-bit rule numbers derived from K_r."""
      def get_cipher_key(self) -> bytes:
          """Returns 32-byte key K_c."""
      def get_mac_key(self) -> bytes:
          """Returns 32-byte key K_a."""
  ```

---

### 3.3 `crypto/dynamic_ca.py`
- **Purpose**: Keyed dynamic cellular automata local state transition engine.
- **Functions**:
  ```python
  def apply_keyed_ca_forward(blocks: list[int], rule_table: list[int]) -> list[int]:
      """
      Applies local transition rules R_k dynamically selected by rule_table[i] on 8-bit blocks.
      Inputs: blocks (list of uint8), rule_table (list of uint8)
      Outputs: transformed_blocks (list of uint8)
      """

  def apply_keyed_ca_inverse(blocks: list[int], rule_table: list[int]) -> list[int]:
      """
      Applies inverse local transition rules to recover original blocks.
      Inputs: transformed_blocks (list of uint8), rule_table (list of uint8)
      Outputs: original_blocks (list of uint8)
      """
  ```

---

### 3.4 `crypto/authentication.py`
- **Purpose**: HMAC-SHA256 tag generation and constant-time integrity verification.
- **Functions**:
  ```python
  def generate_mac_tag(mac_key: bytes, nonce: bytes, salt: bytes, ciphertext: bytes) -> bytes:
      """
      Computes 32-byte HMAC-SHA256 tag T over (Nonce || Salt || Ciphertext).
      """

  def verify_mac_tag(mac_key: bytes, nonce: bytes, salt: bytes, ciphertext: bytes, expected_tag: bytes) -> bool:
      """
      Verifies MAC tag in constant-time using hmac.compare_digest.
      Returns True if valid, False otherwise.
      """
  ```

---

### 3.5 `crypto/encrypt.py` & `crypto/decrypt.py`
- **Functions**:
  ```python
  def encrypt_payload(plaintext: str, password: str) -> dict[str, str]:
      """
      Encrypts plaintext payload using KDR-CA-AEAD.
      Returns JSON-compatible dict: {"nonce": hex, "salt": hex, "ciphertext": hex, "tag": hex}
      """

  def decrypt_payload(package: dict[str, str], password: str) -> str:
      """
      Decrypts KDR-CA-AEAD package after verifying HMAC tag.
      Raises IntegrityError if HMAC verification fails.
      Returns original plaintext string.
      """
  ```

---

## 4. Data Structures & Serialized Payload Schema

### 4.1 Encrypted Payload JSON Package Schema
```json
{
  "version": "KDR-CA-AEAD-v1",
  "nonce": "a1b2c3d4e5f6789012345678",
  "salt": "f0e9d8c7b6a54321123456789abcdef0",
  "ciphertext": "3f8a9b...",
  "tag": "e4d3c2b1a09876543210fedcba9876543210fedcba9876543210fedcba987654"
}
```

### 4.2 Database Schema (`database/models.py`)

```sql
CREATE TABLE doctors (
    doctorId TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,  -- Argon2id hashed password
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patientRecords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patientId TEXT NOT NULL,
    encrypted_name TEXT NOT NULL,  -- Encrypted patient name
    encrypted_payload TEXT NOT NULL, -- Full JSON KDR-CA-AEAD encrypted package
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Encryption & Decryption Sequence Workflows

```
ENCRYPTION WORKFLOW
[Plaintext String P] + [User Password Pass]
       │
       ├─► Generate Salt S (16 random bytes)
       ├─► Generate Nonce N (12 random bytes)
       │
       ▼
 [ HKDF Expansion (Pass, S, N) ] ──► Derives (K_r, K_c, K_a)
       │
       ▼
 [ Plaintext P ] ──► [ Convert to 8-bit Bytes ] ──► [ Keyed Dynamic CA (K_r) ] ──► [ Permute ]
                                                                                      │
                                                                                      ▼
 [ Ciphertext C ] ◄───────────────────────────────────────────── [ Bitwise XOR (PRNG(K_c)) ]
       │
       ▼
 [ Compute HMAC Tag T ] = HMAC-SHA256(K_a, N || S || C)
       │
       ▼
 [ Output Package: (N, S, C, T) ]
```

```
DECRYPTION WORKFLOW
[ Package (N, S, C, T) ] + [ User Password Pass ]
       │
       ▼
 [ HKDF Expansion (Pass, S, N) ] ──► Derives (K_r, K_c, K_a)
       │
       ▼
 [ HMAC Tag Verification: Compare_Digest(T, HMAC(K_a, N || S || C)) ]
       ├─► IF INVALID: Raise IntegrityError ("Corrupted Payload or Wrong Password") -> ABORT ❌
       └─► IF VALID:  PROCEED TO DECRYPTION CONTINUATION ✓
                           │
                           ▼
              [ Reverse Bitwise XOR (PRNG(K_c)) ]
                           │
                           ▼
              [ Reverse Keyed Dynamic CA (K_r) ] ──► [ Convert Bytes to String ]
                                                          │
                                                          ▼
                                              [ Recovered Plaintext P ]
```

---

## 6. Error Handling & Security Logging Strategy

### 6.1 Custom Exceptions
- `CryptoError`: Base class for cryptographic failures.
- `AuthenticationError(CryptoError)`: Raised when HMAC-SHA256 tag verification fails.
- `KeyDerivationError(CryptoError)`: Raised on invalid salt/nonce/password input.
- `CorruptedPayloadError(CryptoError)`: Raised on malformed JSON package structures.

### 6.2 Security Logging Guidelines
- **Rule 1**: NEVER log master passwords, raw keys ($K_r, K_c, K_a$), or plaintext medical records.
- **Rule 2**: Log security events with timestamp and client IP: `"FAILED_LOGIN: doctorId=doctor01, IP=127.0.0.1"`, `"HMAC_VERIFICATION_FAILURE: record_id=4"`.

---

## 7. Definition of Done (DoD) per Module

Every file in the codebase must satisfy the following checklist before being marked **DONE**:

- [ ] **Functional**: Implements specified APIs and passes all edge cases.
- [ ] **Type Annotations**: 100% type hinted (`mypy` compliant).
- [ ] **Docstrings**: Google-style docstrings for every class and function.
- [ ] **Unit Tests**: Minimum 90% branch code coverage (`pytest`).
- [ ] **Security Hardened**: Zero hardcoded credentials; constant-time operations for comparison functions.
- [ ] **Traceable**: Mapped directly to IEEE paper section (Section IV - System Design).

---

## 8. File-by-File Implementation Order

```
[ Step 1: crypto/hkdf.py ] ──► Implement & Unit Test HKDF Key Derivation
          │
          ▼
[ Step 2: crypto/key_schedule.py ] ──► Implement Key Expansion & Rule Tables
          │
          ▼
[ Step 3: crypto/dynamic_ca.py ] ──► Implement Keyed Dynamic CA State Engine
          │
          ▼
[ Step 4: crypto/authentication.py ] ──► Implement Constant-Time HMAC AEAD Verification
          │
          ▼
[ Step 5: crypto/encrypt.py & decrypt.py ] ──► High-Level Encrypt/Decrypt Functions
          │
          ▼
[ Step 6: database/db_manager.py ] ──► SQLite Hardening & Argon2id Password Hashing
          │
          ▼
[ Step 7: web/app.py ] ──► Update Flask Controller & Web Routes
          │
          ▼
[ Step 8: tests/ & benchmarks/ ] ──► Execute SAC, NIST SP 800-22 & Throughput Tests
```

---

## 9. Next Steps

With the Implementation Design Specification finalized and frozen, we are ready to proceed with step-by-step code implementation starting with `crypto/hkdf.py`.
