from tqdm import tqdm
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
    with tqdm(desc="Rectifying: ") as pbar:
        while xj > xe:
            i += 1
            _, yj = cross(rl, lambda x, y: x-xj)
            xj = vle(yj)
            pbar.update(1)
    return (xj, i)

def strip(sl: plane, vle: line, xj: float) -> tuple[float, int]:
    xW, _ = cross(sl, lambda x, y: x-y)
    i = 0
    with tqdm(desc="Stripping: ") as pbar:
        while xj > xW:
            i += 1
            _, yj = cross(sl, lambda x, y: x-xj)
            xj = vle(yj)
            pbar.update(1)
    return (xj, i)



def main():

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--R", type=float, help="reflux ration", default=2.0)
    parser.add_argument("--q", type=float, help="thermal condition of the feed", default=1.0)
    parser.add_argument("--alpha", type=float, help="relative volatility", default=2.5)
    parser.add_argument("--xD", type=float, help="composition of the overhead distillate", default=0.97)
    parser.add_argument("--xF", type=float, help="feed composition", default=0.45)
    parser.add_argument("--xW", type=float, help="composition of the bottom residue", default=0.02)
    args = parser.parse_args()

    rl = rectiOpline(R=args.R, xD=args.xD)
    ql = qline(q=args.q, xF=args.xF)
    sl = striOpline(rl=rl, ql=ql, xW=args.xW)
    vle = vlEqui(alpha=args.alpha)

    xn, n = rectify(rl=rl, vle=vle, ql=ql)
    xm, m = strip(sl=sl, vle=vle, xj=xn)

    print("=" * 48)
    print("Arguments\n---")
    print(f"{f"R={args.R}":<16}{f"q={args.q}":<16}{f"ɑ={args.alpha}":<16}")
    print(f"{f"xD={args.xD}":<16}{f"xF={args.xF}":<16}{f"xW={args.xW}":<16}")
    print("=" * 48)
    print("Calculation Results\n---")
    print(f"{"Nt (Total Number)":<30} : {n+m}")
    print(f"{"Nf (Feed Location)":<30} : {n+1}")
    print(f"{"Nr (Rectifying)":<30} : {n}")
    print(f"{"Ns (Stripping and Reboiler)":<30} : {m}")
    print("=" * 48)

if __name__ == "__main__":
    main()
