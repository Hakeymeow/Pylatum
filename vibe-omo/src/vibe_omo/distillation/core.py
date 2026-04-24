"""
McCabe-Thiele 法精馏塔理论塔板数计算引擎。

支持：
- 相对挥发度法计算气液平衡曲线
- 精馏段/提馏段操作线
- q 线方程
- 逐板图解理论板数
- 最小回流比计算
- 全回流最小理论板数（Fenske 验证）
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class McCabeThieleResult:
    """McCabe-Thiele 法计算结果。"""

    n_stages: int
    """理论塔板数（含再沸器时扣除）"""

    n_rectifying: int
    """精馏段塔板数（进料板以上）"""

    n_stripping: int
    """提馏段塔板数（进料板及以下）"""

    feed_stage: int
    """最佳进料位置（从上往下数，1-indexed）"""

    stage_data: np.ndarray
    """逐板坐标数组，形状 (n, 2)，用于绘图"""

    x_eq: np.ndarray
    """平衡曲线 x 坐标"""

    y_eq: np.ndarray
    """平衡曲线 y 坐标"""

    x_intersect: float
    """操作线与 q 线交点 x 坐标"""

    y_intersect: float
    """操作线与 q 线交点 y 坐标"""

    rectifying_slope: float
    """精馏段操作线斜率"""

    rectifying_intercept: float
    """精馏段操作线截距"""

    stripping_slope: float
    """提馏段操作线斜率"""

    stripping_intercept: float
    """提馏段操作线截距"""

    q_line_slope: Optional[float]
    """q 线斜率 (q=1 时为 None)"""

    q_line_x_vertical: Optional[float]
    """q 线垂直坐标 (q=1 时使用)"""

    xF: float
    """进料组成"""

    xD: float
    """馏出液组成"""

    xB: float
    """釜液组成"""

    r_min: float
    """最小回流比"""

    n_min: int
    """最小理论板数（全回流）"""

    r_actual: float
    """实际回流比"""

    converged: bool
    """是否收敛"""

    message: str
    """状态信息"""


class McCabeThiele:
    """McCabe-Thiele 图解法计算精馏塔理论塔板数。

    参数
    ----------
    xF : float
        进料中轻组分摩尔分数 (0 < xF < 1)
    xD : float
        馏出液中轻组分摩尔分数 (xF < xD < 1)
    xB : float
        釜液中轻组分摩尔分数 (0 < xB < xF)
    R : float
        实际回流比 (R > 0)
    q : float
        进料热状态参数
        - q > 1   : 过冷液体
        - q = 1   : 饱和液体
        - 0 < q < 1 : 气液混合物
        - q = 0   : 饱和蒸汽
        - q < 0   : 过热蒸汽
    alpha : float
        相对挥发度 (alpha > 1)
    n_eq_points : int
        平衡曲线离散点数 (默认 1001)
    """

    def __init__(
        self,
        xF: float,
        xD: float,
        xB: float,
        R: float,
        q: float,
        alpha: float,
        n_eq_points: int = 1001,
    ):
        if not (0 < xB < xF < xD < 1):
            raise ValueError(
                "组成需满足: 0 < xB < xF < xD < 1，"
                f"当前 xB={xB}, xF={xF}, xD={xD}"
            )
        if R <= 0:
            raise ValueError(f"回流比需大于 0，当前 R={R}")
        if alpha <= 1:
            raise ValueError(
                f"相对挥发度需大于 1，当前 alpha={alpha}"
            )

        self.xF = xF
        self.xD = xD
        self.xB = xB
        self.R = R
        self.q = q
        self.alpha = alpha
        self.n_eq_points = n_eq_points

    def _equilibrium_y(self, x: np.ndarray) -> np.ndarray:
        return self.alpha * x / (1.0 + (self.alpha - 1.0) * x)

    def _equilibrium_x(self, y: float) -> float:
        """平衡曲线反函数 x = y / (α - (α-1)y)"""
        return y / (self.alpha - (self.alpha - 1.0) * y)

    def _rectifying_y(self, x: float) -> float:
        a = self.R / (self.R + 1.0)
        b = self.xD / (self.R + 1.0)
        return a * x + b

    def _stripping_y(self, x: float, slope: float, intercept: float) -> float:
        return slope * x + intercept

    def _operating_lines(self):
        """计算操作线参数及 q 线-精馏段交点。"""
        a_r = self.R / (self.R + 1.0)
        b_r = self.xD / (self.R + 1.0)

        eps = 1e-12

        if abs(self.q - 1.0) < eps:
            q_slope = None
            x_int = self.xF
            y_int = a_r * x_int + b_r
            q_vertical = self.xF
        else:
            q_slope = self.q / (self.q - 1.0)
            q_intercept = -self.xF / (self.q - 1.0)
            q_vertical = None
            x_int = (q_intercept - b_r) / (a_r - q_slope)
            y_int = a_r * x_int + b_r

        if abs(x_int - self.xB) < eps:
            slope_s = a_r
        else:
            slope_s = (y_int - self.xB) / (x_int - self.xB)
        intercept_s = self.xB - slope_s * self.xB

        return a_r, b_r, slope_s, intercept_s, q_slope, q_vertical, x_int, y_int

    def _minimum_reflux(self) -> float:
        """计算最小回流比。

        最小回流比工况下，精馏段操作线、q 线、平衡线交于一点。
        R_min = (xD - y_q) / (y_q - x_q)
        其中 (x_q, y_q) 为 q 线与平衡线的交点。
        """
        eps = 1e-12
        x_eq = np.linspace(0, 1, self.n_eq_points)
        y_eq = self._equilibrium_y(x_eq)

        if abs(self.q - 1.0) < eps:
            x_q = self.xF
            y_q = float(np.interp(x_q, x_eq, y_eq))
        else:
            q_slope = self.q / (self.q - 1.0)
            q_intercept = -self.xF / (self.q - 1.0)

            a = (self.alpha - 1.0) * q_slope
            b = q_slope + (self.alpha - 1.0) * q_intercept - self.alpha
            c = q_intercept

            disc = b * b - 4.0 * a * c
            if disc < 0:
                search_x = np.linspace(self.xB, self.xD, self.n_eq_points)
                search_y_q = q_slope * search_x + q_intercept
                search_y_eq = self._equilibrium_y(search_x)
                diff = np.abs(search_y_q - search_y_eq)
                idx = int(np.argmin(diff))
                x_q = search_x[idx]
                y_q = search_y_eq[idx]
            else:
                sqrt_disc = np.sqrt(disc)
                x_q1 = (-b + sqrt_disc) / (2.0 * a)
                x_q2 = (-b - sqrt_disc) / (2.0 * a)
                candidates = [v for v in (x_q1, x_q2) if self.xB - 1e-6 <= v <= self.xD + 1e-6]
                if candidates:
                    x_q = candidates[0]
                else:
                    x_q = (self.xB + self.xD) / 2.0
                x_q = max(self.xB, min(self.xD, x_q))
                y_q = float(np.interp(x_q, x_eq, y_eq))

        if y_q <= x_q + eps:
            return 0.0

        r_min = (self.xD - y_q) / (y_q - x_q)
        return max(0.0, r_min)

    def _minimum_stages(self) -> int:
        """Fenske 方程计算全回流最小理论板数。

        N_min = log[(xD/(1-xD)) / (xB/(1-xB))] / log(α)
        """
        if abs(self.alpha - 1.0) < 1e-12:
            return 0
        ratio = (self.xD / (1.0 - self.xD)) / (self.xB / (1.0 - self.xB))
        if ratio <= 0:
            return 0
        n_min = np.log(ratio) / np.log(self.alpha)
        return max(1, int(np.ceil(n_min)))

    def _step_off(self) -> tuple:
        """逐板计算: x_{n+1} = f⁻¹(op_line(x_n))"""
        eps = 1e-12
        max_stages = 500

        x_eq = np.linspace(0, 1, self.n_eq_points)
        y_eq = self._equilibrium_y(x_eq)

        a_r, b_r, slope_s, intercept_s, q_slope, q_vertical, x_int, y_int = (
            self._operating_lines()
        )

        x_prev = float(self.xD)
        stages = 0
        feed_stage = 1
        cross_feed = False
        stage_data = [(float(self.xD), float(self.xD))]

        while x_prev > self.xB + 1e-8:
            if not cross_feed:
                y_op = a_r * x_prev + b_r
            else:
                y_op = slope_s * x_prev + intercept_s

            if not cross_feed and x_prev <= x_int:
                cross_feed = True
                feed_stage = stages + 1
                y_op = slope_s * x_prev + intercept_s

            x_curr = self._equilibrium_x(y_op)

            stage_data.append((x_curr, y_op))

            stages += 1
            x_prev = x_curr

            if stages >= max_stages:
                break

        full_path = [stage_data[0]]
        for i in range(1, len(stage_data)):
            y_op = stage_data[i][1]
            x_curr = stage_data[i][0]
            x_prev = stage_data[i - 1][0] if i > 0 else self.xD
            full_path.append((x_prev, y_op))
            full_path.append((x_curr, y_op))

        n_rectifying = feed_stage - 1
        n_stripping = stages - feed_stage + 1

        return (
            stages,
            feed_stage,
            n_rectifying,
            n_stripping,
            np.array(full_path),
            x_eq,
            y_eq,
            x_int,
            y_int,
            a_r,
            b_r,
            slope_s,
            intercept_s,
            q_slope,
            q_vertical,
            True,
        )

        

    def calculate(self) -> McCabeThieleResult:
        """执行完整计算。

        Returns
        -------
        McCabeThieleResult
            包含所有计算结果的 dataclass。
        """
        r_min = self._minimum_reflux()

        if self.R < r_min:
            msg = (
                f"回流比 R={self.R:.4f} 小于最小回流比 R_min={r_min:.4f}，"
                "无法收敛，结算结果仅供参考"
            )
        else:
            msg = "计算正常收敛"

        n_min = self._minimum_stages()

        result = self._step_off()
        (
            n_stages,
            feed_stage,
            n_rectifying,
            n_stripping,
            stage_data,
            x_eq,
            y_eq,
            x_int,
            y_int,
            a_r,
            b_r,
            slope_s,
            intercept_s,
            q_slope,
            q_vertical,
            converged,
        ) = result

        if not converged:
            msg = f"逐板计算达到最大迭代次数 (>{n_stages})，可能未收敛至 xB"

        return McCabeThieleResult(
            n_stages=n_stages,
            n_rectifying=n_rectifying,
            n_stripping=n_stripping,
            feed_stage=feed_stage,
            stage_data=stage_data,
            x_eq=x_eq,
            y_eq=y_eq,
            x_intersect=x_int,
            y_intersect=y_int,
            rectifying_slope=a_r,
            rectifying_intercept=b_r,
            stripping_slope=slope_s,
            stripping_intercept=intercept_s,
            q_line_slope=q_slope,
            q_line_x_vertical=q_vertical,
            xF=self.xF,
            xD=self.xD,
            xB=self.xB,
            r_min=r_min,
            n_min=n_min,
            r_actual=self.R,
            converged=converged,
            message=msg,
        )
