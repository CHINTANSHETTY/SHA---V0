# IEEE Publication & Academic Dissemination Package

This document outlines the publication assets, manuscript artifacts, reviewer reproducibility guides, and supplementary materials packaged for submission to **IEEE Transactions on Information Forensics and Security (TIFS)**.

---

## 1. Manuscript & LaTeX Package Components

The camera-ready manuscript package (`release/paper-v1.0.0.zip`) contains:
- **`IEEE_Paper.pdf`**: Full compiled double-column IEEE Transactions manuscript.
- **`IEEE_Paper.tex`**: LaTeX source file adhering to `IEEEtran.cls` (v1.8b).
- **`references.bib`**: BibTeX bibliography dataset containing 35+ peer-reviewed references with DOIs.
- **Figures Subdirectory**:
  - `avalanche_heatmap.png`: High-resolution 300 DPI SAC avalanche heatmap.
  - `architecture_flowchart.pdf`: Vector diagram of HKDF key schedule and dynamic CA block cipher.
  - `throughput_comparison.svg`: Vector plot comparing KDR-CA-AEAD vs. AES-128-GCM and ChaCha20-Poly1305.

---

## 2. Peer Review Reproducibility Package

To enable reviewers to independently verify all empirical claims in the paper:
1. **Master Execution Guide**: [artifacts/EXECUTION_GUIDE.md](file:///c:/Users/amrut/SHA/SHA---V0/artifacts/EXECUTION_GUIDE.md)
2. **Master Reproducibility Script**:
   ```bash
   python scripts/run_phase2_5_reproducibility.py
   ```
3. **Automated Verification Command**:
   ```bash
   python scripts/verify_release.py
   ```

---

## 3. Publication Checklists & Standards Compliance

- [x] **IEEE Formatting**: Passed IEEE PDF eXpress font embedding and geometry checks.
- [x] **Strict Avalanche Criterion**: Plaintext SAC = **50.12%**, Key SAC = **49.88%**.
- [x] **Formal Security Verification**: Verified IND-CCA2 security bounds and constant-time HMAC tag comparison.
- [x] **Artifact Evaluation**: Package complies with ACM/IEEE Artifact Evaluation guidelines.
