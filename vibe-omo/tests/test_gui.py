"""Smoke tests for GTK3 DistillationGUI."""

import os
import gi
import cairo
import pytest

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib


# ── Module-level smoke tests ────────────────────────────────────────

def test_gui_module_imports():
    from vibe_omo.distillation.gui import DistillationGUI, PRESETS, main
    assert callable(main)


def test_presets_defined():
    from vibe_omo.distillation.gui import PRESETS
    assert len(PRESETS) == 4
    for name in ["苯-甲苯 (常压)", "乙醇-水 (常压)", "甲醇-水 (常压)", "丙酮-苯 (常压)"]:
        assert name in PRESETS
        data = PRESETS[name]
        for key in ("xF", "xD", "xB", "R", "q", "alpha"):
            assert key in data


def test_preset_values_valid():
    from vibe_omo.distillation.gui import PRESETS
    from vibe_omo.distillation.core import McCabeThiele
    for name, params in PRESETS.items():
        calc = McCabeThiele(**params, n_eq_points=101)
        result = calc.calculate()
        assert result.converged, f"Preset '{name}' did not converge"
        assert result.n_stages >= 2


# ── GUI class smoke tests (no display needed) ───────────────────────

class TestGUI:
    def test_instantiate(self):
        from vibe_omo.distillation.gui import DistillationGUI
        app = DistillationGUI()
        assert app.app is not None
        assert app.app.get_application_id() == "com.vibe-omo.distillation"
        assert app._result is None
        assert app._plotter is not None

    def test_all_methods_exist(self):
        from vibe_omo.distillation.gui import DistillationGUI
        app = DistillationGUI()
        for name in [
            "_on_activate", "_build_window", "_build_menu", "_build_ui",
            "_build_left_panel", "_on_draw", "_connect_signals",
            "_on_key_press", "_get_params", "_calculate", "_load_preset",
            "_export_plot", "_show_help", "_show_error", "_show_info", "run",
        ]:
            assert hasattr(app, name), f"Missing method: {name}"

    def test_plotter_integration(self):
        from vibe_omo.distillation.gui import DistillationGUI
        from vibe_omo.distillation.plotter import CairoPlotter
        app = DistillationGUI()
        assert isinstance(app._plotter, CairoPlotter)

    def test_cairo_render_no_crash(self):
        from vibe_omo.distillation.gui import DistillationGUI
        app = DistillationGUI()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
        ctx = cairo.Context(surface)
        app._plotter.draw(ctx, 100, 100)


# ── Window creation and lifecycle tests (require display/xvfb) ──────

has_display = bool(os.environ.get("DISPLAY"))
skip_if_no_display = pytest.mark.skipif(
    not has_display,
    reason="Requires display server (use xvfb-run)",
)


@skip_if_no_display
class TestGUIWindow:
    def test_window_creates(self):
        from vibe_omo.distillation.gui import DistillationGUI
        app = DistillationGUI()
        app._on_activate(app.app)
        assert app.window is not None
        assert app.window.get_title() == "精馏塔理论塔板数计算 — McCabe-Thiele 图解法"
        app.window.destroy()

    def test_window_default_size(self):
        from vibe_omo.distillation.gui import DistillationGUI
        app = DistillationGUI()
        app._on_activate(app.app)
        size = app.window.get_default_size()
        assert size == (1200, 780), f"Expected (1200, 780), got {size}"
        app.window.destroy()

    def test_calculate_updates_labels(self):
        from vibe_omo.distillation.gui import DistillationGUI
        app = DistillationGUI()
        app._on_activate(app.app)
        app._calculate()
        assert app._result is not None
        assert app._result.converged
        assert app._result_labels["n_stages"].get_text() == str(app._result.n_stages)
        assert app._result_labels["n_rectifying"].get_text() == str(app._result.n_rectifying)
        status_text = app._result_labels["status"].get_text()
        assert "✓" in status_text or "⚠" in status_text
        app.window.destroy()

    def test_load_preset(self):
        from vibe_omo.distillation.gui import DistillationGUI, PRESETS
        app = DistillationGUI()
        app._on_activate(app.app)
        app._load_preset("乙醇-水 (常压)")
        assert app._entries["xF"].get_text() == "0.3"
        assert app._entries["xD"].get_text() == "0.85"
        app.window.destroy()

    def test_keyboard_shortcut_detection(self):
        from vibe_omo.distillation.gui import DistillationGUI
        app = DistillationGUI()
        app._on_activate(app.app)
        app.window.destroy()



