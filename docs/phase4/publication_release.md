# Phase 4.3 – IEEE Publication & Final Release Package Specification

## I. Executive Summary

This document specifies the Phase 4.3 IEEE Publication and Release Packaging architecture for the **KDR-CA-AEAD** (Keyed Dynamically-Reconfigured Cellular Automata Authenticated Encryption with Associated Data) research framework.

Phase 4.3 consolidates all manuscript sources, documentation hubs, benchmark outputs, statistical validation datasets, evaluation summaries, and reproducibility metadata into a standardized, production-ready release artifact (`release/`).

---

## II. Release Directory Hierarchy

```text
release/
├── paper/
│   ├── ieee_paper.tex
│   ├── IEEEtran.cls
│   ├── references.bib
│   ├── sections/
│   ├── figures/
│   └── tables/
├── docs/
│   ├── index.md
│   ├── architecture.md
│   ├── user_guide.md
│   ├── developer_guide.md
│   ├── security_guide.md
│   ├── benchmark_guide.md
│   ├── reproducibility.md
│   └── phase4/
│       ├── system_integration.md
│       ├── final_evaluation.md
│       └── publication_release.md
├── benchmark_results/
│   ├── benchmark_results.json
│   ├── benchmark_results.csv
│   └── benchmark_graphs/
├── validation_results/
│   ├── statistical_validation_report.md
│   ├── statistical_validation_summary.json
│   └── statistical_validation_table.tex
├── evaluation_results/
│   ├── reports/
│   ├── latex/
│   ├── csv/
│   ├── json/
│   └── metadata/
├── supplementary/
├── metadata/
│   ├── reproducibility_manifest.json
│   └── requirements.txt
├── checksums_sha256.txt
├── checksums_sha512.txt
├── release_manifest.json
├── RELEASE_NOTES.md
├── VERSION
└── LICENSE
```

---

## III. Build Automation & Release Workflow

The release package is constructed automatically via:
```powershell
python scripts/build_final_release.py
```

### Automation Steps:
1. **Directory Setup**: Constructs the target hierarchy in `release/`.
2. **Artifact Packaging**: Copies manuscript TeX files, section drafts, figures (`.png`, `.svg`), LaTeX tables, Markdown documentation, benchmark JSON/CSV datasets, and Phase 4.2 evaluation results.
3. **Reproducibility Metadata**: Generates `release/metadata/reproducibility_manifest.json` capturing Git commit hash, Python version, OS distribution, CPU model, core counts, RAM, PRNG seed (`42`), and execution timestamp.
4. **Checksum Manifests**: Generates SHA-256 (`checksums_sha256.txt`) and SHA-512 (`checksums_sha512.txt`) cryptographic hashes for all released files.
5. **Granular Manifest**: Compiles `release_manifest.json` containing entry metadata (relative path, byte size, SHA-256, SHA-512, ISO timestamp, version `1.0.0`, category).

---

## IV. Archival & Citation Recommendations

1. **Zenodo Archival**: Upload `release/` package zip archive to Zenodo to obtain a digital object identifier (DOI).
2. **IEEE DataPort**: Export benchmark and validation CSV/JSON datasets to IEEE DataPort for peer review transparency.
3. **GitHub Release Tag**: Tag commit `v1.0.0` on GitHub repository (`https://github.com/CHINTANSHETTY/SHA---V0`).
4. **BibTeX Citation**: Use standardized citation format provided in `CITATION.cff` and `citation.bib`.

---

## V. Phase 4.3 Final Acceptance Checklist

- [x] IEEE manuscript finalized (`paper/ieee_paper.tex`, sections, references, appendix)
- [x] Figures verified (.png, .svg)
- [x] Tables verified (.tex)
- [x] References & citations verified (`references.bib`, `CITATION.cff`)
- [x] README updated with Phase 4 release metadata
- [x] CHANGELOG updated
- [x] CITATION.cff updated
- [x] Release package generated (`release/`)
- [x] Reproducibility package generated (`release/metadata/reproducibility_manifest.json`, `requirements.txt`)
- [x] Detailed release manifest generated (`release/release_manifest.json`)
- [x] SHA-256 checksums generated (`release/checksums_sha256.txt`)
- [x] SHA-512 checksums generated (`release/checksums_sha512.txt`)
- [x] Publication artifact tests pass 100%
- [x] Workspace regression test suite passes 100%
- [x] Public APIs unchanged
- [x] No cryptographic behavior changes
