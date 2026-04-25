# Hybrid Package - McCabe-Thiele Calculator

## Run Commands
```bash
uv run python calc.py           # CLI calculator (prompts for inputs)
uv run hy-gui                   # GUI (pywebview + Plotly)
uv run hy-render                # Manim animation demo
```

## Package Structure
- `calc.py` - Core McCabe-Thiele calculation logic (no validation in CLI)
- `calc_gui.py` - pywebview-based GUI with Plotly chart
- `index.html` - Frontend for pywebview GUI (validates inputs)
- `demo.py` - Manim animation for educational demos

## Parameters (McCabe-Thiele Method)
| Symbol | Name | Typical Range |
|--------|------|---------------|
| R | Reflux Ratio | ≥ 0 |
| q | Feed Thermal Condition | / |
| α | Relative Volatility | > 1 |
| xD | Distillate Composition | > xF |
| xF | Feed Composition | xW < xF < xD |
| xW | Bottoms Composition | < xF |

CLI provides no input validation - user must provide valid values.
GUI validates inputs via HTML min/max attributes.

## Package Manager
uv workspace member. Root pyproject.toml at `/home/PomeloFish/Code/PlateNum`. Mirror: Tsinghua.

```bash
uv sync          # Install dependencies from root
uv add <package> # Add new package from hybrid/
```

## Dependencies
- manim >= 0.20.1 (animation)
- pywebview[gtk] >= 6.2.1 (GUI)
- plotly >= 5.0.0 (charts)
- numpy (implicit via dependencies)

## Python Version
Requires Python >= 3.14

## Workflow
- Do NOT commit changes to git after tasks - wait for explicit user request
- Always work within the current workspace (`/home/PomeloFish/Code/Pylatum/hybrid`) and current git branch. Do not switch to other workspaces or branches unless explicitly instructed.
