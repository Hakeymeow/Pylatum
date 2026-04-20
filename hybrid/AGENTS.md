# Hybrid Package

## Project Type
Python distillation column calculator (theoretical plates computation).

## Run Calculator
```bash
cd /home/PomeloFish/Code/PlateNum/hybrid && uv run python calc.py
```
Then input: R, q, ɑ, xD, xF, xW (prompts displayed).

## Python Version
Requires Python 3.14 (check `.python-version`).

## Package Manager
uv workspace. Install deps with `uv sync`. Mirror configured in root `pyproject.toml`.

## Adding Dependencies
Use `uv add <package>` from the `hybrid/` directory to add dependencies.
This automatically updates `pyproject.toml` and the lockfile.

## Testing
No test framework configured yet.

## Key Branch
Active development on `dev-hybrid`.