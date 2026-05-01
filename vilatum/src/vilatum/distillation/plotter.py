"""
Pure Cairo-based renderer for McCabe-Thiele distillation diagrams.

No matplotlib, no GTK dependency — works with any Cairo surface
(PNG, PDF, SVG, or a GTK DrawingArea context).
"""

from __future__ import annotations

import math
from typing import Optional

import cairo
import numpy as np

from .core import McCabeThieleResult


class CairoPlotter:
    """Cairo-based McCabe-Thiele diagram renderer.

    Parameters
    ----------
    result : McCabeThieleResult or None
        If None, renders an empty chart (diagonal + grid only).
    """

    MARGIN = 60
    TOP = 40
    BOTTOM = 50

    def __init__(self, result: Optional[McCabeThieleResult] = None):
        self.result = result

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _setup_coords(self, w: int, h: int) -> None:
        self._x_scale = w - 2.0 * self.MARGIN
        self._y_scale = h - self.TOP - self.BOTTOM
        self._x_off = self.MARGIN
        self._y_off = self.TOP

    def _data_to_pixel(self, x: float, y: float) -> tuple[float, float]:
        px = self._x_off + x * self._x_scale
        py = self._y_off + (1.0 - y) * self._y_scale
        return px, py

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _set_dashed(ctx: cairo.Context, segments: Optional[list[float]] = None) -> None:
        if segments is None:
            segments = [4, 4]
        ctx.set_dash(segments)

    @staticmethod
    def _set_dotted(ctx: cairo.Context, segments: Optional[list[float]] = None) -> None:
        if segments is None:
            segments = [1, 3]
        ctx.set_dash(segments)

    def _draw_line(
        self,
        ctx: cairo.Context,
        x1: float, y1: float,
        x2: float, y2: float,
        r: float, g: float, b: float,
        width: float = 1.0,
    ) -> None:
        px1, py1 = self._data_to_pixel(x1, y1)
        px2, py2 = self._data_to_pixel(x2, y2)
        ctx.set_source_rgb(r, g, b)
        ctx.set_line_width(width)
        ctx.move_to(px1, py1)
        ctx.line_to(px2, py2)
        ctx.stroke()

    def _draw_polyline(
        self,
        ctx: cairo.Context,
        x_array: np.ndarray,
        y_array: np.ndarray,
        r: float, g: float, b: float,
        width: float = 1.0,
        dash: Optional[list[float]] = None,
    ) -> None:
        if len(x_array) < 2:
            return
        ctx.set_source_rgb(r, g, b)
        ctx.set_line_width(width)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        if dash:
            ctx.set_dash(dash)
        else:
            ctx.set_dash([])
        px, py = self._data_to_pixel(float(x_array[0]), float(y_array[0]))
        ctx.move_to(px, py)
        for i in range(1, len(x_array)):
            px, py = self._data_to_pixel(float(x_array[i]), float(y_array[i]))
            ctx.line_to(px, py)
        ctx.stroke()

    def _draw_marker_diamond(
        self,
        ctx: cairo.Context,
        cx: float, cy: float,
        size: float = 6.0,
        r: float = 0.5, g: float = 0.0, b: float = 0.5,
    ) -> None:
        px, py = self._data_to_pixel(cx, cy)
        ctx.set_source_rgb(r, g, b)
        ctx.move_to(px, py - size)
        ctx.line_to(px + size, py)
        ctx.line_to(px, py + size)
        ctx.line_to(px - size, py)
        ctx.close_path()
        ctx.fill()

    def _draw_circle(
        self,
        ctx: cairo.Context,
        cx: float, cy: float,
        radius: float = 3,
        r: float = 0, g: float = 0, b: float = 0,
    ) -> None:
        px, py = self._data_to_pixel(cx, cy)
        ctx.set_source_rgb(r, g, b)
        ctx.arc(px, py, radius, 0, 2 * math.pi)
        ctx.fill()

    def _draw_rect(
        self,
        ctx: cairo.Context,
        x: float, y: float,
        w: float, h: float,
        r: float, g: float, b: float,
        alpha: float = 1.0,
    ) -> None:
        ctx.set_source_rgba(r, g, b, alpha)
        ctx.rectangle(x, y, w, h)
        ctx.fill()

    def _draw_text(
        self,
        ctx: cairo.Context,
        x: float, y: float,
        text: str,
        r: float = 0, g: float = 0, b: float = 0,
        size: float = 10,
        anchor: str = "center",
        rotate: bool = False,
    ) -> None:
        ctx.set_source_rgb(r, g, b)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(size)
        ext = ctx.text_extents(text)

        ctx.save()
        if rotate:
            ctx.translate(x, y)
            ctx.rotate(-math.pi / 2.0)
            ox = -ext.width / 2.0 if anchor == "center" else 0.0
            oy = ext.height / 2.0
            ctx.move_to(ox, oy)
        else:
            if anchor == "center":
                ox = x - ext.width / 2.0
                oy = y + ext.height / 2.0
            elif anchor == "left":
                ox = x
                oy = y + ext.height / 2.0
            elif anchor == "right":
                ox = x - ext.width
                oy = y + ext.height / 2.0
            else:
                ox, oy = x, y
            ctx.move_to(ox, oy)
        ctx.show_text(text)
        ctx.restore()

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------

    def draw(self, ctx: cairo.Context, width: int, height: int) -> None:
        """Render the complete McCabe-Thiele diagram onto *ctx*.

        Parameters
        ----------
        ctx : cairo.Context
            Target Cairo context (from any surface type).
        width, height : int
            Pixel dimensions of the drawing area.
        """
        self._setup_coords(width, height)
        result = self.result

        # ---- 1. Background -------------------------------------------------
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()

        # Shared line-cap / line-join
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        # ---- 3. Grid -------------------------------------------------------
        ctx.set_source_rgba(0.8, 0.8, 0.8, 0.5)
        ctx.set_line_width(0.5)
        ctx.set_dash([])
        for v in range(0, 11):
            val = v / 10.0
            px, py0 = self._data_to_pixel(val, 0.0)
            _, py1 = self._data_to_pixel(val, 1.0)
            ctx.move_to(px, py0)
            ctx.line_to(px, py1)
            ctx.stroke()
            px0, py = self._data_to_pixel(0.0, val)
            px1, _ = self._data_to_pixel(1.0, val)
            ctx.move_to(px0, py)
            ctx.line_to(px1, py)
            ctx.stroke()

        # ---- 4. Axis lines (border rectangle) ------------------------------
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(1.0)
        ctx.set_dash([])
        p00 = self._data_to_pixel(0.0, 0.0)
        p10 = self._data_to_pixel(1.0, 0.0)
        p01 = self._data_to_pixel(0.0, 1.0)
        p11 = self._data_to_pixel(1.0, 1.0)
        ctx.move_to(*p00)
        ctx.line_to(*p10)
        ctx.move_to(*p01)
        ctx.line_to(*p11)
        ctx.move_to(*p00)
        ctx.line_to(*p01)
        ctx.move_to(*p10)
        ctx.line_to(*p11)
        ctx.stroke()

        # ---- 5. Axis labels ------------------------------------------------
        x_center = self._x_off + self._x_scale / 2.0
        y_label = height - 10.0
        self._draw_text(ctx, x_center, y_label, "x (liquid mole fraction)", size=11, anchor="center")
        y_center = self._y_off + self._y_scale / 2.0
        x_label = 14.0
        self._draw_text(ctx, x_label, y_center, "y (vapor mole fraction)", size=11, anchor="center", rotate=True)

        # ---- 6. Diagonal (black dashed) ------------------------------------
        self._set_dashed(ctx)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(0.8)
        p0 = self._data_to_pixel(0.0, 0.0)
        p1 = self._data_to_pixel(1.0, 1.0)
        ctx.move_to(*p0)
        ctx.line_to(*p1)
        ctx.stroke()
        ctx.set_dash([])

        if result is None:
            return  # nothing else to draw

        # ---- 7. Equilibrium curve ------------------------------------------
        self._draw_polyline(
            ctx, result.x_eq, result.y_eq,
            0.0, 0.0, 1.0, width=1.8,
        )

        # ---- 8. Rectifying line --------------------------------------------
        x_r = np.linspace(result.x_intersect, result.xD, 100)
        y_r = result.rectifying_slope * x_r + result.rectifying_intercept
        self._draw_polyline(ctx, x_r, y_r, 1.0, 0.0, 0.0, width=1.5)

        # ---- 9. Stripping line ---------------------------------------------
        x_s = np.linspace(result.xB, result.x_intersect, 100)
        y_s = result.stripping_slope * x_s + result.stripping_intercept
        self._draw_polyline(ctx, x_s, y_s, 0.0, 0.5, 0.0, width=1.5)

        # ---- 10. q-line ----------------------------------------------------
        if result.q_line_x_vertical is not None:
            px, py0 = self._data_to_pixel(result.q_line_x_vertical, 0.0)
            _, py1 = self._data_to_pixel(result.q_line_x_vertical, 1.0)
            self._set_dashed(ctx, [4, 4])
            ctx.set_source_rgb(1.0, 0.65, 0.0)
            ctx.set_line_width(1.2)
            ctx.move_to(px, py0)
            ctx.line_to(px, py1)
            ctx.stroke()
            ctx.set_dash([])
        elif result.q_line_slope is not None:
            x_q = np.linspace(result.xB, result.xD, 100)
            b_q = result.y_intersect - result.q_line_slope * result.x_intersect
            y_q = result.q_line_slope * x_q + b_q
            self._draw_polyline(
                ctx, x_q, y_q,
                1.0, 0.65, 0.0, width=1.2, dash=[4, 4],
            )

        # ---- 11. Stage steps -----------------------------------------------
        sd = result.stage_data
        if len(sd) > 1:
            self._draw_polyline(ctx, sd[:, 0], sd[:, 1], 0, 0, 0, width=0.8)
            for i in range(0, len(sd), 2):
                self._draw_circle(ctx, float(sd[i, 0]), float(sd[i, 1]), radius=2.5, r=0, g=0, b=0)

        # ---- 12. Intersection point ----------------------------------------
        self._draw_marker_diamond(
            ctx, result.x_intersect, result.y_intersect,
            size=6, r=0.5, g=0.0, b=0.5,
        )
        # Annotation text offset to the right and slightly down
        px_int, py_int = self._data_to_pixel(result.x_intersect, result.y_intersect)
        self._draw_text(
            ctx,
            px_int + 10, py_int + 15,
            f"({result.x_intersect:.3f}, {result.y_intersect:.3f})",
            r=0.5, g=0.0, b=0.5,
            size=8, anchor="left",
        )

        # ---- 13. xD / xF / xB markers -------------------------------------
        markers = [
            (result.xD, f"xD={result.xD:.3f}", 1.0, 0.0, 0.0),
            (result.xF, f"xF={result.xF:.3f}", 1.0, 0.65, 0.0),
            (result.xB, f"xB={result.xB:.3f}", 0.0, 0.5, 0.0),
        ]
        label_y_px = self._data_to_pixel(0.0, 0.0)[1] + 6
        for val, label, r, g, b in markers:
            px, _ = self._data_to_pixel(val, 0.0)
            self._set_dotted(ctx)
            ctx.set_source_rgba(r, g, b, 0.5)
            ctx.set_line_width(0.5)
            _, py_top = self._data_to_pixel(val, 1.0)
            ctx.move_to(px, label_y_px + 8)
            ctx.line_to(px, py_top)
            ctx.stroke()
            ctx.set_dash([])
            self._draw_text(
                ctx, px, label_y_px,
                label, r=r, g=g, b=b,
                size=7, anchor="center",
            )

        # ---- 14. Title -----------------------------------------------------
        title = f"McCabe-Thiele Diagram \u2014 N={result.n_stages}  Feed={result.feed_stage}"
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        ext = ctx.text_extents(title)
        title_x = self._x_off + self._x_scale / 2.0
        title_y = 18.0
        self._draw_text(ctx, title_x, title_y, title, size=12, anchor="center")

        # ---- 15. Legend ----------------------------------------------------
        self._draw_legend(ctx, width, height)

    # ------------------------------------------------------------------
    # Legend
    # ------------------------------------------------------------------

    def _draw_legend(self, ctx: cairo.Context, width: int, height: int) -> None:
        result = self.result
        if result is None:
            return

        items: list[tuple[str, tuple[float, float, float], str]] = [
            ("fill", (0.0, 0.0, 1.0), "Equilibrium curve"),
            ("fill", (1.0, 0.0, 0.0), "Rectifying line"),
            ("fill", (0.0, 0.5, 0.0), "Stripping line"),
            ("dash", (1.0, 0.65, 0.0), "q-line"),
            ("diamond", (0.0, 0.0, 0.0), "Stage steps"),
            ("line", (0.0, 0.0, 0.0), "Diagonal y=x"),
        ]

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        line_h = 17.0
        pad_x = 8.0
        pad_y = 6.0
        marker_w = 18.0  # space reserved for the marker

        # Measure the widest label
        max_text_w = 0.0
        for _, _, label in items:
            ext = ctx.text_extents(label)
            if ext.width > max_text_w:
                max_text_w = ext.width

        box_w = marker_w + max_text_w + pad_x * 2
        box_h = len(items) * line_h + pad_y * 2

        # Position: 5 px inset from bottom-right of plot area
        plot_r = self._data_to_pixel(1.0, 0.0)[0]
        plot_b = self._data_to_pixel(0.0, 0.0)[1]
        box_x = plot_r - box_w - 5.0
        box_y = plot_b - box_h - 5.0

        # Legend background (white, slightly transparent)
        self._draw_rect(ctx, box_x, box_y, box_w, box_h, 1, 1, 1, alpha=0.8)

        # Draw each item
        ctx.set_font_size(9)
        for i, (style, color, label) in enumerate(items):
            iy = box_y + pad_y + i * line_h
            mx = box_x + pad_x
            my = iy + line_h / 2.0

            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)

            if style == "fill":
                # Filled rectangle
                self._draw_rect(ctx, mx, my - 5, 10, 10, *color)
            elif style == "dash":
                # Dashed outline rectangle
                ctx.set_dash([3, 3])
                ctx.set_source_rgb(*color)
                ctx.set_line_width(1.2)
                ctx.rectangle(mx, my - 5, 10, 10)
                ctx.stroke()
                ctx.set_dash([])
            elif style == "diamond":
                # Small diamond
                ctx.set_source_rgb(*color)
                ctx.move_to(mx + 5, my - 5)
                ctx.line_to(mx + 10, my)
                ctx.line_to(mx + 5, my + 5)
                ctx.line_to(mx, my)
                ctx.close_path()
                ctx.fill()
            elif style == "line":
                # Short dashed line
                ctx.set_dash([3, 3])
                ctx.set_source_rgb(*color)
                ctx.set_line_width(1.0)
                ctx.move_to(mx, my)
                ctx.line_to(mx + 10, my)
                ctx.stroke()
                ctx.set_dash([])

            # Text label
            tx = mx + marker_w
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(9)
            ctx.set_source_rgb(0, 0, 0)
            ctx.move_to(tx, iy + line_h * 0.65)
            ctx.show_text(label)

    # ------------------------------------------------------------------
    # Export methods
    # ------------------------------------------------------------------

    def export_png(self, path: str, width: int = 1200, height: int = 1000) -> None:
        """Render to a PNG file (width × height in pixels)."""
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        self.draw(ctx, width, height)
        surface.write_to_png(path)
        surface.finish()

    def export_pdf(self, path: str, width: int = 800, height: int = 700) -> None:
        """Render to a PDF file (width × height in points)."""
        surface = cairo.PDFSurface(path, width, height)
        ctx = cairo.Context(surface)
        self.draw(ctx, width, height)
        surface.finish()

    def export_svg(self, path: str, width: int = 800, height: int = 700) -> None:
        """Render to an SVG file."""
        surface = cairo.SVGSurface(path, width, height)
        ctx = cairo.Context(surface)
        self.draw(ctx, width, height)
        surface.finish()
