import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from calc import vlEqui, rectiOpline, qline, striOpline, cross, minR

from manim import *
import numpy as np



class Draw(Scene):
    def construct(self):
        # # default parameters
        R, q, alpha = 10, 1.0, 2.5
        xD, xF, xW = 0.97, 0.45, 0.02
        # # chemical engineering equations
        vley = vlEqui(alpha)
        rl, ql = rectiOpline(R, xD), qline(q, xF)
        sl = striOpline(rl, ql, xW)

        # draw axes and diagonal
        axes = Axes(x_range=[0, 1, 0.1], y_range=[0, 1, 0.1])
        diagonal = DashedLine(axes.c2p(0,0), axes.c2p(1,1))
        self.play(Create(axes))
        self.play(Create(diagonal))
        self.wait()

        # draw equilibrim line
        def vlex(alpha: float):
            return lambda x: alpha*x/(1+(alpha-1)*x)
        vlePlot = axes.plot(vlex(alpha), color=RED_A)
        vleText = MathTex("y=\\frac{\\alpha x}{(\\alpha-1)x}", color=RED_A).next_to(Dot(axes.c2p(0.5, 1.0)))
        self.play(Write(vleText),Create(vlePlot))
        self.play(FadeOut(vleText))
        self.wait()

        # draw rectification operational lines
        startPoint = Dot(axes.c2p(cross(rl, lambda x, y: x-0)), color=BLUE_A)
        endPoint = Dot(axes.c2p((xD, xD)), color=BLUE_A)
        rlPlot = Line(startPoint, endPoint, color=BLUE_A)
        startText = MathTex("(0, \\frac{1}{R+1}x_D)", color=BLUE_A).next_to(startPoint, RIGHT+5*UP)
        endText = MathTex("(x_D, x_D)", color=BLUE_A).next_to(endPoint, DOWN*2)
        rlText = MathTex("y=\\frac{R}{R+1}x+\\frac{1}{R}", color=BLUE_A).next_to(rlPlot.get_center(), UP*5)
        self.play(FadeIn(startPoint), Write(startText))
        self.play(Write(endText), FadeIn(endPoint))
        self.play(Write(rlText), Create(rlPlot))
        self.play(FadeOut(rlText), FadeOut(startText), FadeOut(endText))
        self.wait()

        # draw q-line    
        qlk = np.divide(q*axes.get_y_unit_size(), (q-1)*axes.get_x_unit_size())
        auxiLine = Line(axes.c2p(0, xF), axes.c2p(2*xF, xF), color=YELLOW_A)
        qlAngle = Angle(auxiLine.copy(), auxiLine.copy().rotate(angle=np.arctan(qlk), about_point=auxiLine.get_center()))
        qlCText = MathTex("(x_F, x_F)", color=YELLOW_A).next_to(auxiLine.get_center(), DOWN*0.5+RIGHT*1.5)
        auxiText = MathTex("y=x_F", color=YELLOW_A).next_to(axes.c2p(0, xF+0.1), RIGHT)
        qlAText = MathTex("\\theta=\\arctan{\\frac{q}{q-1}}", color=YELLOW_A).next_to(axes.c2p(xF-0.1, 0.8), LEFT*2)
        qlText = MathTex("y = \\frac{q}{q-1}x-\\frac{1}{q-1}x_F", color=YELLOW_A).next_to(qlCText, DOWN+RIGHT*0.5)
        qlCenter = Dot(auxiLine.get_center(), color=YELLOW_A)
        self.play(FadeIn(qlCenter), Write(qlCText))
        self.play(Create(qlAngle.lines[0]), Write(auxiText))
        self.play(FadeOut(auxiText), Rotate(auxiLine, angle=np.arctan(qlk), about_point=auxiLine.get_center()), Create(qlAngle), Write(qlAText))
        self.play(FadeOut(qlCText), FadeOut(qlAText), Write(qlText))
        self.play(FadeOut(qlAngle.lines[0]), FadeOut(qlAngle), FadeOut(qlText))
        self.wait()

        # draw stripping operational line
        startPoint = Dot(axes.c2p(cross(rl, ql)), color=GREEN_A)
        endPoint = Dot(axes.c2p(xW, xW), color=GREEN_A)
        slPlot = Line(startPoint, endPoint, color=GREEN_A)
        startText = MathTex("(x_d, x_d)", color=GREEN_A).next_to(startPoint, UP+LEFT)
        endText = MathTex("(x_W, x_W)", color=GREEN_A).next_to(endPoint, DOWN)
        slText = MathTex("\\frac{y-x_w}{x-x_w}=\\frac{y_d-x_w}{x_d-x_w}", color=GREEN_A).next_to(slPlot.get_center(), RIGHT*15)
        self.play(FadeIn(startPoint), Write(startText))
        self.play(FadeIn(endPoint), Write(endText))
        self.play(FadeIn(slText), Create(slPlot))
        self.play(FadeOut(slText), FadeOut(startText), FadeOut(endText))
        self.play(FadeOut(auxiLine), FadeOut(qlCenter))
        self.wait()

        # draw rectification section
        xe, _ = cross(rl, ql)
        xi, yi = vley(xD), xD
        di = Dot(axes.c2p(xD, xD), color=BLUE_A)
        li = Line(axes.c2p(xD, xD), axes.c2p(xi, yi))
        self.play(di.animate.set_color(WHITE))
        self.play(Create(li), MoveAlongPath(di, li))
        while xi > xe:
            self.play(li.animate.set_color(PURPLE_A))
            xj, yj = cross(rl, lambda x, y: x-xi)
            self.play(Create(DashedLine(axes.c2p(xi, yi), axes.c2p(xj, yj), color=PURPLE_A)), MoveAlongPath(di, Line(axes.c2p(xi, yi), axes.c2p(xj, yj))))
            xi, yi = vley(yj), yj
            li = Line(axes.c2p(xj, yj), axes.c2p(xi, yi))
            self.play(Create(li), MoveAlongPath(di, li))

        # draw stripping section
        while xi > xW:
            self.play(li.animate.set_color(ORANGE))
            xj, yj = cross(sl, lambda x, y: x-xi)
            self.play(Create(DashedLine(axes.c2p(xi, yi), axes.c2p(xj, yj), color=ORANGE)), MoveAlongPath(di, Line(axes.c2p(xi, yi), axes.c2p(xj, yj))))
            xi, yi = vley(yj), yj
            li = Line(axes.c2p(xj, yj), axes.c2p(xi, yi))
            self.play(Create(li), MoveAlongPath(di, li))
        self.wait()



class Vary(Scene):
    def construct(self):
        q, alpha = 1.0, 2.5
        xD, xF, xW = 0.97, 0.45, 0.02

        Rm = minR(alpha, xD, q, xF)
        R_start = Rm * 5.00
        R_end   = Rm * 1.01

        axes = Axes(x_range=[-0.1, 1, 0.1], y_range=[-0.1, 1, 0.1])
        diagonal = DashedLine(axes.c2p(0, 0), axes.c2p(1, 1))

        def vlex(a):
            return lambda xv: a * xv / (1 + (a - 1) * xv)
        vle_plot = axes.plot(vlex(alpha), color=RED_A, x_range=[0, 1])

        # draw q-line
        ql_plot = Line(axes.c2p(0, xF), axes.c2p(1, xF), color=YELLOW_A).rotate(
            angle=np.arctan(np.divide(q*axes.get_y_unit_size(), (q-1)*axes.get_x_unit_size())),
            about_point=axes.c2p(xF, xF)
        )

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
        self.add(R_text, Dot(axes.c2p(xD, xD), color=BLUE_A), Dot(axes.c2p(xW, xW), color=GREEN_A))

        rl_mob = always_redraw(_rl)
        sl_mob = always_redraw(_sl)
        dot_mob = always_redraw(_dot)
        stages_mob = always_redraw(_stages)
        count_mob = always_redraw(_count)

        self.add(rl_mob, sl_mob, dot_mob, stages_mob, count_mob)

        self.play(
            R_tracker.animate.set_value(R_end),
            run_time=10,
            rate_func=there_and_back,
        )

def main():
    import os, subprocess, argparse

    argParser = argparse.ArgumentParser(description="Render manim demonstration of McCabe-Thiele method.")
    argParser.add_argument("--demo", "-d", type=str, 
        choices=[x.lower() for x in [Draw.__name__, Vary.__name__]],
        help="demo to be rendered"
        )
    if len(sys.argv) == 1:
        argParser.print_help()
        sys.exit(0)

    demoPath = os.path.dirname(os.path.dirname(__file__)) + os.sep + "demo"
    os.makedirs(demoPath, exist_ok=True)
    args = argParser.parse_args()
    cmd = ["manim", "-pqh", __file__, args.demo.capitalize()]
    subprocess.run(cmd, cwd=demoPath, check=True)

if __name__ == "__main__":
    main()
