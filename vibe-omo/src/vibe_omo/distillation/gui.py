"""
McCabe-Thiele 精馏塔理论塔板数计算 - 桌面 GUI 程序。

依赖: tkinter (built-in), matplotlib, numpy
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from .core import McCabeThiele, McCabeThieleResult


PRESETS = {
    "苯-甲苯 (常压)": dict(xF=0.50, xD=0.95, xB=0.05, R=2.5, q=1.0, alpha=2.47),
    "乙醇-水 (常压)": dict(xF=0.30, xD=0.85, xB=0.05, R=3.0, q=1.0, alpha=2.21),
    "甲醇-水 (常压)": dict(xF=0.40, xD=0.90, xB=0.05, R=2.0, q=1.0, alpha=3.72),
    "丙酮-苯 (常压)": dict(xF=0.45, xD=0.90, xB=0.05, R=2.0, q=1.2, alpha=2.10),
}


class DistillationGUI:
    """McCabe-Thiele 图解法精馏塔计算 GUI。"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("精馏塔理论塔板数计算 — McCabe-Thiele 图解法")
        self.root.geometry("1200x780")
        self.root.minsize(1000, 680)

        self._result: Optional[McCabeThieleResult] = None
        self._setup_ui()
        self._setup_menu()

    def _setup_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="导出图片 (PNG)", command=self._export_plot, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用说明", command=self._show_help)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menubar)

        self.root.bind("<Control-e>", lambda e: self._export_plot())
        self.root.bind("<Return>", lambda e: self._calculate())

    def _setup_ui(self):
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        left = ttk.Frame(main, width=340)
        main.add(left, weight=0)

        title = ttk.Label(left, text="McCabe-Thiele 图解法",
                          font=("", 14, "bold"))
        title.pack(pady=(8, 2))

        subtitle = ttk.Label(left, text="精馏塔理论塔板数计算",
                             font=("", 10))
        subtitle.pack(pady=(0, 10))

        params_box = ttk.LabelFrame(left, text="操作参数", padding=10)
        params_box.pack(fill=tk.X, padx=8, pady=4)

        self._entries = {}
        fields = [
            ("xF", "进料组成 (轻组分摩尔分数):", 0.50),
            ("xD", "馏出液组成:", 0.95),
            ("xB", "釜液组成:", 0.05),
            ("R",  "回流比 R:", 2.5),
            ("q",  "进料热状态 q:", 1.0),
            ("alpha", "相对挥发度 α:", 2.47),
        ]

        for key, label_text, default in fields:
            row = ttk.Frame(params_box)
            row.pack(fill=tk.X, pady=3)
            ttk.Label(row, text=label_text, width=24, anchor=tk.W).pack(side=tk.LEFT)
            entry = ttk.Entry(row, width=12, font=("", 10))
            entry.insert(0, str(default))
            entry.pack(side=tk.RIGHT)
            self._entries[key] = entry

        q_note = ttk.Label(params_box,
                           text="  q=1:饱和液体  0<q<1:气液混合  q>1:过冷",
                           font=("", 8), foreground="gray")
        q_note.pack(anchor=tk.W, pady=(0, 2))

        preset_box = ttk.LabelFrame(left, text="预设案例", padding=8)
        preset_box.pack(fill=tk.X, padx=8, pady=6)

        for name in PRESETS:
            btn = ttk.Button(preset_box, text=name,
                             command=lambda n=name: self._load_preset(n))
            btn.pack(fill=tk.X, pady=1)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, padx=8, pady=6)

        self._calc_btn = ttk.Button(btn_frame, text="开始计算",
                                    command=self._calculate)
        self._calc_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        export_btn = ttk.Button(btn_frame, text="导出图片",
                                command=self._export_plot)
        export_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        result_box = ttk.LabelFrame(left, text="计算结果", padding=10)
        result_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self._result_labels = {}
        result_fields = [
            ("n_stages", "理论塔板数 N:"),
            ("feed_stage", "最佳进料位置:"),
            ("r_min", "最小回流比 R_min:"),
            ("n_min", "最小理论板数 N_min:"),
            ("r_actual", "实际回流比 R:"),
            ("status", "状态:"),
        ]
        for key, label_text in result_fields:
            row = ttk.Frame(result_box)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=label_text, width=20, anchor=tk.W).pack(side=tk.LEFT)
            lbl = ttk.Label(row, text="--", font=("", 10, "bold"),
                            anchor=tk.E, width=14)
            lbl.pack(side=tk.RIGHT)
            self._result_labels[key] = lbl

        right = ttk.Frame(main)
        main.add(right, weight=1)

        self.fig = Figure(figsize=(7, 6.5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, right, pack_toolbar=False)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self._draw_empty_chart()

    def _draw_empty_chart(self):
        self.ax.clear()
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_xlabel("x (液相组成)")
        self.ax.set_ylabel("y (气相组成)")
        self.ax.set_title("McCabe-Thiele 图", fontsize=12)
        self.ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="对角线 y=x")
        self.ax.legend(loc="lower right", fontsize=8)
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()

    def _plot_result(self, result: McCabeThieleResult):
        self.ax.clear()
        ax = self.ax

        ax.plot(result.x_eq, result.y_eq, "b-", linewidth=1.8, label="平衡曲线")

        diag = np.linspace(0, 1, 200)
        ax.plot(diag, diag, "k--", linewidth=0.8, label="对角线 y=x")

        x_r = np.linspace(result.x_intersect, result.xD, 100)
        y_r = result.rectifying_slope * x_r + result.rectifying_intercept
        ax.plot(x_r, y_r, "r-", linewidth=1.5, label="精馏段操作线")

        x_s = np.linspace(result.xB, result.x_intersect, 100)
        y_s = result.stripping_slope * x_s + result.stripping_intercept
        ax.plot(x_s, y_s, "g-", linewidth=1.5, label="提馏段操作线")

        if result.q_line_x_vertical is not None:
            ax.axvline(x=result.q_line_x_vertical, color="orange",
                       linewidth=1.2, linestyle="--", label="q 线 (x=xF)")
        elif result.q_line_slope is not None:
            x_q = np.linspace(result.xB, result.xD, 100)
            b_q = result.y_intersect - result.q_line_slope * result.x_intersect
            y_q = result.q_line_slope * x_q + b_q
            ax.plot(x_q, y_q, color="orange", linewidth=1.2,
                    linestyle="--", label="q 线")

        sd = result.stage_data
        if len(sd) > 1:
            ax.plot(sd[:, 0], sd[:, 1], "k-", linewidth=0.8, alpha=0.7)
            for i in range(len(sd) - 1):
                xs, ys = sd[i], sd[i + 1]
                if i % 2 == 0:
                    ax.plot([xs[0], xs[0]], [xs[1], ys[1]], "k-", linewidth=1.2)
                else:
                    ax.plot([xs[0], ys[0]], [xs[1], ys[1]], "k-", linewidth=1.2)
            for i in range(len(sd)):
                if i % 2 == 0:
                    ax.plot(sd[i, 0], sd[i, 1], "ko", markersize=3)

        ax.plot(result.x_intersect, result.y_intersect, "D", color="purple",
                markersize=6, zorder=5)
        ax.annotate(
            f"({result.x_intersect:.3f}, {result.y_intersect:.3f})",
            (result.x_intersect, result.y_intersect),
            xytext=(10, -15), textcoords="offset points",
            fontsize=8, color="purple"
        )

        for val, label, color in [
            (result.xD, f"xD={result.xD:.3f}", "red"),
            (result.xF, f"xF={result.xF:.3f}", "orange"),
            (result.xB, f"xB={result.xB:.3f}", "green"),
        ]:
            ax.axvline(x=val, color=color, linewidth=0.5, linestyle=":", alpha=0.5)
            ax.annotate(label, (val, 0.02), fontsize=7, color=color,
                        ha="center", va="bottom")

        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel("x (液相摩尔分数)", fontsize=10)
        ax.set_ylabel("y (气相摩尔分数)", fontsize=10)
        ax.set_title(
            f"McCabe-Thiele 图 — 理论板数 N={result.n_stages}  进料位置={result.feed_stage}",
            fontsize=12
        )
        ax.legend(loc="lower right", fontsize=8)
        ax.grid(True, alpha=0.25)
        ax.set_aspect("equal")
        self.fig.tight_layout()
        self.canvas.draw()

    def _get_params(self) -> Optional[dict]:
        """读取并校验参数，返回参数字典，无效时返回 None。"""
        try:
            xF = float(self._entries["xF"].get())
            xD = float(self._entries["xD"].get())
            xB = float(self._entries["xB"].get())
            R = float(self._entries["R"].get())
            q = float(self._entries["q"].get())
            alpha = float(self._entries["alpha"].get())
        except ValueError:
            messagebox.showerror("输入错误", "所有参数必须为有效的数值。")
            return None

        errors = []
        if not (0 < xB < xF < xD < 1):
            errors.append("组成需满足: 0 < xB < xF < xD < 1")
        if R <= 0:
            errors.append("回流比 R 必须大于 0")
        if alpha <= 1:
            errors.append("相对挥发度 α 必须大于 1")

        if errors:
            messagebox.showerror("参数校验失败", "\n".join(errors))
            return None

        return dict(xF=xF, xD=xD, xB=xB, R=R, q=q, alpha=alpha)

    def _calculate(self):
        params = self._get_params()
        if params is None:
            return

        try:
            calc = McCabeThiele(**params)
            result = calc.calculate()
        except Exception as e:
            messagebox.showerror("计算错误", str(e))
            return

        self._result = result

        self._result_labels["n_stages"].config(text=str(result.n_stages))
        self._result_labels["feed_stage"].config(text=str(result.feed_stage))
        self._result_labels["r_min"].config(text=f"{result.r_min:.4f}")
        self._result_labels["n_min"].config(text=str(result.n_min))
        self._result_labels["r_actual"].config(text=f"{result.r_actual:.4f}")

        if result.r_actual < result.r_min:
            status_text = f"⚠ R < R_min !"
            self._result_labels["status"].config(foreground="red")
        elif not result.converged:
            status_text = "⚠ 未完全收敛"
            self._result_labels["status"].config(foreground="orange")
        else:
            status_text = "✓ 收敛正常"
            self._result_labels["status"].config(foreground="green")
        self._result_labels["status"].config(text=status_text)

        self._plot_result(result)

    def _load_preset(self, name: str):
        data = PRESETS[name]
        for key in ("xF", "xD", "xB", "R", "q", "alpha"):
            entry = self._entries[key]
            entry.delete(0, tk.END)
            entry.insert(0, str(data[key]))

    def _export_plot(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")],
        )
        if path:
            try:
                self.fig.savefig(path, dpi=200, bbox_inches="tight")
                messagebox.showinfo("导出成功", f"图片已保存至:\n{path}")
            except Exception as e:
                messagebox.showerror("导出失败", str(e))

    def _show_help(self):
        msg = (
            "McCabe-Thiele 图解法计算精馏塔理论塔板数\n\n"
            "参数说明:\n"
            "  xF  — 进料中轻组分摩尔分数 (0~1)\n"
            "  xD  — 馏出液中轻组分摩尔分数 (> xF)\n"
            "  xB  — 釜液中轻组分摩尔分数 (< xF)\n"
            "  R   — 回流比 (> 0)\n"
            "  q   — 进料热状态:\n"
            "        q>1 : 过冷液体\n"
            "        q=1 : 饱和液体\n"
            "        0<q<1 : 气液混合物\n"
            "        q=0 : 饱和蒸汽\n"
            "        q<0 : 过热蒸汽\n"
            "  α   — 相对挥发度 (> 1)\n\n"
            "结果解读:\n"
            "  N       — 理论塔板数\n"
            "  进料位置 — 从塔顶往下数的进料板编号\n"
            "  R_min   — 最小回流比 (R < R_min 无法操作)\n"
            "  N_min   — 全回流最小理论板数 (Fenske)\n\n"
            "操作:\n"
            "  Enter 键  — 开始计算\n"
            "  Ctrl+E   — 导出图片\n"
            "  鼠标滚轮 — 缩放图表"
        )
        messagebox.showinfo("使用说明", msg)

    def run(self):
        self.root.mainloop()


def main():
    app = DistillationGUI()
    app.run()


if __name__ == "__main__":
    main()
