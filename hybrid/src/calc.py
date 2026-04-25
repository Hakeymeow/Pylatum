from typing import Callable
plane = Callable[[float, float], float]
line = Callable[[float], float]

def cross(l1: plane, l2: plane) -> tuple[float, float]:
    c1, c2 = l1(0, 0), l2(0, 0)
    a1, a2 = l1(1, 0) - c1, l2(1, 0) - c2
    b1, b2 = l1(0, 1) - c1, l2(0, 1) - c2
    return (
        (c2 * b1 - c1 * b2) / (a1 * b2 - a2 * b1),
        (c2 * a1 - c1 * a2) / (b1 * a2 - b2 * a1)
    )

def rectiOpline(R: float, xD: float) -> plane:
    return lambda x, y: R * x - (R+1) * y + xD

def qline(q: float, xF: float) -> plane:
    return lambda x, y: q * x - (q-1) * y - xF

def striOpline(rl: plane, ql: plane, xW: float) -> plane:
    xi, yi = cross(rl, ql)
    return lambda x, y: (yi-xW) * (x-xW) - (xi-xW) * (y-xW)

def vlEqui(alpha: float) -> line:
    return lambda y: y / (alpha - (alpha-1) * y)

def rectify(rl: plane, vle: line, ql: plane) -> tuple[float, int]:
    xe, _ = cross(rl, ql)
    xj, i = vle(rl(0, 0)), 0
    while xj > xe:
        i += 1
        _, yj = cross(rl, lambda x, y: x-xj)
        xj = vle(yj)
    return (xj, i)

def strip(sl: plane, vle: line, xj: float) -> tuple[float, int]:
    xW, _ = cross(sl, lambda x, y: x-y)
    i = 0
    while xj > xW:
        i += 1
        _, yj = cross(sl, lambda x, y: x-xj)
        xj = vle(yj)
    return (xj, i)



if __name__ == "__main__":

    inputFloat = lambda name: float(input(f"{name} = "))
    R, q, alpha = inputFloat("R"), inputFloat("q"), inputFloat("ɑ")
    xD, xF, xW = inputFloat("xD"), inputFloat("xF"), inputFloat("xW")

    rl = rectiOpline(R=R, xD=xD)
    ql = qline(q=q, xF=xF)
    sl = striOpline(rl=rl, ql=ql, xW=xW)
    vle = vlEqui(alpha=alpha)

    xn, n = rectify(rl=rl, vle=vle, ql=ql)
    xm, m = strip(sl=sl, vle=vle, xj=xn)
    print(f"Nt = {n+m}\t\t(Total Number of Theoretical Plates)")
    print(f"Nf = {n+1}\t\t(Feed Plate Location)")
    print(f"Nr = {n}\t\t(Number of Plates in Rectifying Section)")
    print(f"Ns = {m}\t\t(Number of Plates in Stripping Section Including Reboiler)")
