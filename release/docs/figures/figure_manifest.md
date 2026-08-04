# Figure Manifest - KDR-CA-AEAD Architecture & Publication Graphics

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Task:** Ashwitha – Phase 3.2.2 (Architecture Figures & Publication Graphics)  
**IEEE Target:** IEEE Transactions on Information Forensics and Security  
**Total Figures:** 8 Publication-Ready Architecture Figures (24 files in SVG, PDF, PNG 300 DPI formats)  

---

> [!IMPORTANT]
> **Primary Source Notice**: Scalable Vector Graphics (`.svg`) files are the primary, authoritative editable sources. All vector PDF (`.pdf`) and 300 DPI PNG (`.png`) files are compiled programmatically via `scripts/generate_architecture_figures.py`. Manual edits should never be made directly to exported PDF/PNG files.

---

## Complete Figure Number & IEEE Label Mapping

| Fig # | Figure Identifier | IEEE TeX Label | IEEE Paper Section | Formats Available | Primary Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fig. 1** | `system_architecture` | `\label{fig:system_arch}` | Section IV-A (`architecture.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `system_architecture.svg` |
| **Fig. 2** | `encryption_workflow` | `\label{fig:encryption_flow}` | Section IV-B (`architecture.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `encryption_workflow.svg` |
| **Fig. 3** | `decryption_workflow` | `\label{fig:decryption_flow}` | Section IV-C (`architecture.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `decryption_workflow.svg` |
| **Fig. 4** | `dynamic_ca_engine` | `\label{fig:dynamic_ca_engine}` | Section IV-D (`architecture.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `dynamic_ca_engine.svg` |
| **Fig. 5** | `key_schedule` | `\label{fig:key_schedule}` | Section IV-D (`architecture.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `key_schedule.svg` |
| **Fig. 6** | `authenticated_encryption_pipeline` | `\label{fig:auth_enc_pipeline}` | Section IV-D (`architecture.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `authenticated_encryption_pipeline.svg` |
| **Fig. 7** | `security_validation_flow` | `\label{fig:sec_val_flow}` | Section V-A (`security_analysis.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `security_validation_flow.svg` |
| **Fig. 8** | `benchmark_pipeline` | `\label{fig:bm_pipeline}` | Section VI-A (`benchmarks.tex`) | `.svg`, `.pdf`, `.png` (300 DPI) | `benchmark_pipeline.svg` |

---

## Publication & Accessibility Standards Compliance

1. **Font Consistency**: Standardized sans-serif font hierarchy (`DejaVu Sans`, `Arial`, `Helvetica`).
2. **Stroke Width & Arrows**: Uniform border stroke width (`1.2pt`) and consistent arrow markers (`arrowstyle="->"`).
3. **Grayscale Legibility**: Contrast fills (`#E2E8F0`, `#FEF3C7`, `#DCFCE7`, `#E0F2FE`, `#F3E8FF`, `#FFEDD5`, `#DBEAFE`) paired with thick slate borders (`#475569`) guarantee readability in monochrome/grayscale print.
4. **Resolution Verification**: All PNG exports verified at 300 DPI (2385 px width for single/double-column IEEE layouts).

---

## Source Reproducibility Command

To regenerate the entire figure suite programmatically:

```powershell
$env:PYTHONPATH="."
python scripts/generate_architecture_figures.py
```
