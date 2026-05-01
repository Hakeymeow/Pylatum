"""Test fixtures and helpers for vibe-omo tests."""

import struct
import numpy as np
import cairo
import pytest

from vibe_omo.distillation.core import McCabeThiele, McCabeThieleResult


# We can't import CairoPlotter in conftest (circular dependency risk),
# so we provide fixtures that the test files will use directly.


@pytest.fixture
def result_benzene_toluene() -> McCabeThieleResult:
    """Default benzene-toluene case result."""
    calc = McCabeThiele(xF=0.45, xD=0.97, xB=0.02, R=2.0, q=1.0, alpha=2.50)
    return calc.calculate()


@pytest.fixture
def result_ethanol_water() -> McCabeThieleResult:
    """Ethanol-water case result."""
    calc = McCabeThiele(xF=0.30, xD=0.85, xB=0.05, R=3.0, q=1.0, alpha=2.21)
    return calc.calculate()


@pytest.fixture
def result_q_lt_1() -> McCabeThieleResult:
    """Case with q < 1 (vapor-liquid mixture) to test sloped q-line."""
    # Acetone-Benzene with q=1.2 (actually q>1), let's use q=0.5 for sloped q-line
    calc = McCabeThiele(xF=0.45, xD=0.90, xB=0.05, R=2.5, q=0.5, alpha=2.10)
    return calc.calculate()


@pytest.fixture
def render_surface():
    """Factory fixture: returns a function that renders a CairoPlotter to ImageSurface.

    Usage:
        surface = render_surface(plotter, width=800, height=700)
    """
    def _render(plotter, width=800, height=700):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        plotter.draw(ctx, width, height)
        return surface
    return _render


def pixel_eq(surface: cairo.ImageSurface, x: int, y: int,
             r: float, g: float, b: float, tol: int = 30) -> bool:
    """Check if pixel at (x,y) approximately equals (r,g,b) color [0-255].

    Cairo ImageSurface uses ARGB32 format stored as BGRA in memory.
    """
    if x < 0 or y < 0 or x >= surface.get_width() or y >= surface.get_height():
        return False
    data = surface.get_data()
    stride = surface.get_stride()
    offset = y * stride + x * 4
    # Cairo FORMAT_ARGB32 stores bytes as B, G, B, A in memory (little-endian)
    b_actual = data[offset]
    g_actual = data[offset + 1]
    r_actual = data[offset + 2]
    return (abs(r_actual - r) <= tol and
            abs(g_actual - g) <= tol and
            abs(b_actual - b) <= tol)


def pixel_at(surface: cairo.ImageSurface, x: int, y: int) -> tuple:
    """Get RGB values [0-255] of pixel at (x, y)."""
    data = surface.get_data()
    stride = surface.get_stride()
    offset = y * stride + x * 4
    return (data[offset + 2], data[offset + 1], data[offset])
