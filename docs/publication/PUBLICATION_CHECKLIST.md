# Publication Completion & Pre-Submission Checklist

This document provides a comprehensive verification checklist for submitting the **KDR-CA-AEAD** manuscript (*Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption*) to high-impact academic journals and conferences (e.g., IEEE Transactions on Information Forensics and Security, IEEE TDSC, or ACM CCS).

---

## 1. Manuscript Completion Checklist
- [ ] Title accurately reflects the paper's focus: *Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)*.
- [ ] All author names, affiliations, email addresses, and ORCIDs are accurate and up to date.
- [ ] Corresponding author contact information is clearly indicated.
- [ ] Document adheres to the specific journal/conference page limits (e.g., 10-14 double-column pages).

## 2. Abstract Verification
- [ ] Concise summary (150–250 words) outlining problem statement, proposed solution, methodology, key findings, and performance/security benchmarks.
- [ ] No citations, acronyms without expansion, or non-standard notation in the abstract.
- [ ] Clearly states empirical Strict Avalanche Criterion (SAC = 50.12%) and comparative performance vs. AES-GCM.

## 3. Keywords Review
- [ ] 5–8 domain-specific IEEE/ACM indexed keywords included:
  - *Cellular Automata*, *Authenticated Encryption (AEAD)*, *Dynamic Reconfiguration*, *HKDF Key Expansion*, *Encrypt-then-MAC (EtM)*, *Lightweight Cryptography*, *Strict Avalanche Criterion*.

## 4. Figures and Captions
- [ ] All figures high-resolution (300 DPI PNG or vector SVG format).
- [ ] Every figure explicitly referenced in the main text in sequential order (Figure 1, Figure 2, ...).
- [ ] Figure captions self-contained and descriptive.
- [ ] Color schemes accessible and legible in monochrome/grayscale prints.

## 5. Table Formatting
- [ ] All tables use standard formal styles (e.g., booktabs without vertical borders).
- [ ] Columns and rows clearly labeled with physical units and performance metrics (e.g., throughput in MB/s, latency in $\mu$s).
- [ ] Every table explicitly cited and discussed in text.

## 6. Algorithm Formatting
- [ ] Pseudocode for K-DCA dynamic rule expansion, encryption, decryption, and HMAC tag computation rendered using standard algorithm environments (`algorithm2e` or `algorithmicx`).
- [ ] Inputs, outputs, time complexity, and memory bounds explicitly specified.

## 7. Equation Numbering
- [ ] All mathematical equations sequentially numbered throughout document.
- [ ] Symbols clearly defined upon first appearance ($K_r$, $K_c$, $K_a$, $S_{salt}$, $N_{nonce}$).
- [ ] Standard mathematical formatting (bold vectors, uppercase matrices, italic variables).

## 8. Reference Verification
- [ ] References formatted strictly according to publisher style (e.g., IEEE style `[1]`, `[2]`).
- [ ] DOIs included for all referenced papers.
- [ ] Modern literature coverage (includes foundational CA papers, NIST AEAD standards RFC 5869 / NIST SP 800-56C, and recent cryptographic benchmarks).

## 9. Grammar & Tone Review
- [ ] Passive voice used appropriately for scientific reporting.
- [ ] Checked using automated tools (Grammarly / LanguageTool) and peer proofread.
- [ ] Consistent cryptographic terminology throughout.

## 10. Plagiarism & Integrity Check
- [ ] Similarity index verified below publisher threshold (< 10% overall, < 1% single source via iThenticate / Turnitin).
- [ ] All reused figures, tables, or standard algorithms properly cited with permission acknowledged if necessary.

## 11. Supplementary Material Checklist
- [ ] Complete proof of security bounds included in Appendix / Supplementary document.
- [ ] Extended experimental test vectors included.
- [ ] Source code link or anonymous repository link provided for double-blind peer review.

## 12. Artifact Evaluation Checklist
- [ ] Open-source repository packaged cleanly with clear `LICENSE` (Apache 2.0).
- [ ] Master reproducibility script (`run_phase2_5_reproducibility.py` / `EXECUTION_GUIDE.md`) functional.
- [ ] Docker / environment setup file (`requirements.txt`, Dockerfile) validated.

## 13. Reproducibility Verification
- [ ] Benchmark scripts output identical CSV reports (`reports/` / `metrics/`).
- [ ] All 465+ automated unit and integration tests passing (`pytest tests/`).

## 14. Final PDF Generation Checklist
- [ ] Fonts 100% embedded (verified via `pdffonts`).
- [ ] IEEE PDF eXpress check passed without compliance errors or warnings.
- [ ] File size optimized under submission threshold (typically < 10 MB).
