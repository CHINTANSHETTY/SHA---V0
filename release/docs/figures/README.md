# Publication Figure Standards & Build Guide - KDR-CA-AEAD

This directory contains the official architecture diagrams and technical illustrations for the **KDR-CA-AEAD** IEEE manuscript.

---

## 1. Primary Source Authority & Design Standards

- **Primary Source**: Scalable Vector Graphics (`.svg`) is the authoritative, editable source.
- **Auto-Generated Exports**: Vector PDF (`.pdf`) and 300 DPI PNG (`.png`) are generated automatically via Python automation. **Do not edit PDF/PNG files manually.**
- **Color Palette**: IEEE Dark Navy (`#002B49`), IEEE Blue (`#1F77B4`), Emerald Green (`#2CA02C`), Warm Amber (`#FF7F0E`), Royal Purple (`#9467BD`), Light Slate Blue (`#F8FAFC`), Slate Charcoal (`#0F172A`).
- **Font Family**: Standardized `DejaVu Sans`, `Arial`, `Helvetica` font stack across all 8 figures.
- **Grayscale Print Legibility**: Contrast fill levels paired with `1.2pt` slate borders guarantee readability when printed in black-and-white.
- **Resolution**: PNG outputs are verified at 300 DPI minimum resolution (2385 px width).

---

## 2. Source Reproducibility & Regeneration Command

To re-build all 8 architecture figures automatically:

```powershell
$env:PYTHONPATH="."
python scripts/generate_architecture_figures.py
```

This updates all 24 `.svg`, `.pdf`, and `.png` files in `docs/figures/` and executes DPI image resolution validation.
