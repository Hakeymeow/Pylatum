# Interactive Diagram — Wave 1 Learnings

## Parameter Derivation Formulas (from mouse_x, mouse_y)

| param_name | Formula | Constraints |
|-----------|---------|-------------|
| `R` | `R = (ym - xD) / (xm - ym)` | `\|xm - ym\| > 1e-12`, `xm < xD`, `ym > xm`, result >= 0 |
| `q` | `q = (ym - xF) / (ym - xm)` | `\|ym - xm\| > 1e-12` else q=1.0 |
| `alpha` | `α = ym·(1-xm) / (xm·(1-ym))` | `0 < xm < 1`, `0 < ym < 1`, result > 1; clamp to 1.01 min |

## Edge Case Handling

### R mode
- `abs(xm - ym) < 1e-12`: keep current R (division by zero guard)
- `xm >= xD`: keep current R (point is at or beyond distillate composition)
- `ym <= xm`: keep current R (point is below the diagonal — reflux would be undefined/negative)
- `derived < 0`: keep current R (negative reflux is unphysical)

### q mode
- `abs(ym - xm) < 1e-12`: set q = 1.0 (saturated liquid — vertical q-line)
- Otherwise: `q = (ym - xF) / (ym - xm)` — no clamping needed, q can be any float

### alpha mode
- `xm <= 0 or xm >= 1 or ym <= 0 or ym >= 1`: keep current alpha (unphysical compositions)
- If `xm` and `ym` are in `(0,1)`:
  - `derived = ym * (1 - xm) / (xm * (1 - ym))`
  - `derived <= 1`: clamp to 1.01 (no separation possible at or below equilibrium)
  - `ym < xm` (below diagonal): clamp to 1.01 (implies alpha < 1)
- Note: `ym < xm` and `0 < xm < 1` implies `derived < 1`, so the diagonal check is a subset of the `<= 1` check

## Architecture

- `_build_chart_data(R, q, alpha, xD, xF, xW)` → `(traces, layout)` — extracted from `plotly_chart()`, no sanitization
- `plotly_chart(...)` → delegates to `_build_chart_data()` then `_sanitize()` — backward compatible
- `interactive_chart(...)` derives parameter from mouse, overrides local var, calls both `_build_chart_data()` and `calc.calculate()`, returns merged dict with `data`, `layout`, `result`, `params`
- Case-insensitive `param_name` matching via `.strip().lower()`
- All operating lines use implicit `ax + by + c = 0` form (calc.py convention)
- `calc.calculate()` returns `inf` stages when `R < Rmin` — this propagates through `_sanitize()` to become `None` in JSON

## Infinite Loop Fix — Stepping Iteration Limits (Wave 1.3)

### Root Cause
When R < Rmin (e.g., R=0.85 with Rmin≈1.35):
- The rectifying operating line is too flat, crossing the equilibrium curve above the feed point
- Below the crossing, the operating line is ABOVE the equilibrium curve
- Vertical equilibrium→operating-line moves go UP instead of DOWN
- `xi` oscillates around the crossing point — neither decreases below `xe` nor exceeds it
- Both `while xi > xe` and `while xi > xW` loops run forever

### Fix
- Added `MAX_STEPS = 1000` before the stepping loops
- Both loops now guard with `if len(stepping_x) > MAX_STEPS * 2: break`
- The `* 2` factor accounts for each step iteration adding 2 points (x and y)
- When the limit is hit, the stepping trace simply shows partial steps
- Non-stepping traces (y=x, Equilibrium, Rectifying, q-line, Stripping) remain unaffected
- `calc.calculate()` already handles R < Rmin by returning `(Rm, inf, inf)` — this fix only affects the chart rendering

### Verification
- `interactive_chart(2.0, 1.0, 2.5, 0.97, 0.45, 0.02, 65536, 'R', 0.6, 0.8)` — no hang
- `_build_chart_data(2.0, 1.0, 2.5, 0.97, 0.45, 0.02)` — normal convergence (R > Rmin, <100 plates)
- MAX_STEPS = 1000 is generous (typical columns have <100 plates)
