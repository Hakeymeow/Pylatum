#!/usr/bin/env python3
"""Plot the relationship between Reflux Ratio (R) and number of stages.

Usage:
    uv run python src/plot.py
    uv run python src/plot.py --R-max-factor 10 --num-points 200
    uv run python src/plot.py --q 0.5 --alpha 3.0 --save plot.png
"""

import math
import sys
import matplotlib.pyplot as plt
from hylatum.src.calc import calculate, minR



def plot_R_vs_stages(
    q=1.0,
    alpha=2.5,
    xD=0.97,
    xF=0.45,
    xW=0.02,
    R_min_factor=1.01,
    R_max_factor=5.0,
    num_points=100,
    inf=10000,
    save_path=None,
):
    """Sweep R from Rm*factor to Rm*factor and plot stages."""

    Rm = minR(alpha, xD, q, xF)

    if math.isinf(Rm) or math.isnan(Rm):
        print("Error: invalid minimum reflux ratio (Rm). Check input parameters.")
        sys.exit(1)

    R_start = Rm * R_min_factor
    R_end = Rm * R_max_factor


    Nt_list, Nr_list, Ns_list, R_list = [], [], [], []
    for i in range(num_points):
        R = R_start + (R_end - R_start) * i / (num_points - 1)
        _, n, m = calculate(R, q, alpha, xD, xF, xW, inf)
        if math.isinf(n + m):
            continue
        R_list.append(R)
        Nr_list.append(n)
        Ns_list.append(m)
        Nt_list.append(n + m)

    if not R_list:
        print("Error: no valid data points (all returned inf). Try increasing inf or R_min_factor.")
        sys.exit(1)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(R_list, Nt_list, "b-", label=r"$N_t$ (Total Stages)", linewidth=2)
    ax.plot(R_list, Nr_list, "g--", label=r"$N_r$ (Rectifying Stages)", linewidth=2)
    ax.plot(R_list, Ns_list, "r-.", label=r"$N_s$ (Stripping Stages)", linewidth=2)

    ax.axvline(
        x=Rm, color="gray", linestyle=":", alpha=0.7, label=rf"$R_m$ = {Rm:.4f}"
    )

    ax.set_xlabel("Reflux Ratio $R$")
    ax.set_ylabel("Number of Stages")
    ax.set_title("McCabe-Thiele: Reflux Ratio vs. Number of Stages")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Plot Reflux Ratio vs. number of stages (McCabe-Thiele)"
    )
    parser.add_argument("--q", type=float, default=1.0, help="feed thermal condition")
    parser.add_argument("--alpha", type=float, default=2.5, help="relative volatility")
    parser.add_argument("--xD", type=float, default=0.97, help="distillate composition")
    parser.add_argument("--xF", type=float, default=0.45, help="feed composition")
    parser.add_argument("--xW", type=float, default=0.02, help="bottoms composition")
    parser.add_argument(
        "--R-min-factor",
        type=float,
        default=1.01,
        help="R sweep starts at Rm * factor",
    )
    parser.add_argument(
        "--R-max-factor",
        type=float,
        default=3.0,
        help="R sweep ends at Rm * factor",
    )
    parser.add_argument(
        "--num-points", "-n", type=int, default=100, help="number of R values to evaluate"
    )
    parser.add_argument(
        "--inf", type=int, default=10000, help="iteration limit per calculate() call"
    )
    parser.add_argument(
        "--save", type=str, default=None, help="save plot to file instead of displaying"
    )
    args = parser.parse_args()

    plot_R_vs_stages(
        q=args.q,
        alpha=args.alpha,
        xD=args.xD,
        xF=args.xF,
        xW=args.xW,
        R_min_factor=args.R_min_factor,
        R_max_factor=args.R_max_factor,
        num_points=args.num_points,
        inf=args.inf,
        save_path=args.save,
    )


if __name__ == "__main__":
    main()
