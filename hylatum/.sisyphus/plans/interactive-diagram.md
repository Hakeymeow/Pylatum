# Plan: Interactive Diagram — Mouse-Driven Parameter Variation

## TL;DR

> **Summary**: Add a toggle to switch between the current static McCabe-Thiele diagram and a new interactive mode where a parameter varies with mouse position over the chart.
>
> **Deliverables**:
> - `calc_gui.py` — new `Api.interactive_chart()` endpoint
> - `index.html` — toggle switch, TAB cycling, mousemove → parameter derivation → chart update
> - `calc.py` — no changes needed (all functions are pure/stateless, reused as-is)
>
> **Estimate**: Medium | **Parallel**: No (sequential file changes)

---

## Requirements

1. **Toggle**: User can switch between current static diagram and interactive mode
2. **Mouse control**: A specific parameter varies based on mouse x,y position over the diagram
3. **TAB cycling**: In interactive mode, TAB key cycles through which parameter is mouse-controlled
4. **Line-through-cursor**: The line/curve associated with the active parameter is constrained to pass through the mouse cursor position

---

## Design

### Mode toggle
- A toggle button/switch in the UI: "Static" ↔ "Interactive"
- Default: Static (current behavior preserved, no change)
- When switching to Interactive: the last static calculation's parameters carry over

### Parameters to cycle (TAB order)

| # | Parameter | Line/Curve | Derivation from mouse (xₘ, yₘ) | Constraint |
|---|-----------|-----------|-------------------------------|-----------|
| 1 | **R** (Reflux Ratio) | Rectifying operating line | `R = (yₘ − xD) / (xₘ − yₘ)` | Line passes through (xD, xD) and (xₘ, yₘ) |
| 2 | **q** (Feed Condition) | q-line | `q = (yₘ − xF) / (yₘ − xₘ)` | Line passes through (xF, xF) and (xₘ, yₘ) |
| 3 | **α** (Relative Volatility) | Equilibrium curve | `α = yₘ·(1−xₘ) / (xₘ·(1−yₘ))` | Curve passes through (xₘ, yₘ) |

TAB cycles forward (R → q → α → R → ...). Shift+TAB cycles backward.

### Interactive data flow

```
Mouse move on chart
       │
       ▼
DOM mousemove handler
  → read pixel (px, py)
  → Plotly axis inverse: (xₘ, yₘ) = p2d(px), p2d(py)
  → clamp to [0, 1] × [0, 1]
       │
       ▼
JavaScript derives new parameter value from (xₘ, yₘ)
  (simple formula, O(1), no bridge needed for this step)
       │
       ▼
Throttled call (≈100ms) → pywebview.api.interactive_chart(
    {param_name, param_value, R, q, alpha, xD, xF, xW}
  )
       │
       ▼
Python recalculates:
  1. Override the active parameter with the new value
  2. Call existing calc functions to generate all traces
  3. Run calculate() to get Rm, Nt, Nf
  4. Return trace data + derived value + calculation result
       │
       ▼
JavaScript → Plotly.react() to update chart
           → update display badge ("R = 2.34")
           → optionally highlight the controlled line
```

### Visual feedback in interactive mode

- **Badge** showing current parameter name + value (e.g., `"R = 2.34"`, `"q = 0.85"`, `"α = 3.12"`)
- **Active line/curve is highlighted** (thicker stroke, brighter color, slight glow or opacity difference)
- **Result panel** updates with current plate count (or shows "∞" when R < Rmin)
- **Warning indicator** when the current configuration is invalid (e.g., R < Rmin → tooltip "Below minimum reflux")

### Edge cases

| Condition | Behavior |
|-----------|----------|
| Mouse at exactly (xD, xD) or (xF, xF) | Keep current R/q value (no division by zero) |
| Mouse near diagonal (yₘ ≈ xₘ) in R or α mode | Keep current parameter value within a small dead zone around the diagonal |
| α derivation gives α ≤ 1 | Clamp to 1.01 minimum |
| Mouse outside [0,1]×[0,1] | Ignore (no update) |
| Derived R < Rmin | Still draw all lines but stepping may produce inf — show warning |
| Stepping produces inf plates | Show "∞" in plate count, draw diagram without stepping trace |
| Rapid mouse movement | Throttle to one bridge call per 100ms; intermediate positions use last valid call |
| Invisible hover area (empty chart regions) | Use DOM mousemove + axis inversion, not plotly_hover — covers entire chart area |

---

## Files to modify

### 1. `calc_gui.py` — New interactive endpoint

**Changes**:
- Add `Api.interactive_chart(param_name, mouse_x, mouse_y, R, q, alpha, xD, xF, xW, inf)` method
  - Derive the active parameter value from (mouse_x, mouse_y) using the formulas above
  - Clamp/validate the derived value
  - Override the active parameter in the parameter list
  - Call the existing calc functions to generate traces (mirrors `plotly_chart` logic but with derived param)
  - Call `calc.calculate()` for plate count
  - Return: `{data: traces, layout, param_name, param_value, result: {Rm, Nt, Nf, Nr, Ns}}`
- Pipeline: parameter derivation is done in Python too (defense-in-depth — JS sends raw mouse coords, Python re-derives and validates)

### 2. `index.html` — Frontend interactive mode

**Changes**:
- **CSS**: Add styles for:
  - Mode toggle switch (static/interactive)
  - Interactive mode badge (parameter name + value)
  - Active line highlight indicator
- **HTML**: Add:
  - Toggle button/switch above or next to "Calculate" button
  - Badge display element (hidden in static mode)
- **JavaScript**: Add:
  - Mode state variable (`isInteractive`) + active parameter tracking
  - `mousemove` event handler on the chart div with Plotly axis inversion
  - Parameter derivation functions (R, q, α from mouse coordinates)
  - TAB/Shift+TAB keydown handler (only when interactive mode is active)
  - Throttled bridge call + `Plotly.react` update
  - Toggle switch handler (transition between modes)
  - Highlight styling for the active trace

---

## Work Breakdown

### Wave 1: Python backend (calc_gui.py)

- [x] Add `Api.interactive_chart()` method
  - Parameter derivation from mouse position with validation/clamping
  - Call existing calc functions for all traces
  - Return combined chart data + result

### Wave 2: Frontend interactive mode (index.html)

- [x] Add toggle switch UI (CSS + HTML)
- [x] Add interactive mode state management (JS)
- [x] Implement mousemove → parameter derivation → throttled bridge call
- [x] Implement TAB cycling of active parameter
- [x] Implement chart update via `Plotly.react`
- [x] Parameter badge + active line highlighting

### Wave 3: Edge cases & polish

- [x] Clamp/validity guards for all parameter derivations
- [x] Throttle/debounce tuning
- [x] Warning display for invalid configurations (R < Rmin, α ≤ 1, etc.)
- [x] Visual polish: active line styling, smooth transitions

---

## Key technical decisions

1. **Use DOM `mousemove` not `plotly_hover`**: We need the mouse position everywhere on the chart (not only near data traces). Use `gd._fullLayout.xaxis.p2d()` / `yaxis.p2d()` for pixel-to-data conversion — these are stable internal APIs widely used in Plotly.js extensions.

2. **Derive parameter in JavaScript first** (for immediate local feedback) but **also re-derive in Python** (for security/correctness as the authoritative source). JS computes the formula, sends raw mouse coords + intended param name to Python. Python re-derives and validates.

3. **Reuse `plotly_chart` trace-generation logic** by extracting it into a shared helper function. `interactive_chart` calls the same helper after overridding the active parameter. No duplication.

4. **Single bridge call per update**: Return both chart data and calculation result in one response to minimize round-trips.

5. **Throttle at 100ms**: Empirical starting point. Provides ~10fps update rate. Can be tuned — the bottleneck is JSON serialization of trace arrays, not the calc logic (~microseconds).

---

## Non-goals (out of scope)

- No changes to `calc.py` (pure math stays untouched)
- No new Python dependencies
- No performance optimizations beyond throttling (trace JSON size is <10KB, fine for 10fps)
- No animation/smooth transitions between parameter changes (instant snap is acceptable for v1)
- No plotly_hover tooltip customization (default Plotly hover behavior preserved)

---

## Success criteria

- [x] Toggle switch works: static mode unchanged, interactive mode activates
- [x] In R mode: rectifying line always passes through mouse cursor; R value updates
- [x] In q mode: q-line always passes through mouse cursor; q value updates
- [x] in α mode: equilibrium curve always passes through mouse cursor; α value updates
- [x] TAB cycles active parameter (R → q → α → R...), Shift+TAB reverses
- [x] Chart is responsive at ~10fps during mouse movement
- [x] Edge cases handled: diagonal proximity, α ≤ 1, x/y out of bounds, R < Rmin
- [x] No crashes when switching modes, rapid mouse movement, or extreme parameter values
