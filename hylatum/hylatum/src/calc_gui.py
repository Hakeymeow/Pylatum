import math, sys, os
import webview
from hylatum.src import calc


def _sanitize(obj):
    """Replace non-JSON-safe floats (inf, -inf, nan) with None recursively."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, float) and (math.isinf(obj) or math.isnan(obj)):
        return None
    return obj


def get_resource_path(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            return os.path.join(meipass, filename)
    return os.path.join(os.path.dirname(__file__), filename)


def build_html() -> str:
    from plotly.offline import get_plotlyjs

    html_path = get_resource_path("index.html")
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    return html.replace(
        "<!-- PLOTLY_JS -->",
        f"<script>{get_plotlyjs()}</script>",
    )


class Api:
    def calculate(self, R: float, q: float, alpha: float, xD: float, xF: float, xW: float, inf: float) -> dict:
        Rm, n, m = calc.calculate(R, q, alpha, xD, xF, xW, inf)
        return _sanitize({
            "Rm": Rm,
            "Nt": n + m,
            "Nf": n + 1,
            "Nr": n,
            "Ns": m
        })

    def _build_chart_data(self, R, q, alpha, xD, xF, xW) -> tuple[list, dict]:
        """Build Plotly traces and layout. Returns (traces, layout) without sanitization."""
        rl = calc.rectiOpline(R=R, xD=xD)
        ql = calc.qline(q=q, xF=xF)
        sl = calc.striOpline(rl=rl, ql=ql, xW=xW)
        vle = calc.vlEqui(alpha=alpha)
        def linspace(start, end, split):
            return [(end-start)*x/(split-1) for x in range(0, split)]
        x_vals = linspace(0, 1, 100)

        traces = [
            dict(x=x_vals, y=x_vals, mode='lines', name='y=x', line=dict(color='#888888', width=1)),
            dict(x=x_vals, y=[alpha*x/(1+(alpha-1)*x) for x in x_vals], mode='lines', name='Equilibrium', line=dict(color='#e74c3c', width=2)),
            dict(x=x_vals, y=[R/(R+1)*x + xD/(R+1) for x in x_vals], mode='lines', name='Rectifying', line=dict(color='#3498db', width=2)),
            dict(x=x_vals if q != 1 else [xF]*100, y=linspace(0,1,100) if q == 1 else [q/(q-1)*x - xF/(q-1) for x in x_vals], mode='lines', name='q-line', line=dict(color='#f1c40f', width=2)),
        ]

        xi, yi = calc.cross(rl, ql)
        traces.append(dict(x=[xi, xW], y=[yi, xW], mode='lines', name='Stripping', line=dict(color='#27ae60', width=2)))

        stepping_x, stepping_y = [xD], [xD]
        xe, _ = calc.cross(rl, ql)
        xi, yi = vle(xD), xD
        MAX_STEPS = 1000

        while xi > xe:
            if len(stepping_x) > MAX_STEPS * 2:
                break
            stepping_x.append(xi)
            stepping_y.append(yi)
            xj, yj = calc.cross(rl, lambda x, y: x-xi)
            stepping_x.append(xj)
            stepping_y.append(yj)
            xi, yi = vle(yj), yj

        while xi > xW:
            if len(stepping_x) > MAX_STEPS * 2:
                break
            stepping_x.append(xi)
            stepping_y.append(yi)
            xj, yj = calc.cross(sl, lambda x, y: x-xi)
            stepping_x.append(xj)
            stepping_y.append(yj)
            xi, yi = vle(yj), yj
        stepping_x.append(xi)
        stepping_y.append(yi)

        traces.append(dict(x=stepping_x, y=stepping_y, mode='lines', name='Stepping', line=dict(color='#9b59b6', width=1, dash='dash')))

        layout = dict(
            xaxis=dict(range=[0, 1], title=dict(text='x'), constrain='domain'),
            yaxis=dict(range=[0, 1], title=dict(text='y'), scaleanchor='x'),
            width=500, height=500,
            margin=dict(l=40, r=40, t=40, b=40),
            showlegend=True,
            legend=dict(x=1.02, y=1)
        )

        return traces, layout

    def plotly_chart(self, R: float, q: float, alpha: float, xD: float, xF: float, xW: float) -> dict:
        traces, layout = self._build_chart_data(R, q, alpha, xD, xF, xW)
        return _sanitize({"data": traces, "layout": layout})

    def interactive_chart(self, R, q, alpha, xD, xF, xW, inf, param_name, mouse_x, mouse_y) -> dict:
        param_name = param_name.strip().lower()
        xm, ym = mouse_x, mouse_y

        if param_name == 'r':
            if abs(xm - ym) < 1e-12 or xm >= xD or ym <= xm:
                pass  # keep current R
            else:
                derived = (ym - xD) / (xm - ym)
                if derived >= 0:
                    R = derived
        elif param_name == 'q':
            if abs(ym - xm) < 1e-12:
                q = 1.0
            else:
                q = (ym - xF) / (ym - xm)
        elif param_name == 'alpha':
            if xm <= 0 or xm >= 1 or ym <= 0 or ym >= 1:
                pass  # keep current alpha
            else:
                derived = ym * (1 - xm) / (xm * (1 - ym))
                if derived <= 1:
                    alpha = 1.01
                elif 0 < xm < 1 and ym < xm:
                    alpha = 1.01
                else:
                    alpha = derived

        traces, layout = self._build_chart_data(R, q, alpha, xD, xF, xW)
        Rm, n, m = calc.calculate(R, q, alpha, xD, xF, xW, inf)
        result = {"Rm": Rm, "Nt": n + m, "Nf": n + 1, "Nr": n, "Ns": m}
        return _sanitize({
            "data": traces,
            "layout": layout,
            "result": result,
            "params": {"R": R, "q": q, "alpha": alpha}
        })

def main():

    import tempfile, atexit, pathlib

    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.write(build_html())
    tmp.close()
    atexit.register(lambda: os.unlink(tmp.name))

    api = Api()
    webview.create_window(
        "McCabe-Thiele Calculator",
        url=pathlib.Path(tmp.name).as_uri(),
        js_api=api
    )
    webview.start()

if __name__ == "__main__":
    main()
