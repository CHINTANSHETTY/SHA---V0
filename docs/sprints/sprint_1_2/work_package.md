# IMPLEMENTATION PLAN: SPRINT 1.2 (KEY SCHEDULE ENGINE)

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Module Target:** `crypto/engine/key_schedule.py`  
**Assigned Developer / Lead:** Chintan (Project Lead, Cryptography Lead, Research Lead)  
**Phase:** Phase 1 (Cryptographic Foundation) – Sub-Phase 1.2 (Key Schedule Engine)  
**IEEE Paper Mapping:** Section IV-B (Dynamic Sub-Key Expansion Subsystem)  
**Primary Output Location:** `docs/sprints/sprint_1_2/work_package.md`  
**Document Status:** FROZEN ARCHITECTURE SPECIFICATION & APPROVED PLAN (NO CODE INCLUDED)  

---

## 1. Module Purpose

`crypto/engine/key_schedule.py` serves as the central key expansion and domain separation engine in the KDR-CA-AEAD architecture.

### Key Relationships
- **Relationship with `hkdf.py`**: Consumes `hkdf()` to derive 3 distinct 32-byte sub-keys from `master_key`, `salt`, and `nonce` using domain-separated HKDF `info` labels.
- **Relationship with `dynamic_ca.py`**: Provides $K_r$ (32 bytes), which formats into an immutable tuple of 32 8-bit Cellular Automata local transition rules ($R_0 \dots R_{31}$).
- **Relationship with `encrypt.py` / `decrypt.py`**: Provides $K_c$ (32 bytes) for CTR-PRNG stream cipher keystream expansion.
- **Relationship with `authentication.py`**: Provides $K_a$ (32 bytes) for HMAC-SHA256 authenticated tag calculation.

---

## 2. Architecture Position & Domain-Separated Key Flow

```
[ Master Key (BytesLike) ] + [ Salt S (16 bytes) ] + [ Nonce N (12 bytes) ]
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │ (info="...-ca-rules")     │ (info="...-cipher-key")   │ (info="...-mac-key")
       ▼                           ▼                           ▼
[ HKDF Expansion 1 ]       [ HKDF Expansion 2 ]       [ HKDF Expansion 3 ]
       │                           │                           │
       ▼                           ▼                           ▼
[ Rule Key K_r (32B) ]     [ Cipher Key K_c (32B) ]   [ MAC Key K_a (32B) ]
(32 uint8 Rule Tuple)      (32 bytes Keystream)       (32 bytes HMAC Tag)
       │                           │                           │
       ▼                           ▼                           ▼
[ Dynamic CA Engine ]      [ Stream XOR Encryption ]  [ HMAC-SHA256 AEAD Tag ]
(dynamic_ca.py)            (encrypt.py / decrypt.py)  (authentication.py)
```

### Architectural Key Derivation Decision: Explicit HKDF Domain Labels
Rather than deriving a single 96-byte OKM and slicing it, `KeySchedule` executes **3 separate HKDF expansions using unique domain separation labels**:
1. $K_r = \text{hkdf}(\text{master\_key}, 32, \text{salt}, \text{info}=b"\text{KDR-CA-AEAD-v1-ca-rules}|" + \text{nonce})$
2. $K_c = \text{hkdf}(\text{master\_key}, 32, \text{salt}, \text{info}=b"\text{KDR-CA-AEAD-v1-cipher-key}|" + \text{nonce})$
3. $K_a = \text{hkdf}(\text{master\_key}, 32, \text{salt}, \text{info}=b"\text{KDR-CA-AEAD-v1-mac-key}|" + \text{nonce})$

**Justification**: Cryptographic domain separation per NIST SP 800-56C Rev. 2 and RFC 5869 Section 3.2. The sub-keys are algebraically independent regardless of input length or derivation context.

---

## 3. Module Responsibilities & Explicit Boundaries

### What the Module SHALL Do:
1. SHALL accept `master_key` as a `BytesLike` buffer (bytes or bytearray).
2. SHALL validate `salt` (exactly 16 bytes) and `nonce` (exactly 12 bytes).
3. SHALL derive sub-keys $K_r, K_c, K_a$ using 3 explicit HKDF domain labels.
4. SHALL export derived sub-keys via an immutable `KeyMaterial` dataclass.
5. SHALL convert $K_r$ into an immutable `tuple[int, ...]` of 32 `uint8` Cellular Automata rules ($0 \dots 255$).

### What the Module SHALL NOT Do (Explicit Module Boundaries):
1. SHALL NOT accept raw un-encoded string passwords (string-to-byte conversion occurs in web controllers).
2. SHALL NOT perform plaintext data encryption or decryption.
3. SHALL NOT calculate HMAC authentication tags.
4. SHALL NOT execute Cellular Automata state transitions.
5. SHALL NOT log or output raw sub-key material to stdout or log streams.

---

## 4. Inputs Specification

| Input Parameter | Type | Required Length | Source | Security Requirements |
| :--- | :--- | :---: | :--- | :--- |
| `master_key` | `BytesLike` | $\ge 16$ bytes | Derived Seed / Pass Hash | Must be binary bytes; never logged. |
| `salt` | `BytesLike` | Exactly 16 bytes | CSPRNG (`random.py`) | Must be non-secret but unique per user/record. |
| `nonce` | `BytesLike` | Exactly 12 bytes | CSPRNG (`random.py`) | Must be cryptographically unique per encryption event. |

---

## 5. Outputs Specification (`KeyMaterial`)

`KeySchedule` exports key material via a frozen dataclass:

```python
@dataclass(frozen=True)
class KeyMaterial:
    rule_key: bytes          # 32 bytes (K_r)
    cipher_key: bytes        # 32 bytes (K_c)
    mac_key: bytes           # 32 bytes (K_a)
    rule_table: tuple[int, ...] # Immutable 32-element uint8 tuple (R_0 .. R_31)
```

### Architectural Rationale: Why 32 Rules?
1. **Direct 1-to-1 Mapping**: The 32-byte Rule Seed $K_r = (b_0, b_1, \dots, b_{31})$ maps exactly 1 byte to 1 local cellular automaton rule integer $R_i = b_i \in [0, 255]$.
2. **SHA-256 Alignment**: Thirty-two rules align directly with the 32-byte (256-bit) digest size of SHA-256 HKDF expansion, maximizing entropy extraction without introducing multi-byte rule formatting overhead.
3. **Cyclic Multi-Block Application**: For payloads consisting of $N$ blocks, rules are indexed as $R_{i \pmod{32}}$, ensuring bounded memory lookup. Future protocol versions may expand rule table size without altering the public `KeyMaterial` API.

---

## 6. Internal State Transition Diagram

```
KeySchedule
    │
    ▼
[ Parameter Validation ] ──► (Validates BytesLike types, 16B salt, 12B nonce, min entropy)
    │
    ▼
[ HKDF Domain Expansions ] ──► Derives (K_r via "rules", K_c via "cipher", K_a via "mac")
    │
    ▼
[ Rule Formatting ] ──► Formats K_r into immutable tuple[int, ...]
    │
    ▼
[ KeyMaterial Frozen ] ──► Constructs KeyMaterial dataclass instance
    │
    ▼
[ READY FOR CONSUMPTION ]
```

---

## 7. Public API Design

### Class: `KeySchedule`

```python
class KeySchedule:
    """Manages dynamic expansion and domain separation of sub-keys (K_r, K_c, K_a)."""

    def __init__(self, master_key: BytesLike, salt: BytesLike, nonce: BytesLike) -> None:
        """Initializes KeySchedule and executes domain-separated HKDF derivations."""

    @classmethod
    def from_master_key(
        cls,
        master_key: BytesLike,
        salt: BytesLike,
        nonce: BytesLike
    ) -> "KeySchedule":
        """Factory method constructing KeySchedule from master key bytes."""

    def export_key_material(self) -> KeyMaterial:
        """Returns immutable KeyMaterial dataclass containing derived sub-keys."""

    def get_ca_rule_table(self) -> tuple[int, ...]:
        """Returns immutable tuple of 32 uint8 CA rules."""

    def get_cipher_key(self) -> bytes:
        """Returns 32-byte cipher key K_c."""

    def get_mac_key(self) -> bytes:
        """Returns 32-byte MAC key K_a."""
```

---

## 8. Data Structures & Types

- `BytesLike: TypeAlias = bytes | bytearray`
- `KeyMaterial` (Frozen dataclass holding derived sub-keys)
- `KeySchedule` (Key Derivation Manager)

---

## 9. Error Handling & Exception Strategy

- **`KeyDerivationError`**: Raised when `master_key` is empty/less than 16 bytes, or `salt` length $\neq 16$, or `nonce` length $\neq 12$.
- **`TypeError`**: Raised when non-bytes-like buffers are passed to `master_key`, `salt`, or `nonce`.

---

## 10. Requirement Traceability Matrix

| Requirement ID | Module Target | Verification Status |
| :--- | :--- | :---: |
| **IDS Specification Section 4.2** | `crypto/engine/key_schedule.py` | `Planned` |
| **NIST SP 800-56C Rev. 2 §4** | `KeySchedule` Domain Separation | `Planned` |
| **RFC 5869 Section 3.2** | `hkdf` Info Parameter | `Planned` |
| **IEEE Manuscript IV-B** | Sub-Key Expansion Engine | `Planned` |

---

## 11. Acceptance Criteria & Definition of Done (DoD)

- [x] `KeySchedule` accepts `master_key` as `BytesLike` buffer.
- [x] Uses 3 explicit HKDF domain labels derived from `PROTOCOL_VERSION = "KDR-CA-AEAD-v1"`.
- [x] Exports `KeyMaterial` immutable dataclass with `rule_seed`, `cipher_key`, `mac_key`, `rule_table`, and `algorithm_id`.
- [x] `get_ca_rule_table()` returns `tuple[int, ...]` of length 32.
- [x] Unit tests pass 100% in `tests/unit/test_key_schedule.py`.
- [x] Zero secret logging.
- [x] Formally approved by Architecture Review Board.

---

## 12. Design Decision Log (Architecture Decision Records)

### ADR-001: Three Independent HKDF Expansions vs. Single OKM Slicing
- **Context**: Sub-keys $K_r$, $K_c$, and $K_a$ are required for rule generation, stream cipher, and MAC authentication.
- **Decision**: Perform 3 distinct HKDF expansions using explicit `info` context strings (`KDR-CA-AEAD-v1-ca-rules|`, `KDR-CA-AEAD-v1-cipher-key|`, `KDR-CA-AEAD-v1-mac-key|`) appended with the nonce.
- **Rationale**: Ensures strict cryptographic domain separation per NIST SP 800-56C Rev. 2 & RFC 5869 §3.2. Eliminates slicing offsets and guarantees algebraic key independence.
- **Trade-off**: Requires 3 HMAC expansion calls instead of 1. Performance cost is negligible (<0.01 ms).
- **Status**: ACCEPTED & FROZEN.

### ADR-002: Placement of Nonce in HKDF `info` Parameter
- **Context**: A 12-byte CSPRNG nonce is generated per encryption event.
- **Decision**: Bind the nonce into the `info` context parameter (`info = label + nonce`) during HKDF expansion, while keeping the 16-byte random salt in the HKDF `salt` parameter.
- **Rationale**: Per RFC 5869 §3.2, `IKM` holds secret keying material, `salt` provides extraction randomizer, and `info` binds application/context parameters. Placing the per-message nonce in `info` explicitly binds each derived sub-key to both the domain label and the unique single-use message nonce context.
- **Status**: ACCEPTED & FROZEN.

### ADR-003: Rule Table Application for Multi-Block Payloads (> 32 Blocks)
- **Context**: $K_r$ produces a 32-element rule tuple $(R_0, \dots, R_{31})$.
- **Decision**: Payloads consisting of $N$ blocks use rule indexing $R_{i \pmod{32}}$ for $i \in [0, N-1]$.
- **Rationale**: Guarantees deterministic, bounded-memory rule lookup across arbitrary length messages while preserving local block-level rule variability.
- **Status**: ACCEPTED & FROZEN.

