import webview
import calc
import numpy as np


class Api:
    def calculate(self, R: float, q: float, alpha: float, xD: float, xF: float, xW: float) -> dict:
        rl = calc.rectiOpline(R=R, xD=xD)
        ql = calc.qline(q=q, xF=xF)
        sl = calc.striOpline(rl=rl, ql=ql, xW=xW)
        vle = calc.vlEqui(alpha=alpha)

        xn, n = calc.rectify(rl=rl, vle=vle, xD=xD, ql=ql)
        xm, m = calc.strip(sl=sl, vle=vle, xj=xn, xW=xW)

        return {
            "Nt": n + m,
            "Nf": n + 1,
            "Nr": n,
            "Ns": m
        }

    def visualization(self, R: float, q: float, alpha: float, xD: float, xF: float, xW: float) -> dict:
        rl = calc.rectiOpline(R=R, xD=xD)
        ql = calc.qline(q=q, xF=xF)
        sl = calc.striOpline(rl=rl, ql=ql, xW=xW)
        vle = calc.vlEqui(alpha=alpha)

        x_vals = np.linspace(0, 1, 100)
        diagonal = [[x, x] for x in x_vals]
        equilibrium = [[x, alpha*x/(1+(alpha-1)*x)] for x in x_vals]
        rectifying = [[x, R/(R+1)*x + xD/(R+1)] for x in x_vals]
        qline_data = [[xF, y] for y in np.linspace(0, 1, 100)] if q == 1 else [[x, q/(q-1)*x - xF/(q-1)] for x in x_vals]

        xi, yi = calc.cross(rl, ql)
        stripping = [[xi, yi], [xW, xW]]

        stepping = []
        xe, _ = calc.cross(rl, ql)
        xi, yi = vle(xD), xD

        while xi > xe:
            stepping.append([xi, yi])
            xj, yj = calc.cross(rl, lambda x, y: x-xi)
            stepping.append([xj, yj])
            xi, yi = vle(yj), yj

        while xi > xW:
            stepping.append([xi, yi])
            xj, yj = calc.cross(sl, lambda x, y: x-xi)
            stepping.append([xj, yj])
            xi, yi = vle(yj), yj
        stepping.append([xi, yi])

        return {
            "diagonal": diagonal,
            "equilibrium": equilibrium,
            "rectifying": rectifying,
            "qline": qline_data,
            "stripping": stripping,
            "stepping": stepping,
            "intersections": {"feed": {"x": xi, "y": yi}, "distillate": {"x": xD, "y": xD}, "bottoms": {"x": xW, "y": xW}},
            "params": {"R": R, "q": q, "alpha": alpha, "xD": xD, "xF": xF, "xW": xW}
        }


if __name__ == "__main__":
    api = Api()
    webview.create_window(
        "McCabe-Thiele Calculator",
        url="index.html",
        js_api=api
    )
    webview.start()