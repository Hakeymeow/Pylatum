#!/usr/bin/env python3
"""Animate McCabe-Thiele diagram with continuously changing reflux ratio R.

Draws the full stage staircase and lets R sweep from near-minimum upward,
so the viewer sees how operating lines and stage count evolve in real time.

Usage:
    uv run hy-render demo_R
    uv run python src/demo_R.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from calc import vlEqui, rectiOpline, qline, striOpline, cross, minR

from manim import *
import numpy as np

class RStagesAnimation(Scene):
    def construct(self):
        q, alpha = 1.0, 2.5
        xD, xF, xW = 0.97, 0.45, 0.02

        Rm = minR(alpha, xD, q, xF)
        R_start = Rm * 1.01
        R_end   = Rm * 5.00

        axes = Axes(x_range=[-0.1, 1, 0.1], y_range=[-0.1, 1, 0.1])
        diagonal = DashedLine(axes.c2p(0, 0), axes.c2p(1, 1))

        def vlex(a):
            return lambda xv: a * xv / (1 + (a - 1) * xv)
        vle_plot = axes.plot(vlex(alpha), color=RED_A, x_range=[0, 1])

        # draw q-line
        if q != 1:
            ql_plot = axes.plot(lambda x: q*x/(q-1)-xF/(q-1))
        else:
            ql_plot = Line(axes.c2p(xF, -1), axes.c2p(xF, 2))
        ql_plot.set_color(color=YELLOW_A)

        # VLE inverse  y → x
        vley = vlEqui(alpha)

        # Label for distillate / bottoms
        xD_label = MathTex("x_D", color=BLUE_A).next_to(axes.c2p(xD, xD), DOWN * 2)
        xW_label = MathTex("x_W", color=GREEN_A).next_to(axes.c2p(xW, 0), DOWN+RIGHT)

        R_tracker = ValueTracker(R_start)

        R_text = always_redraw(
            lambda: MathTex(
                f"R = {R_tracker.get_value()/Rm:.2f}\\,R_m", color=BLUE_A
            ).to_corner(UL)
        )

        def _rl():
            R = R_tracker.get_value()
            return Line(axes.c2p(0, xD/(R+1)), axes.c2p(xD, xD), color=BLUE_A)

        def _dot():
            R = R_tracker.get_value()
            pt = cross(rectiOpline(R, xD), qline(q, xF))
            return Dot(axes.c2p(pt), color=GREEN_A)
        def _sl():
            return Line(_dot(), axes.c2p(xW, xW), color=GREEN_A)

        def _stages():
            R = R_tracker.get_value()
            rl = rectiOpline(R, xD)
            ql = qline(q, xF)
            sl = striOpline(rl, ql, xW)

            lines = VGroup()
            xe, _ = cross(rl, ql)
            xi, yi = vley(xD), xD
            count = 0
            MAX_N = 200

            while xi > xe + 1e-10 and count < MAX_N:
                count += 1
                xj, yj = cross(rl, lambda xp, yp: xp - xi)
                lines.add(DashedLine(axes.c2p(xi, yi), axes.c2p(xj, yj), color=PURPLE_A))
                xi, yi = vley(yj), yj
                lines.add(Line(axes.c2p(xj, yj), axes.c2p(xi, yi), color=PURPLE_A))

            while xi > xW + 1e-10 and count < MAX_N:
                count += 1
                xj, yj = cross(sl, lambda xp, yp: xp - xi)
                lines.add(DashedLine(axes.c2p(xi, yi), axes.c2p(xj, yj), color=ORANGE))
                xi, yi = vley(yj), yj
                lines.add(Line(axes.c2p(xj, yj), axes.c2p(xi, yi), color=ORANGE))

            return lines

        def _count():
            R = R_tracker.get_value()
            rl = rectiOpline(R, xD)
            ql = qline(q, xF)
            sl = striOpline(rl, ql, xW)

            xe, _ = cross(rl, ql)
            xi, yi = vley(xD), xD
            Nr, Ns = 0, 0
            MAX_N = 200

            while xi > xe + 1e-10 and Nr+Ns < MAX_N:
                Nr += 1
                xj, yj = cross(rl, lambda xp, yp: xp - xi)
                xi, yi = vley(yj), yj

            while xi > xW + 1e-10 and Nr+Ns < MAX_N:
                Ns += 1
                xj, yj = cross(sl, lambda xp, yp: xp - xi)
                xi, yi = vley(yj), yj

            if Nr+Ns >= MAX_N:
                return MathTex("N_r=\\infty\\ \\ N_s=\\infty", color=RED).next_to(axes.c2p(0.9, 0), UP)
            return MathTex(f"N_r={Nr}\\ \\ N_s={Ns}", color=WHITE).next_to(axes.c2p(0.9, 0), UP)

        self.add(axes, diagonal, vle_plot, ql_plot, xD_label, xW_label)
        self.add(R_text, Dot(axes.c2p(xD, xD), color=BLUE_A), Dot(xW, xW, color=GREEN_A))

        rl_mob = always_redraw(_rl)
        sl_mob = always_redraw(_sl)
        dot_mob = always_redraw(_dot)
        stages_mob = always_redraw(_stages)
        count_mob = always_redraw(_count)

        self.add(rl_mob, sl_mob, dot_mob, stages_mob, count_mob)

        self.play(
            R_tracker.animate.set_value(R_end),
            run_time=15,
            rate_func=linear,
        )


def main():
    import subprocess
    import os

    demoPath = os.path.dirname(os.path.dirname(__file__)) + os.sep + "demo"
    os.makedirs(demoPath, exist_ok=True)
    cmd = ["manim", "-pqh", __file__, Vary.__name__]
    subprocess.run(cmd, cwd=demoPath, check=True)


if __name__ == "__main__":
    main()
