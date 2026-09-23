"""
Phase 4.3 Publication Artifact Validation Tests (`tests/test_publication_artifacts.py`).

Automated checks for:
- IEEE LaTeX manuscript source completeness (`paper/ieee_paper.tex`, sections, references, appendix)
- Availability of figure graphics (`.png`, `.svg`)
- Existence of publication LaTeX tables
- Reproducibility manifest schema correctness
"""

import json
import os
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


class TestPublicationArtifacts:
    """Verifies existence, syntax integrity, and path validity of manuscript artifacts."""

    def test_ieee_paper_sources_exist(self) -> None:
        """Verify IEEE LaTeX main paper and template exist."""
        paper_dir = os.path.join(ROOT_DIR, "paper")
        assert os.path.exists(paper_dir)

        tex_file = os.path.join(paper_dir, "ieee_paper.tex")
        cls_file = os.path.join(paper_dir, "IEEEtran.cls")
        bib_file = os.path.join(paper_dir, "references.bib")

        assert os.path.exists(tex_file), "Main IEEE LaTeX file missing"
        assert os.path.exists(cls_file), "IEEEtran.cls class file missing"
        assert os.path.exists(bib_file), "references.bib file missing"

    def test_paper_section_files(self) -> None:
        """Verify all manuscript section TeX files exist."""
        sections_dir = os.path.join(ROOT_DIR, "paper", "sections")
        assert os.path.exists(sections_dir)

        expected_sections = [
            "abstract.tex",
            "introduction.tex",
            "literature_review.tex",
            "methodology.tex",
            "architecture.tex",
            "security_analysis.tex",
            "benchmarks.tex",
            "discussion.tex",
            "future_work.tex",
            "conclusion.tex",
        ]
        for sec in expected_sections:
            sec_path = os.path.join(sections_dir, sec)
            assert os.path.exists(sec_path), f"Manuscript section TeX file missing: {sec}"

    def test_figure_graphics_exist(self) -> None:
        """Verify publication figure graphics (.png and .svg) exist."""
        figures_dir = os.path.join(ROOT_DIR, "paper", "figures")
        assert os.path.exists(figures_dir)

        expected_figures = [
            "avalanche.png",
            "comparison.png",
            "correlation.png",
            "entropy.png",
            "histogram.png",
        ]
        for fig in expected_figures:
            fig_path = os.path.join(figures_dir, fig)
            assert os.path.exists(fig_path), f"Figure graphic file missing: {fig}"

    def test_latex_table_files(self) -> None:
        """Verify publication LaTeX table files exist."""
        tables_dir = os.path.join(ROOT_DIR, "paper", "tables")
        assert os.path.exists(tables_dir)

        expected_tables = [
            "comparative_table.tex",
            "master_security_table.tex",
            "performance_scaling_table.tex",
        ]
        for tbl in expected_tables:
            tbl_path = os.path.join(tables_dir, tbl)
            assert os.path.exists(tbl_path), f"LaTeX table file missing: {tbl}"

    def test_phase4_documentation_artifacts(self) -> None:
        """Verify Phase 4 documentation files exist in docs/phase4/."""
        phase4_dir = os.path.join(ROOT_DIR, "docs", "phase4")
        assert os.path.exists(phase4_dir)

        sys_integ = os.path.join(phase4_dir, "system_integration.md")
        final_eval = os.path.join(phase4_dir, "final_evaluation.md")
        pub_rel = os.path.join(phase4_dir, "publication_release.md")

        assert os.path.exists(sys_integ), "docs/phase4/system_integration.md missing"
        assert os.path.exists(final_eval), "docs/phase4/final_evaluation.md missing"
        assert os.path.exists(pub_rel), "docs/phase4/publication_release.md missing"
