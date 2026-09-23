"""Unit tests for VisualizationEngine (research/visualization.py)."""

import os
import tempfile
import pytest
from research.visualization import VisualizationEngine


class TestVisualizationEngine:
    """Tests for VisualizationEngine figure generation (PNG, SVG, PDF)."""

    def test_plot_throughput(self):
        """Verify throughput plot generates valid non-empty PNG file."""
        engine = VisualizationEngine()
        benchmark_data = {
            "scalability": [
                {"message_size_bytes": 64, "throughput_mbps": {"mean": 10.5}},
                {"message_size_bytes": 1024, "throughput_mbps": {"mean": 35.2}},
                {"message_size_bytes": 65536, "throughput_mbps": {"mean": 95.0}},
            ]
        }

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            res_path = engine.plot_throughput(benchmark_data, tmp_path)
            assert os.path.exists(res_path)
            assert os.path.getsize(res_path) > 1000
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_plot_sac_matrix(self):
        """Verify SAC heatmap generates valid non-empty PNG file."""
        engine = VisualizationEngine()
        sac_matrix = [
            [0.5, 0.48, 0.52],
            [0.51, 0.49, 0.50],
            [0.49, 0.51, 0.48],
        ]

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            res_path = engine.plot_sac_matrix(sac_matrix, tmp_path)
            assert os.path.exists(res_path)
            assert os.path.getsize(res_path) > 1000
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_export_all_figures(self):
        """Verify export_all_figures exports PNG, SVG, and PDF files."""
        engine = VisualizationEngine()
        with tempfile.TemporaryDirectory() as tmp_dir:
            generated = engine.export_all_figures(tmp_dir)

            assert len(generated) >= 4
            for fpath in generated:
                assert os.path.exists(fpath)
                assert os.path.getsize(fpath) > 500
