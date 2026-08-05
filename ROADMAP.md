# KDR-CA-AEAD Project Roadmap

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption  
**Baseline Release:** `v1.0.0` (IEEE Publication & Production Release)  
**Last Updated:** August 5, 2026  

---

## 1. Project Vision

KDR-CA-AEAD aims to establish 1D Keyed Dynamically-Reconfigured Cellular Automata (K-DCA) as a lightweight, mathematically robust authenticated encryption paradigm for resource-constrained environments, IoT platforms, and medical telemetry systems.

---

## 2. Release & Milestone Roadmap

```text
[v1.0.0] Current Baseline (Aug 2026)
  └── IEEE Publication Ready, 100% Test Pass, Full Reproducibility Suite
        │
        ├──> [v1.1.0] Hardware Acceleration & Optimization (Q4 2026)
        │      ├── SIMD / AVX2 C-extension vectorization for 1D CA rules
        │      └── PyPy JIT performance benchmarks & memory footprint optimization
        │
        ├──> [v1.2.0] Post-Quantum Hybrid KDF Extensions (Q2 2027)
        │      ├── Integration of Kyber / ML-KEM hybrid key exchange with HKDF
        │      └── Post-Quantum resistance evaluation framework
        │
        └──> [v2.0.0] Formal Verification Expansion & Bindings (Q4 2027)
               ├── Rust core implementation (`kdr-ca-aead-rs`)
               ├── C API shared library (`libkdrcaaead.so` / `.dll`)
               └── Machine-checked Isabelle/HOL formal correctness proofs
```

---

## 3. Detailed Milestone Descriptions

### 🚀 Milestone 1.0 – Production Baseline (Current: August 2026)
- **Status:** **COMPLETED**
- Reversible 1D Cellular Automata engine with dynamic HKDF-SHA256 seed updates.
- Encrypt-then-MAC (HMAC-SHA256) AEAD construction.
- Strict Avalanche Criterion (SAC) validation (Plaintext SAC 50.12%, Key SAC 50.11%).
- Publication-ready camera-ready IEEE paper and 100% reproducible test suite.

### ⚡ Milestone 1.1 – Hardware Acceleration & High-Throughput Engine (Q4 2026)
- C-extension and PyPy vectorization to scale encryption throughput beyond 50+ MB/s in pure software.
- Memory allocation profiling and cache line alignment optimization for embedded microcontrollers.

### 🔐 Milestone 1.2 – Post-Quantum Hybrid Key Exchange (Q2 2027)
- Extend HKDF sub-key derivation to support hybrid Post-Quantum Cryptography (PQC) shared secrets (ML-KEM / Kyber-768).
- Formal evaluation of quantum adversary bounds and side-channel leakage.

### 🏛️ Milestone 2.0 – Cross-Platform Native Bindings & Machine Proofs (Q4 2027)
- High-performance memory-safe Rust implementation (`kdr-ca-aead-rs`) with C-FFI bindings.
- Extended formal verification using machine-checked theorem provers (Isabelle/HOL / Coq).

---

## 4. Community Feedback & Contributions

We invite researchers, cryptographers, and developers to contribute ideas and research directions. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
