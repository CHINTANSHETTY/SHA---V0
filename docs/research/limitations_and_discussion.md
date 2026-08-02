# RESEARCH LIMITATIONS, EMPIRICAL DISCUSSION & FUTURE DIRECTIONS

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Document Target:** `docs/research/limitations_and_discussion.md`  
**IEEE Paper Mapping:** Section VI (*Discussion, Limitations & Future Work*)  
**Status:** ✅ **FROZEN RESEARCH SPECIFICATION**  

---

## 1. Executive Summary

This document provides a transparent, scientifically rigorous discussion of the empirical findings, mathematical observations, and identified research limitations of the KDR-CA-AEAD cipher framework.

Acknowledging research limitations and performance trade-offs is essential for IEEE-grade peer review and ensures that paper claims remain strictly proportional to empirical evidence.

---

## 2. Empirical Discussion of Results

### 2.1 Analysis of Strict Avalanche Criterion (SAC = 0.2472)
- **Empirical Measurement**: Mean SAC $\mu = 0.2472$ (95% CI $[0.2444, 0.2501]$) across $N = 10,000$ randomized trials.
- **Scientific Discussion**:
  * The theoretical ideal value for Strict Avalanche Criterion is $\text{SAC}_{\text{ideal}} = 0.5000$.
  * Candidate A-Chain achieves over $>170\times$ higher bit flip propagation than local non-chained S-box candidates ($\mu = 0.0012$), demonstrating successful inter-byte state feedback.
  * However, $\mu = 0.2472$ remains below the theoretical ideal of $0.5000$. This indicates that while the single-pass 1D ECA transformation diffuses bit flips downstream, a single forward pass does not achieve complete bit independence across all output positions.

### 2.2 Analysis of Shannon Entropy Profiles across Datasets
- **Empirical Measurement**:
  * English Medical Text Payload: $6.40$ bits/byte (Raw input: $4.81$ bits/B).
  * Structured JSON Payload: $5.79$ bits/byte (Raw input: $4.24$ bits/B).
  * All-Zero Stream (1,024 Bytes): **$7.80$ bits/byte** (Raw input: $0.00$ bits/B).
- **Scientific Discussion**:
  * For long zero streams, the output stream reflects the pure pseudo-random distribution of the HMAC-SHA256 CTR-PRNG keystream coupled with dynamic CA substitution, approaching the theoretical maximum of $8.0000$ bits/byte.
  * For short structured text payloads (e.g., 60–120 bytes), the symbol frequency distribution retains slight non-uniformity due to payload length bounds.

### 2.3 Performance & Execution Runtime Profiling
- **Empirical Measurement**:
  * KDR-CA-AEAD (Pure Python Reference Implementation): $\approx 0.17$ MB/s throughput, $443\ \mu\text{s}$ latency (64B).
  * AES-256-GCM (Hardware AES-NI C): $\approx 992$ MB/s throughput, $2.56\ \mu\text{s}$ latency (64B).
  * ChaCha20-Poly1305 (Software C): $\approx 797$ MB/s throughput, $2.72\ \mu\text{s}$ latency (64B).
- **Scientific Discussion**:
  * The benchmark baseline comparison evaluates a 100% pure CPython reference implementation against native C/assembly ciphers utilizing dedicated hardware instructions (Intel AES-NI).
  * High-level byte loops in Python introduce interpreter bytecode dispatch overhead per byte. A native C/Cython compilation of the inner ECA loop will eliminate interpreter overhead and achieve standard native throughput ($>100$ MB/s).

---

## 3. Explicit Research Limitations

To maintain academic integrity, the following limitations are explicitly recognized:

1. **Prototype Implementation**: The current codebase is a pure Python reference implementation designed for functional correctness and empirical security analysis, not production execution speed.
2. **Avalanche Propagation Gap**: Mean SAC ($\mu = 0.2472$) remains below the theoretical optimum ($0.5000$).
3. **Evaluated NIST Randomness Scope**: Validation evaluated a 3-test subset of NIST SP 800-22 (Frequency Monobit, Block Frequency, Runs). The full 15-test battery will be executed in dedicated C-based test suites.
4. **Lack of Hardware Acceleration**: No dedicated SIMD or AES-NI style hardware instruction set exists for dynamic elementary cellular automata transitions.

---

## 4. Future Research Directions

1. **Multi-Round CA State Evolution**: Investigating 2-round and 4-round dynamic cellular automata iterations to elevate SAC toward $0.5000$.
2. **Native C / Cython Extension Module**: Developing a compiled C extension module (`_dynamic_ca_fast.c`) to achieve multi-gigabit throughput.
3. **Full NIST SP 800-22 Battery**: Running the complete 15-test NIST SP 800-22 randomness suite on multi-gigabyte ciphertext streams.
