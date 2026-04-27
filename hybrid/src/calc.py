import math, sys
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

def minR(alpha: float, xD: float, q: float, xF: float) -> float:
    if q == 1:
        x, y = xF, alpha * xF / (1+(alpha-1)*xF)
    else:
        a, b, c = (alpha-1) * q, alpha * (1-q-xF), -xF
        x = (math.sqrt(b*b-4*a*c) - b) / 2*a
        y = alpha * x / (1+(alpha-1)*x)
    return (xD-y) / (y-x)

def rectify(rl: plane, vle: line, ql: plane, inf: int, noisy: bool = False) -> tuple[float, int|float]:
    xe, _ = cross(rl, ql)
    xj, i = vle(rl(0, 0)), 0
    while xj > xe:
        i += 1
        _, yj = cross(rl, lambda x, y: x-xj)
        xj = vle(yj)
        if noisy:
            print(f"{f"\rRectifying: {i}":<48}", end='')
        if i > inf:
            return (0, float('inf'))
    return (xj, i)

def strip(sl: plane, vle: line, xj: float, noisy: bool = False) -> tuple[float, int]:
    xW, _ = cross(sl, lambda x, y: x-y)
    i = 0
    while xj > xW:
        i += 1
        _, yj = cross(sl, lambda x, y: x-xj)
        xj = vle(yj)
        if noisy:
            print(f"{f"\rStripping: {i}":<48}", end='')
    return (xj, i)

def calculate(R: float, q: float, alpha: float, xD: float, xF: float, xW: float, inf: int, noisy: bool = False) -> tuple[float, float, float]:
    Rm = minR(alpha, xD, q, xF)
    if R < minR(alpha, xD, q, xF):
        return (Rm, float('inf'), float('inf'))
    rl = rectiOpline(R=R, xD=xD)
    ql = qline(q=q, xF=xF)
    sl = striOpline(rl=rl, ql=ql, xW=xW)
    vle = vlEqui(alpha=alpha)
    xn, n = rectify(rl=rl, vle=vle, ql=ql, inf=inf, noisy=noisy)
    xm, m = strip(sl=sl, vle=vle, xj=xn, noisy=noisy)
    return (Rm, n, m)

def main():

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--inf", '-i', type=int, help="iteration limit", default=sys.maxsize)
    parser.add_argument("--R", type=float, help="reflux ration", default=2.0)
    parser.add_argument("--q", type=float, help="thermal condition of the feed", default=1.0)
    parser.add_argument("--alpha", type=float, help="relative volatility", default=2.5)
    parser.add_argument("--xD", type=float, help="composition of the overhead distillate", default=0.97)
    parser.add_argument("--xF", type=float, help="feed composition", default=0.45)
    parser.add_argument("--xW", type=float, help="composition of the bottom residue", default=0.02)
    args = parser.parse_args()

    Rm, n, m = calculate(args.R, args.q, args.alpha, args.xD, args.xF, args.xW, args.inf)

    print('\n' + "=" * 48)
    print("Arguments\n---")
    print(f"{f"R={args.R}":<14}   {f"q={args.q}":<14}   {f"ɑ={args.alpha}":<14}")
    print(f"{f"xD={args.xD}":<14}   {f"xF={args.xF}":<14}   {f"xW={args.xW}":<14}")
    print("=" * 48)
    print("Calculation Results\n---")
    print(f"{"Rm (Minimum Reflux Ration)":<30} : {Rm:.12f}")
    print(f"{"Nt (Total Number)":<30} : {n+m}")
    print(f"{"Nf (Feed Location)":<30} : {n+1}")
    print(f"{"Nr (Rectifying)":<30} : {n}")
    print(f"{"Ns (Stripping and Reboiler)":<30} : {m}")
    print("=" * 48 + '\n')

if __name__ == "__main__":
    main()
