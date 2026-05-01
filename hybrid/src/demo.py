import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from calc import vlEqui, rectiOpline, qline, striOpline, cross

from manim import *
import numpy as np

class Demostration(Scene):
    def construct(self):
        # # default parameters
        R, q, alpha = 10, -1.0, 2.5
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


def main():
    import subprocess
    import os

    demoPath = os.path.dirname(os.path.dirname(__file__)) + os.sep + "demo"
    os.makedirs(demoPath, exist_ok=True)
    cmd = ["manim", "-pqh", __file__, Demostration.__name__]
    subprocess.run(cmd, cwd=demoPath, check=True)

if __name__ == "__main__":
    main()
