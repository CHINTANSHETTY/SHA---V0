# Benchmark Visualization Standards & Regeneration Guide - KDR-CA-AEAD

This directory contains the official publication-ready benchmark graphs, performance analytics, and statistical plots for the **KDR-CA-AEAD** IEEE manuscript.

---

## 1. Design & Vector Formatting Standards

- **Primary Source Format**: Scalable Vector Graphics (`.svg`) is the authoritative primary editable source format.
- **LaTeX Format**: Vector PDF (`.pdf`) compiled directly via `pdflatex` or `reportlab`.
- **Raster Format**: Portable Network Graphics (`.png`) rendered at 300 DPI minimum resolution for high-print quality.
- **Color Palette**: IEEE Navy (`#002B49`), IEEE Blue (`#1F77B4`), Emerald Green (`#2CA02C`), Amber (`#FF7F0E`), Royal Purple (`#9467BD`), Light Slate (`#F8FAFC`), Slate Charcoal (`#0F172A`).
- **Typography**: Standardized `DejaVu Sans`, `Arial`, `Helvetica` font stack across all 30 graph groups.
- **Grayscale Print Legibility**: Contrast fills, hatch patterns (`//`, `\\\\`), distinct marker shapes (`o`, `s`, `^`, `d`), and dashed lines guarantee full readability in monochrome/grayscale print.

---

## 2. Source Reproducibility & Regeneration Command

To re-generate all 30 benchmark graph groups (90 files) automatically:

```powershell
$env:PYTHONPATH="."
python scripts/generate_benchmark_graphs.py
```

This script validates benchmark dataset schema, computes statistical metrics, plots every figure, and verifies 300 DPI resolution.
