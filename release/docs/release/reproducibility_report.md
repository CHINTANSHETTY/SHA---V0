# Deterministic Reproducibility Audit Report — KDR-CA-AEAD v1.0.0

All publication deliverables are 100% reproducible via single-command automated build scripts:

| Publication Deliverable | Regeneration Command | Reproducibility Status |
| :--- | :--- | :--- |
| **Architecture Figures** | `python scripts/generate_architecture_figures.py` | ✅ Verified Deterministic |
| **Benchmark Visualizations** | `python scripts/generate_benchmark_graphs.py` | ✅ Verified Deterministic |
| **API Reference Documentation** | `python docs/api/build_api_docs.py` | ✅ Verified Deterministic |
| **User Manual Suite** | `python docs/manual/build_manual.py` | ✅ Verified Deterministic |
| **IEEE PDF Manuscript** | `python paper/build_paper.py` | ✅ Verified Deterministic |
