# Hylatum - McCabe-Thiele Calculator

## Run Commands
```bash
uv run hy-cli       # CLI calculator (stdlib only)
uv run hy-gui       # GUI (pywebview + Plotly, inline Plotly JS)
uv run hy-render    # Manim animation demo
uv run hy-build -g  # Build GUI standalone binary (Nuitka onefile)
uv run hy-build -c  # Build CLI standalone binary
uv run python hylatum/src/plot.py  # R vs. stages plot (matplotlib, NOT registered as entrypoint)
```

## Source Layout
```
hylatum/
├── hylatum/
│   ├── __init__.py
│   └── src/
│       ├── calc.py       # Core algorithm — pure Python, zero third-party deps
│       ├── calc_gui.py   # pywebview GUI, exposes Api to JS bridge
│       ├── demo.py       # Manim scenes: Draw (step-by-step), Vary (R sweep)
│       ├── build.py      # Nuitka onefile builder (uses isolated temp venv)
│       ├── plot.py       # Matplotlib R vs. stages analysis (not in entrypoints)
│       └── index.html    # GUI frontend (inline CSS/JS, no external files)
├── AGENTS.md
├── pyproject.toml
└── README.md
```

## Entrypoints
All registered in `[project.scripts]` in both root and member `pyproject.toml`:
- `hy-cli` = `hylatum.src.calc:main` — 7 args: `--R`, `--q`, `--alpha`, `--xD`, `--xF`, `--xW`, `--inf`
- `hy-gui` = `hylatum.src.calc_gui:main`
- `hy-build` = `hylatum.src.build:main` — flags: `--cli`, `--gui`
- `hy-render` = `hylatum.src.demo:main` — flag: `--demo {draw, vary}`

## Dependencies
| Group | Packages | Used By |
|-------|----------|---------|
| runtime | `pywebview[gtk]`, `plotly` | calc_gui.py, index.html |
| dev | `manim`, `matplotlib` | demo.py, plot.py |
| build | `nuitka[onefile]` | build.py |

`calc.py` has **zero** third-party dependencies — pure Python 3.14+ stdlib.
Install via: `uv sync` (runtime), `uv sync --group dev` (+dev), `uv sync --group build` (+build).

## Package Manager
uv workspace member (single member: `hylatum`). Root at `/home/PomeloFish/Code/Pylatum`.
Mirror: Tsinghua (`[[tool.uv.index]]` in root `pyproject.toml`).

## Python Version
Requires Python >= 3.14. Set in `.python-version` and both `pyproject.toml`.

## McCabe-Thiele Parameters
| Symbol | Name | Validation |
|--------|------|-----------|
| R | Reflux Ratio | >= 0 |
| q | Feed Thermal Condition | any float |
| α | Relative Volatility | > 1 |
| xD | Distillate Composition | > xF |
| xF | Feed Composition | xW < xF < xD |
| xW | Bottoms Composition | < xF |

CLI provides no input validation (user provides valid values). GUI validates via HTML `min`/`max` attributes.

## Architecture Notes
- All operating lines and q-line use implicit form `ax + by + c = 0` to avoid `ZeroDivisionError` at edge cases (e.g., q=1).
- `calc.py` functions are **stateless** — each call is independent. No classes, no global state.
- GUI wiring: `index.html` ↔ pywebview JS bridge ↔ `calc_gui.py:Api` ↔ `calc.py`. Plotly JS injected inline via `plotly.offline.get_plotlyjs()` for offline capability.
- Build script creates an **isolated temp venv** each run (not the project venv), installs the package + Nuitka, then compiles a onefile binary.
- No tests directory exists. No CI pipeline configured. No linters/formatters configured.

## Workflow
- Do NOT commit changes to git after tasks — wait for explicit user request.
- Do NOT switch workspaces or branches unless explicitly instructed.
- All uv commands run from root `/home/PomeloFish/Code/Pylatum`.
- Commit format: `<type>(<scope>): <description>` where scope prefixes always include `hyv-`. Do not follow the scope patterns in repository history.
