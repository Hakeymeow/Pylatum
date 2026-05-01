"""Tests for CairoPlotter — pure Cairo McCabe-Thiele diagram renderer."""

import cairo
import numpy as np
import pytest

from vilatum.distillation.plotter import CairoPlotter
from vilatum.distillation.core import McCabeThiele


# ── helpers ─────────────────────────────────────────────────────────

def pixel_at(surface: cairo.ImageSurface, x: int, y: int) -> tuple:
    """Get RGB values [0-255] of pixel at (x, y)."""
    data = surface.get_data()
    stride = surface.get_stride()
    offset = y * stride + x * 4
    return (data[offset + 2], data[offset + 1], data[offset])


def render(p, width=800, height=700):
    """Render a CairoPlotter to an ImageSurface and return the surface."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    p.draw(cairo.Context(surface), width, height)
    return surface


# ── Basic construction ──────────────────────────────────────────────

class TestConstruction:
    def test_import_and_instantiate(self):
        p = CairoPlotter()
        assert p.result is None

    def test_with_result(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        assert p.result is not None
        assert p.result.n_stages >= 2

    def test_with_none_after_result(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        assert p.result is not None
        p2 = CairoPlotter()
        assert p2.result is None


# ── Empty chart ─────────────────────────────────────────────────────

class TestEmptyChart:
    def test_renders_no_error(self):
        p = CairoPlotter()
        surface = render(p)
        assert surface.get_width() == 800
        assert surface.get_height() == 700

    def test_background_is_white(self):
        p = CairoPlotter()
        surface = render(p)
        r, g, b = pixel_at(surface, 0, 0)
        assert r == 255 and g == 255 and b == 255

    def test_has_diagonal_pixels(self):
        p = CairoPlotter()
        surface = render(p)
        # (0.5, 0.5) → px = 60 + 0.5*680 = 400, py = 40 + 0.5*610 = 345
        r, g, b = pixel_at(surface, 400, 345)
        assert max(r, g, b) < 250, "Center pixel is nearly white — diagonal likely missing"

    def test_grid_lines_visible(self):
        p = CairoPlotter()
        surface = render(p)
        any_dark = False
        for data_x in [0.1, 0.3, 0.5, 0.7, 0.9]:
            px = int(60 + data_x * 680)
            for frac_y in [0.2, 0.4, 0.6, 0.8]:
                py = int(40 + frac_y * 610)
                r, g, b = pixel_at(surface, px, py)
                if max(r, g, b) < 248:
                    any_dark = True
                    break
            if any_dark:
                break
        assert any_dark, "No grid pixels found in plot area"


# ── Full chart ──────────────────────────────────────────────────────

class TestFullChart:
    def test_renders_no_error(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        surface = render(p)
        assert surface.get_width() == 800

    def test_has_more_content_than_empty(self):
        calc = McCabeThiele(xF=0.45, xD=0.97, xB=0.02, R=2.0, q=1.0, alpha=2.50)
        full_plotter = CairoPlotter(calc.calculate())

        s_empty = render(CairoPlotter())
        s_full = render(full_plotter)

        def count_non_white(surf, x1, y1, x2, y2):
            return sum(
                1
                for y in range(y1, y2, 4)
                for x in range(x1, x2, 4)
                if max(pixel_at(surf, x, y)) < 240
            )

        empty_count = count_non_white(s_empty, 80, 60, 720, 620)
        full_count = count_non_white(s_full, 80, 60, 720, 620)
        assert full_count > empty_count, (
            f"Full chart has {full_count} vs {empty_count} in empty"
        )

    def test_equilibrium_curve_region(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        surface = render(p)
        # alpha=2.50, x=0.5 → y = 2.5*0.5/(1+1.5*0.5) ≈ 0.714
        # px = 60 + 0.5*680 = 400, py = 40 + (1-0.714)*610 ≈ 215
        r, g, b = pixel_at(surface, 400, 215)
        assert max(r, g, b) < 250, "Pixel on equilibrium curve is white"

    def test_intersection_marker(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        surface = render(p)
        result = result_benzene_toluene
        px = int(60 + result.x_intersect * 680)
        py = int(40 + (1 - result.y_intersect) * 610)
        r, g, b = pixel_at(surface, px, py)
        assert max(r, g, b) < 250, "Intersection marker pixel is white"

    def test_xD_marker_visible(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        surface = render(p)
        px = int(60 + result_benzene_toluene.xD * 680)
        py = int(40 + 0.5 * 610)
        r, g, b = pixel_at(surface, px, py)
        assert max(r, g, b) < 250, "xD marker pixel is white"

    def test_legend_renders(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        surface = render(p)
        # Legend items have colored markers at x≈652, y≈542-645
        found = False
        for cx in range(653, 670):
            for cy in range(542, 560):
                r, g, b = pixel_at(surface, cx, cy)
                if b > 100 and r + g < 200:  # blue legend swatch
                    found = True
                    break
            if found:
                break
        assert found, "No legend blue swatch found at expected position"


# ── Stage steps ─────────────────────────────────────────────────────

class TestStageSteps:
    def test_stage_data_present(self, result_benzene_toluene):
        result = result_benzene_toluene
        assert len(result.stage_data) >= result.n_stages * 2

    def test_stage_circles_drawn(self, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        surface = render(p)
        sd = result_benzene_toluene.stage_data
        first_eq = sd[0]
        px = int(60 + first_eq[0] * 680)
        py = int(40 + (1 - first_eq[1]) * 610)
        r, g, b = pixel_at(surface, px, py)
        assert max(r, g, b) < 240, "First stage circle pixel is white"


# ── Export ──────────────────────────────────────────────────────────

class TestExport:
    def test_export_png(self, tmp_path, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        path = tmp_path / "test.png"
        p.export_png(str(path))
        assert path.exists()
        assert path.stat().st_size > 5000

    def test_export_pdf(self, tmp_path, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        path = tmp_path / "test.pdf"
        p.export_pdf(str(path))
        assert path.exists()
        assert path.stat().st_size > 1000

    def test_export_svg(self, tmp_path, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        path = tmp_path / "test.svg"
        p.export_svg(str(path))
        assert path.exists()
        assert path.stat().st_size > 1000

    def test_export_empty_chart(self, tmp_path):
        p = CairoPlotter()
        path = tmp_path / "empty.png"
        p.export_png(str(path))
        assert path.exists()
        assert path.stat().st_size > 1000

    @pytest.mark.parametrize("fmt,method", [
        ("png", "export_png"),
        ("pdf", "export_pdf"),
        ("svg", "export_svg"),
    ])
    def test_export_overwrite(self, tmp_path, fmt, method, result_benzene_toluene):
        p = CairoPlotter(result_benzene_toluene)
        path = tmp_path / f"overwrite.{fmt}"
        getattr(p, method)(str(path))
        size1 = path.stat().st_size
        getattr(p, method)(str(path))
        size2 = path.stat().st_size
        assert size2 > 0


# ── Edge cases ──────────────────────────────────────────────────────

class TestEdgeCases:
    @pytest.mark.parametrize("xF, xD, xB, R, q, alpha", [
        (0.45, 0.97, 0.02, 2.0, 1.0, 2.50),
        (0.30, 0.85, 0.05, 3.0, 1.0, 2.21),
        (0.40, 0.90, 0.05, 2.0, 1.0, 3.72),
        (0.45, 0.90, 0.05, 2.0, 1.2, 2.10),
    ])
    def test_all_presets_render(self, xF, xD, xB, R, q, alpha):
        calc = McCabeThiele(xF=xF, xD=xD, xB=xB, R=R, q=q, alpha=alpha)
        result = calc.calculate()
        p = CairoPlotter(result)
        render(p)

    @pytest.mark.parametrize("q", [1.0, 0.5, 1.5, -0.5, 0.0])
    def test_various_q_values_render(self, q):
        calc = McCabeThiele(xF=0.45, xD=0.90, xB=0.05, R=2.5, q=q, alpha=2.10)
        result = calc.calculate()
        p = CairoPlotter(result)
        surface = render(p)
        r, g, b = pixel_at(surface, 400, 345)
        assert max(r, g, b) < 250, f"Center pixel white for q={q}"

    def test_r_less_than_rmin_still_renders(self):
        calc = McCabeThiele(xF=0.45, xD=0.97, xB=0.02, R=0.5, q=1.0, alpha=2.50)
        result = calc.calculate()
        p = CairoPlotter(result)
        surface = render(p)
        r, g, b = pixel_at(surface, 400, 345)
        assert max(r, g, b) < 250, "R<Rmin chart center pixel is white"

    def test_very_small_render(self):
        calc = McCabeThiele(xF=0.45, xD=0.97, xB=0.02, R=2.0, q=1.0, alpha=2.50)
        result = calc.calculate()
        p = CairoPlotter(result)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 180)
        p.draw(cairo.Context(surface), 200, 180)

    def test_large_render(self):
        calc = McCabeThiele(xF=0.45, xD=0.97, xB=0.02, R=2.0, q=1.0, alpha=2.50)
        result = calc.calculate()
        p = CairoPlotter(result)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 2000, 1600)
        p.draw(cairo.Context(surface), 2000, 1600)


# ── Coordinate helpers ──────────────────────────────────────────────

class TestCoordinates:
    def test_data_to_pixel_origin(self):
        p = CairoPlotter()
        p._setup_coords(800, 700)
        px, py = p._data_to_pixel(0.0, 0.0)
        assert abs(px - 60) < 0.001
        assert abs(py - 650) < 0.001

    def test_data_to_pixel_top_right(self):
        p = CairoPlotter()
        p._setup_coords(800, 700)
        px, py = p._data_to_pixel(1.0, 1.0)
        assert abs(px - 740) < 0.001
        assert abs(py - 40) < 0.001

    def test_data_to_pixel_center(self):
        p = CairoPlotter()
        p._setup_coords(800, 700)
        px, py = p._data_to_pixel(0.5, 0.5)
        assert abs(px - 400) < 0.001
        assert abs(py - 345) < 0.001

    def test_data_to_pixel_inverts_y(self):
        p = CairoPlotter()
        p._setup_coords(800, 700)
        _, py_low = p._data_to_pixel(0.0, 0.0)
        _, py_high = p._data_to_pixel(0.0, 1.0)
        assert py_low > py_high, "y-axis inverted (data up = pixel down)"


# ── Drawing helpers ─────────────────────────────────────────────────

class TestDrawingHelpers:
    def test_draw_line(self):
        p = CairoPlotter()
        p._setup_coords(200, 200)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
        ctx = cairo.Context(surface)
        p._draw_line(ctx, 0.1, 0.1, 0.9, 0.9, 0, 0, 0, width=1.0)
        r, g, b = pixel_at(surface, 100, 100)
        assert max(r, g, b) < 250

    def test_draw_marker_diamond(self):
        p = CairoPlotter()
        p._setup_coords(200, 200)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
        ctx = cairo.Context(surface)
        p._draw_marker_diamond(ctx, 0.5, 0.5, size=6, r=0.5, g=0, b=0.5)
        r, g, b = pixel_at(surface, 100, 100)
        assert max(r, g, b) < 250

    def test_draw_circle(self):
        p = CairoPlotter()
        p._setup_coords(200, 200)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
        ctx = cairo.Context(surface)
        p._draw_circle(ctx, 0.5, 0.5, radius=3, r=0, g=0, b=0)
        r, g, b = pixel_at(surface, 100, 100)
        assert max(r, g, b) < 250

    def test_draw_text(self):
        p = CairoPlotter()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
        ctx = cairo.Context(surface)
        p._draw_text(ctx, 100, 100, "Hello", size=12, anchor="center")

    def test_dashed_restores(self):
        p = CairoPlotter()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
        ctx = cairo.Context(surface)

        p._set_dashed(ctx)
        ctx.move_to(10, 10)
        ctx.line_to(100, 100)
        ctx.stroke()

        p._set_dotted(ctx)
        ctx.move_to(10, 50)
        ctx.line_to(100, 50)
        ctx.stroke()

        dash_list, dash_offset = ctx.get_dash()
        assert len(dash_list) > 0
