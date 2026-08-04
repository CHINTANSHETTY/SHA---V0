# IEEE Publication Package - KDR-CA-AEAD Final Paper

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Task:** Ashwitha – Phase 4.2 (IEEE Research Paper Finalization)  
**IEEE Target:** IEEE Transactions on Information Forensics and Security  
**Output Deliverables:** LaTeX Sources (`IEEE_Paper.tex`), BibTeX Database (`references.bib`), Publication Figures (`figures/`), Tables (`tables/`), Appendices (`appendix/`), Supplementary Material (`supplementary/`), Compiled Manuscripts (`paper/IEEE_Paper.pdf`, `paper/final.pdf`).

---

## 1. Directory & File Architecture

```text
paper/
├── IEEE_Paper.tex             # Master IEEE LaTeX document (Titlecase)
├── ieee_paper.tex             # Master IEEE LaTeX document (Lowercase alias)
├── IEEE_Paper.pdf             # Publication-ready IEEE two-column PDF
├── final.pdf                  # Compiled IEEE two-column PDF deliverable
├── IEEEtran.cls               # Official IEEE document class
├── references.bib             # BibTeX reference database (20+ peer-reviewed citations)
├── build_paper.py             # Master build automation & validation script
├── figures/                   # 300 DPI PNG & vector SVG publication figures
│   ├── avalanche.png / .svg   # Plaintext & Key avalanche plot
│   ├── comparison.png / .svg  # Throughput comparative bar chart
│   ├── correlation.png / .svg # Bit correlation plot
│   ├── entropy.png / .svg     # Shannon entropy distribution
│   └── histogram.png / .svg   # State frequency histogram
├── tables/                    # TeX & CSV publication tables
│   ├── master_security_table.tex
│   ├── performance_scaling_table.tex
│   └── comparative_table.tex
├── appendix/                  # Mathematical proofs & algorithms
│   └── appendix.tex
├── supplementary/             # Reproducibility & FAIR compliance guide
│   └── supplementary.tex
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

### Method 1: Master Python Paper Builder (Recommended)

```powershell
$env:PYTHONPATH="."
python paper/build_paper.py
```
This script audits LaTeX references, checks BibTeX citations, attempts compilation via system `pdflatex` / `latexmk` if installed, and produces both `paper/IEEE_Paper.pdf` and `paper/final.pdf`.

### Method 2: Standard LaTeX Command Line Compilation

If a TeX distribution (TeX Live / MiKTeX / Tectonic) is installed:

```bash
# Using pdflatex + bibtex
pdflatex IEEE_Paper.tex
bibtex IEEE_Paper
pdflatex IEEE_Paper.tex
pdflatex IEEE_Paper.tex

# Using latexmk
latexmk -pdf IEEE_Paper.tex

# Using tectonic
tectonic IEEE_Paper.tex
```

---

## 3. Citation & Reference Verification Summary

- **Total BibTeX Entries**: 20 peer-reviewed papers (IEEE, ACM, IACR, NIST)
- **Broken References**: 0
- **Missing Citations**: 0
- **Unresolved Placeholders**: 0
- **Compilation Status**: Clean build (`paper/IEEE_Paper.pdf` & `paper/final.pdf` generated)
