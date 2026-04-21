# Hybrid Package

## Run Commands
```bash
cd /home/PomeloFish/Code/PlateNum/hybrid
uv run python calc.py           # CLI calculator (prompts for inputs)
uv run python gui_webview.py    # GUI (requires X11 display)
ruff check .                    # Lint
```

## Parameters (McCabe-Thiele Method)
| Symbol | Name | Typical Range |
|--------|------|---------------|
| R | Reflux Ratio | ≥ 0 |
| q | Feed Thermal Condition | 0-2 |
| α | Relative Volatility | > 1 |
| xD | Distillate Composition | > xF |
| xF | Feed Composition | xW < xF < xD |
| xW | Bottoms Composition | < xF |

GUI provides input validation; CLI assumes valid inputs.

## Package Manager
uv workspace. Mirror configured in root `pyproject.toml`. Install deps with `uv sync`.

## Adding Dependencies
```bash
cd /home/PomeloFish/Code/PlateNum/hybrid
uv add <package>
```

## Key Branch
Active development on `dev-hybrid`.