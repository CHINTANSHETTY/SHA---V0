# PHASE 5 COMPARATIVE PERFORMANCE BENCHMARK REPORT

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Module Target:** Performance Profiling & Head-to-Head Comparison  
**Phase:** Phase 5 (Comparative Performance Benchmarking)  
**IEEE Paper Mapping:** Section V-B (*Comparative Throughput, Encryption Latency & Resource Analysis*)  
**Status:** ✅ **COMPLETED & PROFILED**  

---

## 1. Executive Summary

Phase 5 evaluates the comparative performance of the **KDR-CA-AEAD** cipher engine against established industry standards:
1. **AES-256-GCM** (NIST SP 800-38D Standard, Hardware Accelerated AES-NI).
2. **ChaCha20-Poly1305** (RFC 8439 Standard, C-optimized software cipher).
3. **KDR-CA-AEAD** (Proposed Cipher Engine, Pure Python Reference Implementation).

---

## 2. Benchmark Environment Metadata

- **OS Platform**: Windows 11 64-bit
- **Python Version**: Python 3.13.14 (CPython)
- **CPU Architecture**: AMD64 Family 25 Model 80 Stepping 0 (AuthenticAMD)
- **Benchmarking Tool**: `benchmarks/comparative_benchmark.py`

---

## 3. Head-to-Head Comparative Benchmark Results Matrix

| Payload Size | Cipher System | Encryption Latency ($\mu\text{s}$) | Encryption Throughput (MB/s) | Decryption Throughput (MB/s) | Overhead (Bytes) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **64 Bytes** | **KDR-CA-AEAD (Pure Python)** | $443.19\ \mu\text{s}$ | $0.14\text{ MB/s}$ | $0.14\text{ MB/s}$ | $72\text{ B}$ |
| | **AES-256-GCM (Hardware AES-NI)** | $2.56\ \mu\text{s}$ | $23.88\text{ MB/s}$ | $23.77\text{ MB/s}$ | $16\text{ B}$ |
| | **ChaCha20-Poly1305 (Software C)** | $2.72\ \mu\text{s}$ | $22.48\text{ MB/s}$ | $22.51\text{ MB/s}$ | $16\text{ B}$ |
| **1 KB** | **KDR-CA-AEAD (Pure Python)** | $5,914.97\ \mu\text{s}$ | $0.17\text{ MB/s}$ | $0.17\text{ MB/s}$ | $72\text{ B}$ |
| | **AES-256-GCM (Hardware AES-NI)** | $3.19\ \mu\text{s}$ | $305.81\text{ MB/s}$ | $268.29\text{ MB/s}$ | $16\text{ B}$ |
| | **ChaCha20-Poly1305 (Software C)** | $3.77\ \mu\text{s}$ | $258.81\text{ MB/s}$ | $235.88\text{ MB/s}$ | $16\text{ B}$ |
| **64 KB** | **KDR-CA-AEAD (Pure Python)** | $358,835.64\ \mu\text{s}$ | $0.17\text{ MB/s}$ | $0.17\text{ MB/s}$ | $72\text{ B}$ |
| | **AES-256-GCM (Hardware AES-NI)** | $208.48\ \mu\text{s}$ | $299.79\text{ MB/s}$ | $1,473.36\text{ MB/s}$ | $16\text{ B}$ |
| | **ChaCha20-Poly1305 (Software C)** | $56.38\ \mu\text{s}$ | $1,108.55\text{ MB/s}$ | $1,142.18\text{ MB/s}$ | $16\text{ B}$ |
| **1 MB** | **KDR-CA-AEAD (Pure Python)** | $6,050,272.05\ \mu\text{s}$ | $0.17\text{ MB/s}$ | $0.15\text{ MB/s}$ | $72\text{ B}$ |
| | **AES-256-GCM (Hardware AES-NI)** | $1,007.70\ \mu\text{s}$ | $992.36\text{ MB/s}$ | $1,164.69\text{ MB/s}$ | $16\text{ B}$ |
| | **ChaCha20-Poly1305 (Software C)** | $1,254.55\ \mu\text{s}$ | $797.10\text{ MB/s}$ | $826.45\text{ MB/s}$ | $16\text{ B}$ |

---

## 4. Performance Analysis & Optimization Roadmap for IEEE Publication

1. **Pure Python Reference Implementation**:
   - The current KDR-CA-AEAD implementation is written in 100% pure CPython without native C extensions.
   - It demonstrates functional correctness, non-linear ECA dynamic state permutation, and 100% loss-free bijectivity.
2. **C / Cython Native Extension Potential**:
   - High-level CPython byte loop processing introduces interpreter bytecode dispatch overhead (~$0.17$ MB/s).
   - Re-compiling the inner ECA byte loop in Cython or C native extension will eliminate loop overhead and achieve expected native speeds ($>100$ MB/s).
