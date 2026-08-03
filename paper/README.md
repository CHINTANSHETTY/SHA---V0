# IEEE Publication Package - KDR-CA-AEAD Final Paper

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Task:** Ashwitha – Phase 3.2.1 (IEEE Research Paper – Final Version)  
**IEEE Target:** IEEE Transactions on Information Forensics and Security  
**Output Deliverables:** LaTeX Sources, BibTeX Database, Compiled IEEE Manuscript (`paper/final.pdf`)  

---

## 1. Directory & File Architecture

```
paper/
├── ieee_paper.tex             # Master IEEE LaTeX document
├── IEEEtran.cls               # Official IEEE document class
├── references.bib             # BibTeX reference database (20+ peer-reviewed citations)
├── build_paper.py             # Build automation & citation validation script
├── final.pdf                  # Compiled two-column IEEE paper deliverable
└── sections/                  # Modular LaTeX sections
    ├── abstract.tex           # Title, authors, abstract, keywords
    ├── introduction.tex       # Intro, problem statement, contributions
    ├── literature_review.tex  # Related work & comparative taxonomy
    ├── methodology.tex        # Mathematical model, HKDF & Candidate A-Chain
    ├── architecture.tex       # System architecture & IEEE algorithms
    ├── security_analysis.tex  # NIST SP 800-22, SAC, entropy, attack bounds
    ├── benchmarks.tex         # Performance micro-benchmarks & comparisons
    ├── discussion.tex         # Trade-offs, strengths, limitations
    ├── future_work.tex        # Hardware prototyping & post-quantum directions
    └── conclusion.tex         # Concluding summary & findings
```

---

## 2. Compilation & Build Instructions

### Method 1: Using Python Master Builder (Recommended)

```powershell
$env:PYTHONPATH="."
python paper/build_paper.py
```
This script audits LaTeX references, checks BibTeX citations, attempts compilation via system `pdflatex` / `latexmk` if installed, and produces `paper/final.pdf`.

### Method 2: Standard LaTeX Command Line Compilation

If a TeX distribution (TeX Live / MiKTeX / Tectonic) is installed:

```bash
# Using pdflatex + bibtex
pdflatex ieee_paper.tex
bibtex ieee_paper
pdflatex ieee_paper.tex
pdflatex ieee_paper.tex

# Using latexmk
latexmk -pdf ieee_paper.tex

# Using tectonic
tectonic ieee_paper.tex
```

---

## 3. Required LaTeX Packages

The manuscript requires standard IEEEtran packages:
- `amsmath`, `amssymb`, `amsfonts` (Mathematical formatting)
- `algorithm`, `algorithmic` (IEEE Pseudocode rendering)
- `graphicx` (Figure placement)
- `booktabs`, `array` (Publication tables)
- `cite` (BibTeX citations)
- `hyperref` (Clickable cross-references)

---

## 4. Citation & Reference Verification Summary

- **Total BibTeX Entries**: 20 peer-reviewed papers (IEEE, ACM, IACR, NIST)
- **Broken References**: 0
- **Missing Citations**: 0
- **Compilation Status**: Clean build (`paper/final.pdf` generated)
