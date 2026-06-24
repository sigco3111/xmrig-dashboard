"""Unit tests for v0.2.0 visualization helpers.

These tests use importlib to load miner-dashboard.py (which has a hyphen
in its filename and can't be imported directly). The helpers are pure
functions that return Rich markup strings; we assert structural
properties (no exceptions, contains expected tokens) without depending
on a live Textual app or a running XMRig process.

Run: python3 -m pytest tests/test_visual.py -v
Or:  /path/to/conda/envs/xmrig-dash/bin/python -m pytest tests/
"""

import importlib.util
import pathlib
import re

import pytest


# Load miner-dashboard.py as a module (filename has a hyphen, so we
# can't just `import miner_dashboard`).
ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "miner-dashboard.py"
spec = importlib.util.spec_from_file_location("miner_dashboard", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# ---------- render_donut ----------

class TestDonut:
    def test_zero_shares_returns_placeholder(self):
        out = mod.render_donut(0, 0)
        assert "no shares yet" in out
        # No Rich markup for a "real" donut
        assert "▄" not in out  # no donut rows
        assert "██" not in out

    def test_nonzero_renders_donut_rows(self):
        out = mod.render_donut(100, 5)
        # Should contain the donut cells
        assert "▄" in out
        assert "█" in out
        # And a percent label
        assert "acc" in out
        # The percent should be ~95.2 (100/105)
        assert "95" in out

    def test_low_acceptance_uses_warning_color(self):
        out = mod.render_donut(50, 50)  # 50% acceptance
        # Below 90% threshold -> warning color
        assert "#ffaa00" in out

    def test_high_acceptance_uses_default(self):
        out = mod.render_donut(99, 1)  # 99%
        assert "#33ff66" in out
        assert "99" in out

    def test_total_lines_is_consistent(self):
        """A donut should render 4 rows total.

        The helper builds a 4-row donut and appends the label inline
        after the 4th row, so the output has 4 newline-separated lines
        (the 4th line contains both the bottom arc and the percentage
        label)."""
        out = mod.render_donut(50, 50)
        lines = out.split("\n")
        assert len(lines) == 4
        # The label is on the 4th line
        assert "acc" in lines[-1]


# ---------- render_core_bars ----------

class TestCoreBars:
    def test_empty_returns_placeholder(self):
        out = mod.render_core_bars([])
        assert "no core data" in out

    def test_eight_cores_render(self):
        per_core = [10, 25, 50, 75, 90, 100, 5, 30]
        out = mod.render_core_bars(per_core, width=4)
        # Should have N+1 lines (N bar rows + 1 caption)
        lines = out.split("\n")
        assert len(lines) == 5  # width=4 bars + 1 caption
        # Caption should contain average
        assert "avg" in lines[-1]
        assert "48" in lines[-1]  # average of [10,25,50,75,90,100,5,30] = 48.125

    def test_caps_at_32_visible_cores(self):
        # 40 cores, should show 32 + "+8 more" suffix
        per_core = [50.0] * 40
        out = mod.render_core_bars(per_core, width=2)
        assert "+8 more" in out

    def test_uses_block_chars(self):
        # 50% load on a 3-cell bar: 1 empty (▁) + 2 full (█) per column
        per_core = [50.0] * 4
        out = mod.render_core_bars(per_core, width=3)
        # Should have full-block (█) characters for the filled rows
        assert chr(0x2588) in out  # █
        # And lower-1/8 block (▁) for the empty row
        assert chr(0x2581) in out  # ▁


# ---------- render_forecast_bars ----------

class TestForecastBars:
    def test_empty_returns_placeholder(self):
        out = mod.render_forecast_bars([])
        assert "no data yet" in out
        assert "fills in" in out

    def test_all_zeros_returns_placeholder(self):
        """All-zero data is treated as 'no data' — avoids rendering
        a flat line that looks like a bug."""
        out = mod.render_forecast_bars([0.0, 0.0, 0.0])
        assert "no data yet" in out

    def test_positive_values_render_blocks(self):
        out = mod.render_forecast_bars([0.001, 0.002, 0.003, 0.005])
        # Should contain ramp blocks
        assert "▂" in out or "▃" in out
        # And the max label
        assert "max" in out
        assert "$0.0050" in out

    def test_caps_at_14_days(self):
        days = [0.001 * (i + 1) for i in range(20)]
        out = mod.render_forecast_bars(days)
        # Count bar chars - should be at most 14
        # Ramp characters: ▁▂▃▄▅▆▇
        ramp = "▁▂▃▄▅▆▇"
        bar_count = sum(1 for ch in out if ch in ramp)
        assert bar_count <= 14


# ---------- render_core_heatmap ----------

class TestHeatmap:
    def test_empty_returns_placeholder(self):
        out = mod.render_core_heatmap([], [])
        assert "no core samples yet" in out

    def test_pads_to_width(self):
        """If history is shorter than width, the helper pads with empty."""
        per_core = [50.0, 60.0]
        history = [[40.0, 50.0]]  # only 1 sample
        out = mod.render_core_heatmap(per_core, history, width=12)
        # Should have 2 core rows + 1 footer
        lines = out.split("\n")
        assert len(lines) == 3
        # Footer should have "old" and "now"
        assert "old" in lines[-1]
        assert "now" in lines[-1]

    def test_uses_heat_chars(self):
        per_core = [50.0, 80.0]
        history = [
            [10.0, 20.0],
            [50.0, 80.0],
            [90.0, 95.0],
        ]
        out = mod.render_core_heatmap(per_core, history, width=3)
        # Should have at least one of: ░▒▓
        assert any(ch in out for ch in "▒▓")

    def test_legend_uses_palette_colors(self):
        per_core = [50.0, 90.0]
        # Mix of mid-load (▒ → fg) and high-load (▓ → accent) so both
        # colors are exercised.
        history = [
            [50.0, 90.0],
            [50.0, 90.0],
        ]
        out = mod.render_core_heatmap(per_core, history, width=2)
        # Three of the four palette levels should be reachable.
        # We pick fg_dim, fg, and accent.
        assert "#1f8033" in out  # fg_dim
        assert "#33ff66" in out  # fg
        assert "#00ff9c" in out  # accent


# ---------- render_header_logo ----------

class TestHeaderLogo:
    def test_returns_nonempty_string(self):
        out = mod.render_header_logo()
        assert isinstance(out, str)
        assert len(out) > 0

    def test_uses_accent_color(self):
        out = mod.render_header_logo()
        # Should be bold + accent color
        assert "[bold" in out
        assert "#00ff9c" in out

    def test_contains_block_chars(self):
        out = mod.render_header_logo()
        # Should have ▀ ▄ █ characters
        assert any(ch in out for ch in "█▀▄")
