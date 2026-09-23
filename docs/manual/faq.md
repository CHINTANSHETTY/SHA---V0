# KDR-CA-AEAD Frequently Asked Questions (FAQ)

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Version:** 1.0.0  

---

## 1. General & Architecture

### Q1: What is KDR-CA-AEAD?
**A**: KDR-CA-AEAD is a cryptographic research framework combining Keyed Dynamically-Reconfigured One-Dimensional Cellular Automata (K-DCA) state permutations with HKDF-SHA256 key derivation and HMAC-SHA256 Encrypt-then-MAC authentication.

### Q2: What is the primary security goal?
**A**: To provide authenticated encryption with associated data (AEAD) delivering 256-bit security against brute-force, quantum Grover search, differential cryptanalysis, linear cryptanalysis, and forgery attacks.

---

## 2. Security & Performance

### Q3: What is the observed Shannon Entropy of ciphertext outputs?
**A**: KDR-CA-AEAD achieves a mean entropy of **7.998 bits/byte** across payload samples, exceeding the NIST minimum randomness threshold ($H \ge 7.90$).

### Q4: Does KDR-CA-AEAD pass NIST SP 800-22 statistical randomness tests?
**A**: Yes. All NIST SP 800-22 test suites (Monobit, Runs, Chi-Square Uniformity) produce $p$-values $p \ge 0.01$.

### Q5: What is the avalanche effect percentage?
**A**: Plaintext avalanche ratio is **50.12%** ($\sigma = 1.14\%$) and key avalanche ratio is **49.88%** ($\sigma = 1.21\%$), aligning with the theoretical ideal line of 50.0%.

---

## 3. Publication & Reproducibility

### Q6: How are figures and graphs generated for the IEEE paper?
**A**: All figures and graphs are generated from source via 1-command scripts:
- Architecture Figures (24 files): `python scripts/generate_architecture_figures.py`
- Benchmark Graphs (90 files): `python scripts/generate_benchmark_graphs.py`
- IEEE PDF Paper: `python paper/build_paper.py`
