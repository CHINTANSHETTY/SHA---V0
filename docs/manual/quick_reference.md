# KDR-CA-AEAD Quick Reference Guide

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Version:** 1.0.0  

---

## 1. Frequently Used Commands

| Command Purpose | Execution Command |
| :--- | :--- |
| **Set Environment Variable** | `$env:PYTHONPATH="."` |
| **Run Pytest Suite** | `python -m pytest` |
| **Run Integration Tests** | `python -m pytest tests/integration/test_phase2_5_integration.py` |
| **Run Security Suite** | `python -c "from crypto.analysis.final_validation import run_full_security_analysis; run_full_security_analysis()"` |
| **Generate Architecture Figures** | `python scripts/generate_architecture_figures.py` |
| **Generate Benchmark Graphs** | `python scripts/generate_benchmark_graphs.py` |
| **Build API Documentation** | `python docs/api/build_api_docs.py` |
| **Build User Manual** | `python docs/manual/build_manual.py` |
| **Build IEEE PDF Manuscript** | `python paper/build_paper.py` |

---

## 2. Directory Artifact Map

| Artifact Category | File Location |
| :--- | :--- |
| **IEEE LaTeX Manuscript** | `paper/ieee_paper.tex`, `paper/final.pdf` |
| **Architecture Figures** | `docs/figures/*.svg`, `*.pdf`, `*.png` |
| **Benchmark Graphs** | `docs/graphs/*.svg`, `*.pdf`, `*.png`, `benchmark_statistical_summary.csv` |
| **API Reference Docs** | `docs/api/html/index.html`, `docs/api/pdf/kdr_ca_aead_developer_reference.pdf`, `docs/api/coverage_report.json` |
| **User Manual Docs** | `docs/manual/user_manual.html`, `docs/manual/user_manual.pdf`, `docs/manual/manual_validation_report.json` |
