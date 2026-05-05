# Pylatum

A learning project for calculating the number of theoretical plates in binary distillation columns, with subprojects developed in different ways, driven by my homework.

- [`hylatum`](./hylatum/README.md): A hybrid subproject of artificial coding and vibe coding. I preferred functional programming and developed a simple core by myself. The GUI is developed with vibe coding.
- [`vilatum`](./vilatum/README.md): A subproject developed with pure vibe coding. I was not sure whether artificial coding is permitted in my homework so I added this subproject.

<video controls src="https://github.com/Hakeymeow/Pylatum/releases/download/v0.0.0/Draw.mp4" title="Title" width="500"></video>

## Capabilities at a Glance

| What you can do | [hylatum]((./hylatum/README.md)) | [vilatum](./vilatum/README.md) |
|---|---|---|
| **Calculate theoretical stages** | ❯ CLI + GUI | ❯ GTK3 desktop app |
| **View McCabe-Thiele diagram** | Plotly interactive chart | Pure Cairo rendering (no matplotlib) |
| **Export chart** | Supproted by Plotly | PNG / PDF / SVG |
| **Use without installation** | Pre-built standalone binaries | — |
| **Watch step-by-step animation** | Manim educational demo | — |
| **Use programmatically as a library** | ✅ Stateless functions | ✅ Object-oriented engine |
| **Test coverage** | — | ✅ pytest with pixel-level assertions |

## Quick Start

### From Binaries
Pre-built binaries of hylatum are available from the [release](https://github.com/Hakeymeow/Pylatum/releases/latest). No python and uv required.

### From Source Code
```bash
# Prerequisites: Python >= 3.13, uv
uv sync --all-packages

# hylatum CLI (stdlib only, no extra deps needed)
uv run hy-cli --R 2.0 --q 1.0 --alpha 2.5 --xD 0.97 --xF 0.45 --xW 0.02

# hylatum GUI (interactive Plotly chart in webview)
uv run hy-gui

# hylatum Manim animation demo
# install manim from `demo` group
uv sync --all-packages --group demo
uv run hy-render

# vilatum GUI (native GTK3 app with Cairo rendering)
uv run vi-gui
```

## Project Structure

```
Pylatum/
├── hylatum/                                # Hybrid development (hand-written core + vibe-coded GUI)
│   ├── hylatum/src/calc.py                 # Core algorithm — zero third-party dependencies
│   ├── hylatum/src/calc_gui.py             # pywebview desktop application
│   ├── hylatum/src/demo.py                 # Manim educational animation
│   └── hylatum/src/build.py                # Nuitka onefile binary builder
├── vilatum/                                # Pure vibe coding (AI-generated end-to-end)
│   ├── src/vilatum/distillation/core.py    # McCabe-Thiele calculation engine
│   ├── src/vilatum/distillation/gui.py     # GTK3 desktop application
│   ├── src/vilatum/distillation/plotter.py # Pure Cairo renderer
│   └── tests/                              # pytest suite with pixel-level assertions
├── pyproject.toml   # uv workspace root
└── README.md
```

---

## License
[MIT](./LICENSE)
