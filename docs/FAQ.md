# Frequently Asked Questions (FAQ)

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Document Version:** 1.0.0  

---

## 1. Installation & Environment

### Q1.1: Which Python versions are supported?
KDR-CA-AEAD is supported and tested on Python 3.10, 3.11, 3.12, and 3.13 on Windows, Linux, and macOS.

### Q1.2: Does KDR-CA-AEAD require C compilers or native C extensions?
No. Core encryption (`crypto/`, `encrypt.py`, `decrypt.py`) is written in pure Python using the Standard Library (`hashlib`, `hmac`, `secrets`, `os`).

---

## 2. Security & Threat Model

### Q2.1: What security model does KDR-CA-AEAD provide?
KDR-CA-AEAD provides Authenticated Encryption with Associated Data (AEAD), guaranteeing IND-CCA2 confidentiality and INT-CTXT integrity via constant-time Encrypt-then-MAC (EtM).

### Q2.2: How are side-channel timing attacks mitigated?
Authentication tag verification uses `hmac.compare_digest`, ensuring constant-time comparison regardless of tag mismatches.

### Q2.3: How should security vulnerabilities be disclosed?
Security flaws should be reported privately to `shettyashwitha26@gmail.com` or `chntnshetty@gmail.com` per our private disclosure policy in `SECURITY.md`.

---

## 3. Performance & Benchmarking

### Q3.1: What is the throughput of KDR-CA-AEAD?
Un-optimized pure Python execution achieves 12.66 MB/s throughput for 100KB payloads.

### Q3.2: How do I run performance benchmarks?
Run `python examples/benchmark_demo.py` or execute `python scripts/run_phase2_5_reproducibility.py`.

---

## 4. Academic Citation & Licensing

### Q4.1: What license governs KDR-CA-AEAD?
KDR-CA-AEAD is released under the OSI-approved Apache License 2.0 (`LICENSE`).

### Q4.2: How should I cite KDR-CA-AEAD in academic papers?
Refer to `docs/research/CITATION_GUIDE.md` for BibTeX, IEEE, ACM, and APA citation formats.
