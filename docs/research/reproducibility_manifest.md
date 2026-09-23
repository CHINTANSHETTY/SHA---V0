# REPRODUCIBILITY & RESEARCH PACKAGING MANIFEST

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Document Target:** `docs/research/reproducibility_manifest.md`  
**IEEE Paper Mapping:** Appendix A (*Experimental Reproducibility & Research Artifact Manifest*)  
**Status:** ✅ **FROZEN REPRODUCIBILITY MANIFEST**  

---

## 1. Environment & Runtime Specifications

| Attribute | Specification Value |
| :--- | :--- |
| **Operating System** | Microsoft Windows 11 Enterprise (64-bit, Build 22631) |
| **Python Runtime** | CPython 3.13.14 (64-bit) |
| **Virtual Environment** | `venv` (Isolated Python Virtual Environment) |
| **CPU Architecture** | AMD64 Family 25 Model 80 Stepping 0 (AuthenticAMD) |
| **Cryptographic Library** | `cryptography` v50.0.0 (OpenSSL 3.x backend) |

---

## 2. Deterministic Seeds & Test Parameters

- **Validation Trial Count ($N$)**: $10,000$ randomized bit-flip trials
- **Pseudo-Random Generator Seed**: `random.Random(2026)` (Deterministic reproducible seed)
- **Candidate Study Seed**: `random.Random(42)`
- **Default Rule Offset ($\Delta$)**: `13` (Coprime to table length $M = 32$)
- **Default Feedback State IV**: `0xC5`
- **Protocol Identifier**: `KDR-CA-AEAD-v1`

---

## 3. Automated Command Execution Matrix

To reproduce all experimental results and tables reported in the IEEE manuscript, execute the following commands in order:

### 1. Run Complete Unit Test Suite (39 Tests):
```bash
.\venv\Scripts\python.exe -m unittest discover -s tests
```

### 2. Run Candidate Algorithm & Parameter Study (Phase 2.1A):
```bash
.\venv\Scripts\python.exe benchmarks/candidate_study.py
```

### 3. Run Scientific Cryptographic Validation Battery ($N = 10,000$ Trials & NIST Tests):
```bash
.\venv\Scripts\python.exe benchmarks/cryptographic_validation.py
```

### 4. Run Comparative Cipher Performance Benchmarks:
```bash
.\venv\Scripts\python.exe benchmarks/comparative_benchmark.py
```

---

## 4. Repository Artifact Checklist

- [x] `crypto/primitives/hkdf.py` (RFC 5869 HKDF Engine)
- [x] `crypto/engine/key_schedule.py` (Domain-separated Key Schedule)
- [x] `crypto/engine/dynamic_ca.py` (Candidate A-Chain Dynamic CA Engine)
- [x] `crypto/engine/encrypt.py` (High-Level AEAD Encryptor)
- [x] `crypto/engine/decrypt.py` (High-Level AEAD Decryptor & Authenticator)
- [x] `docs/research/threat_model.md` (Threat Model Specification)
- [x] `docs/research/limitations_and_discussion.md` (Limitations & Empirical Discussion)
- [x] `docs/research/algorithm_evolution_log.md` (Algorithm Evolution History Log)
- [x] `docs/research/reproducibility_manifest.md` (Reproducibility Manifest)
