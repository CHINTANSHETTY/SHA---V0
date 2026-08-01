# IMPLEMENTATION PLAN: SPRINT 1.2 (KEY SCHEDULE ENGINE)

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Module Target:** `crypto/engine/key_schedule.py`  
**Assigned Developer / Lead:** Chintan (Project Lead, Cryptography Lead, Research Lead)  
**Phase:** Phase 1 (Cryptographic Foundation) – Sub-Phase 1.2 (Key Schedule Engine)  
**IEEE Paper Mapping:** Section IV-B (Dynamic Sub-Key Expansion Subsystem)  
**Primary Output Location:** `docs/sprints/sprint_1_2/work_package.md`  
**Document Status:** REVIEW & FREEZE PLAN (NO CODE INCLUDED)  

---

## 1. Module Purpose

`crypto/engine/key_schedule.py` serves as the central key expansion and key separation engine in the KDR-CA-AEAD architecture. 

### Key Relationships
- **Relationship with `hkdf.py`**: Consumes `hkdf()` to expand 96 bytes of cryptographically pseudorandom output keying material (OKM) derived from master passwords, salts, and nonces.
- **Relationship with `dynamic_ca.py`**: Provides $K_r$ (32 bytes), which formats into an array of 32 8-bit Cellular Automata local transition rules ($R_0 \dots R_{31}$).
- **Relationship with `encrypt.py` / `decrypt.py`**: Provides $K_c$ (32 bytes) for CTR-PRNG stream cipher keystream expansion.
- **Relationship with `authentication.py`**: Provides $K_a$ (32 bytes) for HMAC-SHA256 authenticated tag calculation.

---

## 2. Architecture Position & Data Flow

```
[ Master Password (str) ] + [ Salt S (16 bytes) ] + [ Nonce N (12 bytes) ]
                                   │
                                   ▼
                   [ HKDF Expansion Engine (96 bytes) ]
                                   │
                                   ▼
                    KeySchedule (key_schedule.py)
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
  [ Rule Key K_r ]         [ Cipher Key K_c ]        [ MAC Key K_a ]
  (32 uint8 Rules)         (32 bytes Keystream)       (32 bytes HMAC)
         │                         │                         │
         ▼                         ▼                         ▼
[ Dynamic CA Engine ]   [ Stream XOR Encryption ]  [ HMAC-SHA256 AEAD Tag ]
(dynamic_ca.py)         (encrypt.py / decrypt.py)  (authentication.py)
```

---

## 3. Module Responsibilities

### What the Module SHALL Do:
1. SHALL accept low-entropy master password strings, 16-byte random salts, and 12-byte random nonces.
2. SHALL invoke `hkdf()` with context-specific info strings (`b"KDR-CA-AEAD-v1-subkeys|" + nonce`) to derive 96 bytes of OKM.
3. SHALL enforce strict **key separation**: $K_r \neq K_c \neq K_a$.
4. SHALL expose clear, typed accessor methods for derived sub-keys (`get_ca_rule_table()`, `get_cipher_key()`, `get_mac_key()`).

### What the Module SHALL NOT Do:
1. SHALL NOT store master passwords in persistent object memory longer than initial derivation.
2. SHALL NOT perform plaintext encryption or decryption directly (delegated to `encrypt.py` / `decrypt.py`).
3. SHALL NOT log or output raw sub-key material to stdout or log streams.

---

## 4. Inputs Specification

| Input Parameter | Type | Required Length | Source | Security Requirements |
| :--- | :--- | :---: | :--- | :--- |
| `master_password` | `str` | $\ge 1$ char | User / Web Form | Must be converted to UTF-8 bytes; never logged. |
| `salt` | `BytesLike` | Exactly 16 bytes | CSPRNG (`random.py`) | Must be non-secret but unique per user/record. |
| `nonce` | `BytesLike` | Exactly 12 bytes | CSPRNG (`random.py`) | Must be cryptographically unique per encryption event. |

---

## 5. Outputs Specification

| Output Property | Type | Byte Length | Purpose | Consumer Module |
| :--- | :--- | :---: | :--- | :--- |
| `get_ca_rule_table()` | `list[int]` | 32 uint8 rules | Local CA rule parameters ($R_0 \dots R_{31}$) | `dynamic_ca.py` |
| `get_cipher_key()` | `bytes` | 32 bytes | Keystream expansion key ($K_c$) | `encrypt.py` / `decrypt.py` |
| `get_mac_key()` | `bytes` | 32 bytes | HMAC-SHA256 tag key ($K_a$) | `authentication.py` |

---

## 6. Internal Component Breakdown

1. **Parameter Validator**: Validates type, presence, and exact byte length of `master_password`, `salt`, and `nonce`.
2. **HKDF Sub-Key Expander**: Calls `crypto.primitives.hkdf.hkdf()` requesting 96 bytes of output keying material.
3. **Key Separator & Rule Formatter**: Slices the 96-byte array into 3 distinct 32-byte sub-keys and converts $K_r$ into a list of 32 `uint8` integers.

---

## 7. Public API Design

### Class: `KeySchedule`

```python
class KeySchedule:
    """Manages dynamic expansion and separation of sub-keys (K_r, K_c, K_a)."""

    def __init__(self, master_password: str, salt: BytesLike, nonce: BytesLike) -> None:
        """Initializes KeySchedule and expands 96 bytes of sub-key material.

        Preconditions:
            - master_password must be a non-empty string.
            - salt must be a bytes-like object of exactly 16 bytes.
            - nonce must be a bytes-like object of exactly 12 bytes.

        Postconditions:
            - Derives 32-byte K_r, 32-byte K_c, and 32-byte K_a.

        Raises:
            KeyDerivationError: If input validation fails.
            TypeError: If input parameter types are invalid.
        """

    def get_ca_rule_table(self) -> list[int]:
        """Returns array of 32 uint8 integers for Cellular Automata rules."""

    def get_cipher_key(self) -> bytes:
        """Returns 32-byte cipher key K_c for stream encryption."""

    def get_mac_key(self) -> bytes:
        """Returns 32-byte MAC key K_a for HMAC authentication."""
```

---

## 8. Internal Helper Functions

- `_validate_inputs(master_password: str, salt: BytesLike, nonce: BytesLike) -> None`: Private static validator enforcing password non-emptiness, 16-byte salt length, and 12-byte nonce length.

---

## 9. Data Structures & Types

- `BytesLike: TypeAlias = bytes | bytearray`
- `KeySchedule` (Class managing sub-key derivation state)

---

## 10. Security Requirements

1. **Key Independence**: Sub-keys $K_r, K_c, K_a$ must be computationally independent (guaranteed by HKDF pseudo-randomness).
2. **Strict Length Enforcement**: Enforces exactly 16-byte salt and 12-byte nonce to prevent key derivation reuse under variable-length parameters.
3. **Zero Secret Logging**: Prohibits logging or string printing of $K_r, K_c, K_a$.

---

## 11. Error Handling Strategy

- **`KeyDerivationError`**: Raised when `master_password` is empty, or `salt` length $\neq 16$, or `nonce` length $\neq 12$.
- **`TypeError`**: Raised when non-string passwords or non-bytes-like salts/nonces are passed.

---

## 12. Integration Plan

```
[ hkdf.py ] ──► KeySchedule (key_schedule.py)
                    │
                    ├──► dynamic_ca.py (consumes get_ca_rule_table())
                    ├──► encrypt.py / decrypt.py (consumes get_cipher_key())
                    └──► authentication.py (consumes get_mac_key())
```

---

## 13. Testing Plan

1. **Unit Tests**: Test 96-byte derivation consistency for fixed password, salt, and nonce.
2. **Key Separation Tests**: Verify $K_r \neq K_c \neq K_a$.
3. **Different Parameter Tests**: Verify changing password, salt, or nonce produces completely distinct sub-key sets.
4. **Boundary & Negative Tests**: Verify `KeyDerivationError` is raised for empty password, 15-byte salt, or 11-byte nonce.

---

## 14. Documentation Plan

- **Module Metadata**: Standard header docstrings referencing IEEE Section IV-B and NIST SP 800-56C.
- **API Docstrings**: Complete Google-style docstrings with `Preconditions`, `Postconditions`, `Args`, `Returns`, and `Raises`.

---

## 15. GitHub Workflow

```bash
git checkout main
git pull origin main

# After implementation & test verification
git add crypto/engine/key_schedule.py tests/unit/test_key_schedule.py
git commit -m "feat(crypto): Implement KeySchedule dynamic sub-key expansion engine"
git push origin main
```

---

## 16. Implementation Risks & Mitigations

- **Risk**: Salt or Nonce parameter length mismatch leading to key stream degradation.
- **Mitigation**: Enforce strict 16-byte salt and 12-byte nonce validation checks in `__init__`.

---

## 17. Acceptance Criteria

- [x] Sub-keys $K_r, K_c, K_a$ derived deterministically via `hkdf`.
- [x] `get_ca_rule_table()` returns exactly 32 `uint8` integers $[0 \dots 255]$.
- [x] Sub-keys $K_r, K_c, K_a$ pass mutual independence checks.
- [x] Unit tests pass 100% in `tests/unit/test_key_schedule.py`.

---

## 18. Definition of Done (DoD)

- [ ] `crypto/engine/key_schedule.py` implemented.
- [ ] 100% Type hints and Google docstrings added.
- [ ] Unit tests passing in `tests/unit/test_key_schedule.py`.
- [ ] Zero secret logging.
- [ ] Pushed to GitHub `main` branch.

---

## 19. Handover to Phase 1.3 (Dynamic CA Engine)

Upon completion of Phase 1.2, `crypto/engine/key_schedule.py` provides `KeySchedule.get_ca_rule_table()`. 

The developer for **Phase 1.3 (`crypto/engine/dynamic_ca.py`)** will consume `rule_table: list[int]` to dynamically select Cellular Automata local state transition rules $R_i$ for payload block transformations.
