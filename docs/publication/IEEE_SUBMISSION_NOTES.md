# IEEE Submission Notes & Formatting Guidelines

This document specifies the exact formatting standards, font requirements, image specifications, and PDF validation rules required for IEEE journal and conference submissions of the **KDR-CA-AEAD** paper.

---

## 1. IEEE Manuscript Template

- **Class File**: `IEEEtran.cls` (v1.8b or newer).
- **Document Mode**: `\documentclass[journal,twocolumn,10pt]{IEEEtran}`.
- **Font Package**: Standard Computer Modern or Times New Roman (LaTeX `mathptmx` / `newtxtext`).
- **Paper Size**: US Letter (`8.5 x 11 inches`) or A4 depending on venue instructions.

---

## 2. Formatting Rules & Geometry

```text
+-------------------------------------------------------------+
| Margin          | US Letter (Inches) | Metric (mm)          |
+-----------------+--------------------+----------------------+
| Top             | 0.75 in            | 19.1 mm              |
| Bottom          | 1.00 in            | 25.4 mm              |
| Left            | 0.625 in           | 15.9 mm              |
| Right           | 0.625 in           | 15.9 mm              |
| Column Width    | 3.50 in            | 88.9 mm              |
| Column Gutter   | 0.25 in            | 6.3 mm               |
+-------------------------------------------------------------+
```

---

## 3. Font Embedding & Font Size Guidelines

- **Mandatory**: All fonts must be 100% Type 1 embedded (no Type 3 bitmap fonts allowed).
- **Title**: 24 pt, Bold.
- **Author Names**: 11 pt, Regular.
- **Section Headings (Level 1)**: 10 pt, Small Caps, Centered (`I. INTRODUCTION`).
- **Subsection Headings (Level 2)**: 10 pt, Italic, Left-Aligned (`A. Dynamic Rule Expansion`).
- **Main Body**: 10 pt, Regular.
- **Abstract & Keywords**: 9 pt, Bold/Italic.
- **Captions & Footnotes**: 8 pt, Regular.

---

## 4. Figure Resolution & Format Rules

- **Raster Graphics (PNG/JPEG)**: Minimum **300 DPI** for color photos, **600 DPI** for line art/plots.
- **Vector Graphics (PDF/EPS/SVG)**: Preferred for block diagrams, system architecture, and line graphs.
- **Color Space**: CMYK or RGB (verify RGB legibility on grayscale printers).
- **Bounding Boxes**: Crop figure white spaces tightly to prevent layout shift.

---

## 5. Reference Style (IEEE Standard)

- References listed numerically in order of appearance (`[1]`, `[2]`, `[3]`).
- Journal article example:
  > [1] N. Author and C. Coauthor, "Keyed Dynamically-Reconfigured Cellular Automata Encryption," *IEEE Transactions on Information Forensics and Security*, vol. 18, pp. 1024–1038, 2025. doi: 10.1109/TIFS.2025.1234567.
- Conference paper example:
  > [2] A. Researcher, "EtM AEAD bounds for dynamic permutations," in *Proc. IEEE International Conference on Communications (ICC)*, 2024, pp. 45–52.

---

## 6. IEEE PDF eXpress Checklist

Before uploading to the IEEE submission system:

1. Go to the [IEEE PDF eXpress Website](https://ieee-pdf-express.org/).
2. Enter the Conference/Journal ID.
3. Upload source LaTeX or PDF for compliance check.
4. Verify:
   - [x] No missing fonts.
   - [x] No non-embedded subset fonts.
   - [x] Page margins comply with IEEE standards.
   - [x] PDF version is 1.4 to 1.7 (Acrobat 5.0 compatible).
   - [x] Security permissions / password protection disabled.

---

## 7. ORCID & Author Metadata Requirements

- Every author must link their 16-digit ORCID iD during ScholarOne submission.
- Example format: `https://orcid.org/0000-0000-0000-0000`.

---

## 8. Electronic Copyright Form (eCF) Submission

- Upon acceptance, the corresponding author must complete the IEEE eCF.
- Select licensing model:
  - **Traditional IEEE Copyright** (standard for subscription journal issues).
  - **IEEE Open Access / Creative Commons CC-BY** (requires APC payment).
