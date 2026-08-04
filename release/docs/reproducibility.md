# Reproducibility Guide & FAIR Archival

This document provides full instructions for independently executing the **KDR-CA-AEAD** reproducibility pipeline, generating evaluation datasets, building camera-ready 300 DPI IEEE figures, and verifying test suite execution.

---

## 1. Master Reproducibility Pipeline Overview

The repository includes a single, fully automated master evaluation script:
`scripts/run_phase2_5_reproducibility.py`

This script executes:
1. **Full Pytest Test Suite Verification**: Runs unit, integration, and security tests.
2. **Benchmark Execution**: Evaluates throughput, latency, avalanche criterion (SAC), and Shannon entropy.
3. **Dataset Generation**: Exports raw JSON metrics and comparative Markdown/CSV tables.
4. **Publication Asset Generation**: Produces 300 DPI vector SVG and raster PNG graphs for inclusion in `paper/ieee_paper.tex`.

---

## 2. Step-by-Step Reproduction Instructions

### Step 1: Environment Preparation

Ensure Python 3.10+ and required dependencies are installed:
```powershell
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
python -m pip install -r requirements.txt
```

Set the module path:
```powershell
# Windows PowerShell
$env:PYTHONPATH="."

# Linux / macOS Bash
export PYTHONPATH="."
```

### Step 2: Run Master Reproducibility Pipeline

Execute the master evaluation pipeline:
```powershell
python scripts/run_phase2_5_reproducibility.py
```

### Step 3: Verify Output Artifacts

Confirm that the following output directory structure and files are generated:

```text
results/
├── master_results.json               # Full JSON benchmark & test dataset
├── tables/
│   ├── performance_summary.csv       # Throughput & latency CSV table
│   └── comparative_metrics.md        # Comparative Markdown table
└── security_graphs/
    ├── avalanche_plot.png            # 300 DPI SAC Avalanche plot
    ├── avalanche_plot.svg            # Vector SAC Avalanche plot
    ├── throughput_bar.png            # 300 DPI Throughput comparison bar chart
    └── throughput_bar.svg            # Vector Throughput comparison bar chart
```

---

## 3. Building IEEE LaTeX Paper Package

To compile the IEEE manuscript using the generated figures and data:

```powershell
cd paper
pdflatex ieee_paper.tex
bibtex ieee_paper
pdflatex ieee_paper.tex
pdflatex ieee_paper.tex
```

Output manuscript: `paper/ieee_paper.pdf`

---

## 4. FAIR Data Principles Compliance

KDR-CA-AEAD adheres to FAIR archival standards:
- **Findable**: Documented in `CITATION.cff`, `citation.bib`, and indexed via GitHub release v1.0.0.
- **Accessible**: Openly licensed under Apache 2.0 with public repository access.
- **Interoperable**: Standard JSON, CSV, and BibTeX output schemas.
- **Reusable**: Deterministic random seeds (`seed=42`) ensure exact numerical reproducibility across independent hardware platforms.
