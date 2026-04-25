import webview
import calc
import numpy as np
import sys
import os


def get_resource_path(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            return os.path.join(meipass, filename)
    return os.path.join(os.path.dirname(__file__), filename)


class Api:
    def calculate(self, R: float, q: float, alpha: float, xD: float, xF: float, xW: float) -> dict:
        Rm, n, m = calc.calculate(R, q, alpha, xD, xF, xW)
        return {
            "Rm": Rm,
            "Nt": n + m,
            "Nf": n + 1,
            "Nr": n,
            "Ns": m
        }

    def plotly_chart(self, R: float, q: float, alpha: float, xD: float, xF: float, xW: float) -> dict:
        rl = calc.rectiOpline(R=R, xD=xD)
        ql = calc.qline(q=q, xF=xF)
        sl = calc.striOpline(rl=rl, ql=ql, xW=xW)
        vle = calc.vlEqui(alpha=alpha)

        x_vals = list(np.linspace(0, 1, 100))

        traces = [
            dict(x=x_vals, y=x_vals, mode='lines', name='y=x', line=dict(color='#888888', width=1)),
            dict(x=x_vals, y=[alpha*x/(1+(alpha-1)*x) for x in x_vals], mode='lines', name='Equilibrium', line=dict(color='#e74c3c', width=2)),
            dict(x=x_vals, y=[R/(R+1)*x + xD/(R+1) for x in x_vals], mode='lines', name='Rectifying', line=dict(color='#3498db', width=2)),
            dict(x=x_vals if q != 1 else [xF]*100, y=np.linspace(0,1,100).tolist() if q == 1 else [q/(q-1)*x - xF/(q-1) for x in x_vals], mode='lines', name='q-line', line=dict(color='#f1c40f', width=2)),
        ]

        xi, yi = calc.cross(rl, ql)
        traces.append(dict(x=[xi, xW], y=[yi, xW], mode='lines', name='Stripping', line=dict(color='#27ae60', width=2)))

        stepping_x, stepping_y = [xD], [xD]
        xe, _ = calc.cross(rl, ql)
        xi, yi = vle(xD), xD

        while xi > xe:
            stepping_x.append(xi)
            stepping_y.append(yi)
            xj, yj = calc.cross(rl, lambda x, y: x-xi)
            stepping_x.append(xj)
            stepping_y.append(yj)
            xi, yi = vle(yj), yj

        while xi > xW:
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

        return {"data": traces, "layout": layout}

def main():
    api = Api()
    webview.create_window(
        "McCabe-Thiele Calculator",
        url=get_resource_path("index.html"),
        js_api=api
    )
    webview.start()

if __name__ == "__main__":
    main()
