# KDR-CA-AEAD Community & Project Roadmap

This document outlines planned feature additions, performance optimizations, hardware acceleration goals, and release milestones for future versions of **KDR-CA-AEAD**.

---

## Strategic Goals & Version Milestones

```text
  [v1.0.0 Current Release]
   ├── Python 3.10+ Reference AEAD Engine
   ├── Automated 465+ Pytest Verification Suite
   ├── Master Reproducibility Script & IEEE Artifact Package
   └── Web GUI Application (app.py)

            │
            ▼

  [v1.1.0 Short-Term Milestone - Q4 2025]
   ├── C/C++ Cython / CFFI Performance Extensions
   ├── Hardware-Accelerated Bitwise Assembly Primitives
   ├── NIST SP 800-22 Statistical Test Suite Auto-Runner
   └── Expanded CLI Utilities & Multi-File Package Formatting

            │
            ▼

  [v2.0.0 Long-Term Vision - Q2 2026]
   ├── Open-Source SystemVerilog / VHDL RTL Cores for FPGA & ASIC
   ├── GPU Acceleration (CUDA / OpenCL) for Parallel Batch Processing
   ├── Post-Quantum Hybrid Key Exchange Integration (ML-KEM / Kyber)
   └── 2D/3D Cellular Automata Permutation Extensions
```

---

## Detailed Milestone Objectives

### Version 1.1 Goals (Short-Term)
- **Cython Speedups**: Port core cellular automata state transitions from pure Python to Cython/C extensions to boost throughput past 800 MB/s.
- **Enhanced CLI Tooling**: Add batch directory encryption, key file generation, and interactive shell commands.
- **NIST Randomness Runner**: Integrated execution of NIST SP 800-22 statistical test suite.

### Version 2.0 Vision (Long-Term)
- **Hardware RTL Release**: Open-source Verilog/SystemVerilog modules targeting Xilinx Artix-7 / UltraScale+ FPGAs and 45nm ASIC synthesis.
- **GPU Acceleration**: OpenCL and CUDA implementations for high-throughput batch encryption in cloud infrastructure.
- **Post-Quantum Key Exchange**: Hybrid key schedule integrating NIST PQC standards (ML-KEM / Kyber-768) with HKDF master derivation.
