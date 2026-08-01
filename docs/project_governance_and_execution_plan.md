# Project Governance & Execution Plan: KDR-CA-AEAD

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Role:** Lead Software Engineer & Cryptography Systems Architect  
**Primary Output Artifact:** `project_governance_and_execution_plan.md`  

---

## 1. Refined Directory Architecture

To separate **standard cryptographic primitives** from the **novel research contribution**, the project layout is updated as follows:

```text
SHA/
├── crypto/
│   ├── primitives/           # Standard Cryptographic Building Blocks
│   │   ├── __init__.py
│   │   ├── hkdf.py           # HKDF-SHA256 (RFC 5869 / NIST SP 800-56C)
│   │   ├── hmac.py           # Constant-Time HMAC-SHA256 Tag Verification
│   │   └── random.py         # Cryptographically Secure PRNG (CSPRNG via secrets)
│   ├── engine/               # Novel IEEE Research Contribution Engine
│   │   ├── __init__.py
│   │   ├── key_schedule.py   # Dynamic Sub-Key Expansion & Rule Table Generation
│   │   ├── dynamic_ca.py     # Keyed Dynamic Cellular Automata Local State Engine
│   │   ├── encrypt.py        # High-Level KDR-CA-AEAD Encryptor
│   │   └── decrypt.py        # High-Level KDR-CA-AEAD Decryptor & Verification
│   ├── models/               # Data Transfer & Exceptions
│   │   ├── __init__.py
│   │   ├── package.py        # Encrypted Payload Dataclass & Serializer
│   │   └── exceptions.py     # Crypto Error Hierarchy
│   └── utils/
│       ├── __init__.py
│       └── byte_ops.py       # Fast Byte Array Transformations
├── database/
│   ├── __init__.py
│   ├── db_manager.py         # SQLite Persistence & Argon2id Password Hashing
│   └── models.py             # Database Models
├── web/
│   ├── __init__.py
│   ├── app.py                # Flask Web Controller
│   ├── static/
│   └── templates/
├── tests/
│   ├── unit/
│   │   ├── test_hkdf.py
│   │   ├── test_hmac.py
│   │   ├── test_key_schedule.py
│   │   ├── test_dynamic_ca.py
│   │   ├── test_encrypt_decrypt.py
│   │   └── test_database.py
│   └── integration/
│       └── test_web_flow.py
├── benchmarks/
│   ├── avalanche_test.py     # SAC & BIC Heatmaps
│   ├── nist_sp800_22.py      # NIST SP 800-22 Randomness Battery
│   └── performance.py        # Throughput (MB/s) vs AES-GCM
├── requirements.txt
└── .gitignore
```

---

## 2. Coding Standards & Governance Rules

- **Language / Environment**: Python 3.10+
- **Style & Docstrings**: Google Python Docstring Style
- **Type Checking**: Strict type hinting (`mypy`)
- **Formatting**: `black` & `isort`
- **Linting**: `ruff` / `flake8`
- **Testing**: `pytest` with code coverage report

---

## 3. Git Commit Conventions

All commits follow the Conventional Commits standard:
- `feat(crypto)`: New cryptographic feature or module implementation.
- `test(crypto)`: Unit test suite or RFC test vector additions.
- `refactor(database)`: Code cleanup or migration (e.g. Argon2id).
- `fix(auth)`: Security patch or timing leak fix.
- `docs(paper)`: IEEE manuscript or design specification updates.

---

## 4. Module Task Tracker & Execution Status

| Task ID | Component Module | File Path | Status | Target Outcome |
| :-: | :--- | :--- | :-: | :--- |
| **C-01** | HKDF Primitive | `crypto/primitives/hkdf.py` | 🟡 **IN PROGRESS** | Pass RFC 5869 test vectors |
| **C-02** | HMAC Primitive | `crypto/primitives/hmac.py` | ⚪ Todo | Constant-time tag check |
| **C-03** | CSPRNG Primitive | `crypto/primitives/random.py` | ⚪ Todo | Secure Salt/Nonce generator |
| **C-04** | Data Models | `crypto/models/package.py` | ⚪ Todo | Dataclass payload serialization |
| **C-05** | Exceptions | `crypto/models/exceptions.py` | ⚪ Todo | Custom Crypto error hierarchy |
| **C-06** | Key Schedule Engine | `crypto/engine/key_schedule.py` | ⚪ Todo | Sub-key & Rule derivation |
| **C-07** | Dynamic CA Engine | `crypto/engine/dynamic_ca.py` | ⚪ Todo | Keyed CA forward/inverse |
| **C-08** | AEAD Encrypt/Decrypt | `crypto/engine/encrypt.py` & `decrypt.py` | ⚪ Todo | Full AEAD pipeline |
| **D-01** | Database Hardening | `database/db_manager.py` | ⚪ Todo | Argon2id & Encrypted SQLite |
| **W-01** | Flask Integration | `web/app.py` | ⚪ Todo | Web controller update |
| **T-01** | Test Suite | `tests/unit/` | ⚪ Todo | 90%+ pytest code coverage |
| **B-01** | IEEE Benchmarks | `benchmarks/` | ⚪ Todo | SAC, NIST SP 800-22 & Throughput |

---

## 5. Global Definition of Done (DoD)

A task is officially **DONE** when:
1. Core functional code implemented cleanly.
2. 100% Type hints (`mypy`) & Google docstrings present.
3. Unit test coverage passes (`pytest`).
4. Security audit checklist verified (no hardcoded keys, constant-time operations).
5. Mapped directly to IEEE paper section.
