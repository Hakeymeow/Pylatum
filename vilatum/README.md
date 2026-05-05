# Vilatum

[**中文版**](README.zh-CN.md)

**McCabe-Thiele Distillation Column Design Tool** — A chemical engineering teaching and design aid for theoretical stage calculation, powered by pure Cairo rendering, developed with pure vibe coding.

Calculates the number of theoretical stages, minimum reflux ratio, and optimal feed location for a distillation column given separation requirements, with a GTK3 desktop application that generates McCabe-Thiele diagrams. No matplotlib — all charts are rendered directly with Cairo.

---

## Features

- **McCabe-Thiele graphical method engine** — vapor-liquid equilibrium curve (relative volatility), rectifying/stripping operating lines, q-line, stage-by-stage construction
- **Minimum reflux ratio** — automatically solves the intersection of q-line and equilibrium curve
- **Minimum stages at total reflux** — Fenske equation verification
- **GTK3 graphical interface** — parameter input, built-in presets, live charting, results display (Chinese UI)
- **Pure Cairo rendering** — no matplotlib dependency; export to PNG / PDF / SVG
- **Calculator mode** — hide the chart for quick parameter iteration

## Chemical Principles

### McCabe-Thiele Method

The McCabe-Thiele method is a graphical technique for determining the number of theoretical stages required for binary distillation. It was developed by Warren L. McCabe and Ernest Thiele in 1925. The method makes two key assumptions:

- **Constant molar overflow** — molar flow rates of liquid and vapor are constant within each section of the column
- **Equimolal heat of vaporization** — each mole of vapor condensed requires the same energy as vaporizing one mole of liquid

### Vapor-Liquid Equilibrium (VLE)

For an ideal binary mixture, the relationship between the vapor composition *y* and liquid composition *x* at equilibrium is given by Raoult's law, expressed through relative volatility *α*:

$$
y = \frac{\alpha x}{1 + (\alpha - 1) x}
$$

where *α* is the relative volatility of the light key component. The equilibrium curve (plotted as *y* vs. *x*) is concave downward for *α* > 1 and coincides with the 45° diagonal when *α* = 1 (no separation possible).

### Operating Lines

The **rectifying section** (above the feed) operating line describes the material balance in the top of the column:

$$
y = \frac{R}{R + 1} x + \frac{x_D}{R + 1}
$$

where *R* is the reflux ratio and *x_D* is the distillate composition.

The **stripping section** (below the feed) operating line describes the bottom of the column:

$$
y = \frac{L'}{L' - W} x - \frac{W x_B}{L' - W}
$$

where *L'* is the liquid flow below the feed, *W* is the bottoms flow, and *x_B* is the bottoms composition.

### q-Line (Feed Line)

The q-line describes the change in liquid and vapor flows at the feed stage:

$$
y = \frac{q}{q - 1} x - \frac{x_F}{q - 1}
$$

The parameter *q* represents the thermal condition of the feed:

| q value | Feed condition |
|---------|---------------|
| q > 1 | Subcooled liquid — more liquid to stripping section |
| q = 1 | Saturated liquid — bubble point |
| 0 < q < 1 | Vapor-liquid mixture |
| q = 0 | Saturated vapor — dew point |
| q < 0 | Superheated vapor — more vapor to rectifying section |

The intersection of the q-line with the equilibrium curve determines the **minimum reflux ratio** *R_min*, the smallest possible reflux that can achieve the desired separation.

### Stage Construction (Stepping Off)

Starting from *x_D* on the diagonal, the graphical construction alternates between:

1. Move horizontally to the operating line (*y* on the operating line)
2. Move vertically to the equilibrium curve (new *x* after equilibrium stage)

Each complete step represents one theoretical stage. The construction ends when *x* falls below *x_B*. The number of steps minus one (subtracting the reboiler if included) is the number of theoretical stages.

### Fenske Equation (Total Reflux)

At total reflux (*R* → ∞), the minimum number of theoretical stages *N_min* is given by the Fenske equation:

$$
N_{\min} = \frac{\log\left[\frac{x_D}{1 - x_D} \cdot \frac{1 - x_B}{x_B}\right]}{\log \alpha}
$$

This provides an upper bound check: the actual stages at a finite reflux ratio will always exceed *N_min*.

## Quick Start

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt install libgtk-3-dev libcairo2-dev libglib2.0-dev \
                 libgirepository1.0-dev libpango1.0-dev
```

### Installation & Running

```bash
# Using uv (recommended)
uv sync
uv run vi-gui

# Or using pip
pip install -e .
vi-gui
```

> Without a display server, use `xvfb-run uv run vi-gui` for headless operation.

## Usage

### GUI Mode

The interface consists of a left-side parameter panel and a right-side McCabe-Thiele chart:

1. Enter operating parameters: feed composition xF, distillate composition xD, bottoms composition xB, reflux ratio R, feed thermal condition q, relative volatility α
2. Select a **preset case** to quickly fill parameters (Benzene-Toluene, Ethanol-Water, Methanol-Water, Acetone-Benzene)
3. Click **Calculate** or press `Enter` to execute
4. Toggle chart visibility from the **View** menu (calculator mode)
5. Export from **File → Export** or `Ctrl+E` as PNG / PDF / SVG

### Programmatic Usage

```python
from vilatum.distillation import McCabeThiele, CairoPlotter

# Create calculator (benzene-toluene system)
calc = McCabeThiele(xF=0.45, xD=0.97, xB=0.02, R=2.0, q=1.0, alpha=2.50)
result = calc.calculate()

print(f"Theoretical stages N = {result.n_stages}")
print(f"Rectifying stages = {result.n_rectifying}")
print(f"Stripping stages = {result.n_stripping}")
print(f"Optimal feed stage = {result.feed_stage}")
print(f"Minimum reflux ratio R_min = {result.r_min:.4f}")
print(f"Minimum stages N_min = {result.n_min}")

# Export chart
plotter = CairoPlotter(result)
plotter.export_png("mccabe-thiele.png")
plotter.export_pdf("mccabe-thiele.pdf")
plotter.export_svg("mccabe-thiele.svg")
```

## Package Structure

```
vilatum/
├── pyproject.toml
├── src/vilatum/
│   ├── __init__.py
│   └── distillation/
│       ├── __init__.py    # exports McCabeThiele, McCabeThieleResult, CairoPlotter
│       ├── core.py        # McCabe-Thiele calculation engine
│       ├── gui.py         # GTK3 desktop application
│       └── plotter.py     # Pure Cairo renderer
└── tests/
    ├── conftest.py        # shared test fixtures
    ├── test_plotter.py    # plotter tests (pixel-level assertions)
    └── test_gui.py        # GUI smoke tests
```

## API Reference

### `McCabeThiele`

Parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `xF` | float | Feed mole fraction of light key (0 < xF < 1) |
| `xD` | float | Distillate mole fraction (xF < xD < 1) |
| `xB` | float | Bottoms mole fraction (0 < xB < xF) |
| `R` | float | Actual reflux ratio (> 0) |
| `q` | float | Feed thermal condition |
| `alpha` | float | Relative volatility (> 1) |
| `n_eq_points` | int | Equilibrium curve discretization points (default 1001) |

Feed thermal condition (q):

| q value | Meaning |
|---------|---------|
| q > 1 | Subcooled liquid |
| q = 1 | Saturated liquid |
| 0 < q < 1 | Vapor-liquid mixture |
| q = 0 | Saturated vapor |
| q < 0 | Superheated vapor |

### `McCabeThieleResult`

Result dataclass containing all computed values: stage counts, operating line parameters, stage coordinates, intersection points, and convergence status.

### `CairoPlotter`

| Method | Description |
|--------|-------------|
| `draw(ctx, width, height)` | Render onto any Cairo Context |
| `export_png(path, width, height)` | Export as PNG |
| `export_pdf(path, width, height)` | Export as PDF |
| `export_svg(path, width, height)` | Export as SVG |

## Testing

```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest vilatum/tests/test_plotter.py

# Run GUI tests (requires display)
xvfb-run uv run pytest vilatum/tests/test_gui.py
```

## Tech Stack

| Aspect | Details |
|--------|---------|
| Python | >= 3.13 |
| Package manager | uv |
| Build system | setuptools >= 75 |
| Runtime deps | numpy >= 2.0, PyGObject >= 3.56.2 (with PyCairo) |
| Dev deps | pytest >= 9.0.3 |
| Graphics backend | Cairo (no matplotlib) |
| GUI framework | GTK3 (PyGObject) |

## License

[MIT](../LICENSE)

---

## Record of Sessions
- [[/init#1]](https://opncd.ai/share/G9PLazNs): Set basic rules for agents.
- [[implementation]](https://opncd.ai/share/ZK85qRaR): Implemented the calculation program with pure vibe coding.
- [[feat: optional chart#1]](https://opncd.ai/share/rYakUmXb): Tell the agent to make the chart expansible but it seems to misunderstand. 
- [[feat: optional chart#2]](https://opncd.ai/share/hN0h1xHE): Fork the previous session and use the word "optional" instead of "expansible" in prompt.
- [[/init#2]](https://opncd.ai/share/eE9OggzI): Update AGENTS.md after implementation.
