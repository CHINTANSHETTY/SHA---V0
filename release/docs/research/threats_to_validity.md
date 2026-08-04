# THREATS TO VALIDITY SPECIFICATION

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Document Target:** `docs/research/threats_to_validity.md`  
**IEEE Paper Mapping:** Section VI-B (*Threats to Validity*)  
**Status:** ✅ **FROZEN RESEARCH SPECIFICATION**  

---

## 1. Executive Summary

This document categorizes potential threats to validity concerning the experimental methodology, empirical measurements, and research conclusions of the KDR-CA-AEAD project. Addressing threats to validity ensures scientific rigor and prepares the paper for peer review.

---

## 2. Taxonomy of Threats to Validity

### 2.1 Internal Validity (Experimental Design & Measurement Noise)
- **Threat**: Software bugs or indexing errors in benchmark measurement scripts (`benchmarks/candidate_study.py`, `benchmarks/cryptographic_validation.py`) could skew empirical results (SAC, NPCR, UACI).
- **Mitigation**:
  * All benchmark utility functions (`count_bit_flips`, `calculate_shannon_entropy`, `calculate_npcr_uaci`) were verified independently against 39 unit tests in `tests/unit/`.
  * Deterministic random seeds (`Random(2026)`, `Random(42)`) ensure zero variance across experimental runs.

### 2.2 External Validity (Generalizability & Performance Environment)
- **Threat**: Empirical throughput metrics ($0.17$ MB/s) measured in pure CPython on Windows 11 may not generalize to optimized C/C++ or hardware-accelerated embedded platforms.
- **Mitigation**:
  * Comparative performance benchmarks explicitly state that KDR-CA-AEAD is evaluated as a pure Python reference implementation against hardware-accelerated AES-NI ($992$ MB/s) and ChaCha20-Poly1305 ($797$ MB/s).
  * Future compilation of the inner ECA byte loop in native C/Cython will eliminate interpreter bytecode dispatch overhead.

### 2.3 Construct Validity (Security Metrics vs. Formal Cryptanalysis)
- **Threat**: Passing an evaluated 3-test subset of NIST SP 800-22 or measuring SAC ($\mu = 0.2472$) does not constitute a formal mathematical proof of security against all possible cryptanalytic attacks.
- **Mitigation**:
  * Statistical randomness and avalanche testing are presented as necessary empirical indicators of non-linearity and state confusion, not as absolute security proofs.
  * Formal provable security reductions (IND-CCA2 under HMAC-SHA256 PRF assumption) are treated separately in Section III.

### 2.4 Conclusion Validity (Statistical Confidence & Sample Size Bounds)
- **Threat**: Small sample sizes ($N < 100$) could introduce sampling error, leading to incorrect statistical conclusions.
- **Mitigation**:
  * The sample size was expanded to **$N = 10,000$ randomized trials**, and results are reported with **95% Confidence Intervals** ($\mu \pm 1.96 \frac{\sigma}{\sqrt{N}}$) to ensure statistical significance.
