# Long-Term Reproducibility Checklist — KDR-CA-AEAD v1.0.0

| Reproducibility Checkpoint | Verification Command | Status |
| :--- | :--- | :--- |
| **Full Pytest Regression Suite** | `python -m pytest` | ✅ Passed (251/251 Tests) |
| **Architecture Figures Rebuild** | `python scripts/generate_architecture_figures.py` | ✅ Verified Deterministic |
| **Benchmark Graphs Rebuild** | `python scripts/generate_benchmark_graphs.py` | ✅ Verified Deterministic |
| **API Reference Docs Rebuild** | `python docs/api/build_api_docs.py` | ✅ Verified Deterministic |
| **User Manual Rebuild** | `python docs/manual/build_manual.py` | ✅ Verified Deterministic |
| **IEEE PDF Manuscript Rebuild** | `python paper/build_paper.py` | ✅ Verified Deterministic |
| **Master Release Package Rebuild** | `python scripts/build_release_package.py` | ✅ Verified Deterministic |
