"""
McCabe-Thiele 精馏塔理论塔板数计算 - GTK3 GUI 程序。

依赖: PyGObject (GTK3), PyCairo, numpy
"""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GLib, Pango

import numpy as np
import os

from .core import McCabeThiele, McCabeThieleResult
from .plotter import CairoPlotter


PRESETS = {
    "苯-甲苯 (常压)": dict(xF=0.45, xD=0.97, xB=0.02, R=2.0, q=1.0, alpha=2.50),
    "乙醇-水 (常压)": dict(xF=0.30, xD=0.85, xB=0.05, R=3.0, q=1.0, alpha=2.21),
    "甲醇-水 (常压)": dict(xF=0.40, xD=0.90, xB=0.05, R=2.0, q=1.0, alpha=3.72),
    "丙酮-苯 (常压)": dict(xF=0.45, xD=0.90, xB=0.05, R=2.0, q=1.2, alpha=2.10),
}


class DistillationGUI:
    """McCabe-Thiele 图解法精馏塔计算 GTK3 GUI。"""

    def __init__(self):
        self.app = Gtk.Application.new(
            "com.vibe-omo.distillation", Gio.ApplicationFlags.FLAGS_NONE
        )
        self.app.connect("activate", self._on_activate)
        self._result: McCabeThieleResult | None = None
        self._plotter = CairoPlotter(None)
        self._chart_visible = True
        self._default_size = (1200, 780)

    def _on_activate(self, app):
        self._build_window(app)
        self._build_menu()
        self._build_ui()
        self._connect_signals()
        self.window.show_all()

    def _build_window(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_title("精馏塔理论塔板数计算 — McCabe-Thiele 图解法")
        self.window.set_default_size(1200, 780)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_resizable(True)
        css = (
            b".result-value { font-weight: bold; font-size: 10pt; }\n"
            b".title-label { font-weight: bold; font-size: 14pt; }\n"
            b".q-note { font-size: 8pt; color: #808080; }"
        )
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            self.window.get_screen(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _build_menu(self):
        mb = Gtk.MenuBar()

        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="文件")
        file_item.set_submenu(file_menu)

        export_item = Gtk.MenuItem(label="导出图片")
        export_item.connect("activate", lambda _: self._export_plot())
        file_menu.append(export_item)
        file_menu.append(Gtk.SeparatorMenuItem())
        quit_item = Gtk.MenuItem(label="退出")
        quit_item.connect("activate", lambda _: self.window.close())
        file_menu.append(quit_item)

        view_menu = Gtk.Menu()
        view_item = Gtk.MenuItem(label="视图")
        view_item.set_submenu(view_menu)

        self._chart_toggle = Gtk.CheckMenuItem(label="显示图表")
        self._chart_toggle.set_active(True)
        self._chart_toggle.connect("toggled", lambda _: self._toggle_chart())
        view_menu.append(self._chart_toggle)

        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="帮助")
        help_item.set_submenu(help_menu)
        usage_item = Gtk.MenuItem(label="使用说明")
        usage_item.connect("activate", lambda _: self._show_help())
        help_menu.append(usage_item)

        mb.append(file_item)
        mb.append(view_item)
        mb.append(help_item)

        ag = Gtk.AccelGroup()
        self.window.add_accel_group(ag)
        key, mod = Gtk.accelerator_parse("<Control>e")
        export_item.add_accelerator(
            "activate", ag, key, mod, Gtk.AccelFlags.VISIBLE
        )
        self._menu_bar = mb

    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.pack_start(self._menu_bar, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        vbox.pack_start(hbox, True, True, 0)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        left.set_size_request(340, -1)
        hbox.pack_start(left, False, False, 0)

        self._right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        hbox.pack_start(self._right_box, True, True, 0)

        self._drawing_area = Gtk.DrawingArea()
        self._drawing_area.connect("draw", self._on_draw)
        self._drawing_area.set_hexpand(True)
        self._drawing_area.set_vexpand(True)
        self._right_box.pack_start(self._drawing_area, True, True, 0)

        self.window.add(vbox)
        self._build_left_panel(left)

    def _build_left_panel(self, parent):
        title = Gtk.Label(label="McCabe-Thiele 图解法")
        title.get_style_context().add_class("title-label")
        parent.pack_start(title, False, False, 2)

        subtitle = Gtk.Label(label="精馏塔理论塔板数计算")
        parent.pack_start(subtitle, False, False, 2)

        params_frame = Gtk.Frame(label="操作参数")
        params_grid = Gtk.Grid(row_spacing=6, column_spacing=8)
        params_frame.add(params_grid)
        parent.pack_start(params_frame, False, False, 2)

        self._entries = {}
        fields = [
            ("xF", "进料组成 (轻组分摩尔分数):"),
            ("xD", "馏出液组成:"),
            ("xB", "釜液组成:"),
            ("R", "回流比 R:"),
            ("q", "进料热状态 q:"),
            ("alpha", "相对挥发度 α:"),
        ]
        defaults = {"xF": 0.45, "xD": 0.97, "xB": 0.02, "R": 2.0, "q": 1.0, "alpha": 2.50}
        for i, (key, label_text) in enumerate(fields):
            lbl = Gtk.Label(label=label_text, xalign=0.0)
            entry = Gtk.Entry()
            entry.set_text(str(defaults[key]))
            entry.set_width_chars(12)
            params_grid.attach(lbl, 0, i, 1, 1)
            params_grid.attach(entry, 1, i, 1, 1)
            self._entries[key] = entry

        q_note = Gtk.Label(
            label="q=1:饱和液体  0<q<1:气液混合  q>1:过冷",
            xalign=0.0,
        )
        q_note.get_style_context().add_class("q-note")
        parent.pack_start(q_note, False, False, 2)

        preset_frame = Gtk.Frame(label="预设案例")
        preset_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        preset_frame.add(preset_box)
        parent.pack_start(preset_frame, False, False, 2)

        for name in PRESETS:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", lambda b, n=name: self._load_preset(n))
            preset_box.pack_start(btn, True, True, 0)

        btn_box = Gtk.Box(spacing=4)
        parent.pack_start(btn_box, False, False, 4)

        calc_btn = Gtk.Button(label="开始计算")
        calc_btn.connect("clicked", lambda _: self._calculate())
        btn_box.pack_start(calc_btn, True, True, 0)

        export_btn = Gtk.Button(label="导出图片")
        export_btn.connect("clicked", lambda _: self._export_plot())
        btn_box.pack_start(export_btn, True, True, 0)

        result_frame = Gtk.Frame(label="计算结果")
        result_grid = Gtk.Grid(row_spacing=4, column_spacing=8)
        result_frame.add(result_grid)
        parent.pack_start(result_frame, True, True, 2)

        self._result_labels = {}
        result_fields = [
            ("n_stages", "理论塔板数 N:"),
            ("n_rectifying", "精馏段塔板数:"),
            ("n_stripping", "提馏段塔板数:"),
            ("feed_stage", "最佳进料位置:"),
            ("r_min", "最小回流比 R_min:"),
            ("n_min", "最小理论板数 N_min:"),
            ("r_actual", "实际回流比 R:"),
            ("status", "状态:"),
        ]
        for i, (key, label_text) in enumerate(result_fields):
            lbl = Gtk.Label(label=label_text, xalign=0.0)
            val = Gtk.Label(label="--", xalign=1.0)
            val.get_style_context().add_class("result-value")
            result_grid.attach(lbl, 0, i, 1, 1)
            result_grid.attach(val, 1, i, 1, 1)
            self._result_labels[key] = val

    def _on_draw(self, widget, ctx):
        alloc = widget.get_allocation()
        width = alloc.width
        height = alloc.height
        self._plotter.draw(ctx, width, height)
        return False

    def _connect_signals(self):
        self.window.connect("key-press-event", self._on_key_press)

    def _toggle_chart(self):
        self._chart_visible = self._chart_toggle.get_active()
        if self._chart_visible:
            self._right_box.show()
            self.window.set_title("精馏塔理论塔板数计算 — McCabe-Thiele 图解法")
            w, h = self._default_size
            self.window.resize(w, h)
        else:
            self._right_box.hide()
            self.window.set_title("精馏塔理论塔板数计算 (计算器模式)")
            self.window.resize(400, 600)
            self.window.set_position(Gtk.WindowPosition.CENTER)

    def _on_key_press(self, widget, event):
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._calculate()
            return True
        return False

    def _get_params(self):
        try:
            xF = float(self._entries["xF"].get_text())
            xD = float(self._entries["xD"].get_text())
            xB = float(self._entries["xB"].get_text())
            R = float(self._entries["R"].get_text())
            q = float(self._entries["q"].get_text())
            alpha = float(self._entries["alpha"].get_text())
        except ValueError:
            self._show_error("所有参数必须为有效的数值。")
            return None

        errors = []
        if not (0 < xB < xF < xD < 1):
            errors.append("组成需满足: 0 < xB < xF < xD < 1")
        if R <= 0:
            errors.append("回流比 R 必须大于 0")
        if alpha <= 1:
            errors.append("相对挥发度 α 必须大于 1")
        if errors:
            self._show_error("\n".join(errors))
            return None

        return dict(xF=xF, xD=xD, xB=xB, R=R, q=q, alpha=alpha)

    def _calculate(self):
        params = self._get_params()
        if params is None:
            return
        try:
            calc = McCabeThiele(
                xF=params["xF"], xD=params["xD"], xB=params["xB"],
                R=params["R"], q=params["q"], alpha=params["alpha"],
            )
            result = calc.calculate()
        except Exception as e:
            self._show_error(str(e))
            return

        self._result = result
        self._plotter = CairoPlotter(result)

        self._result_labels["n_stages"].set_text(str(result.n_stages))
        self._result_labels["n_rectifying"].set_text(str(result.n_rectifying))
        self._result_labels["n_stripping"].set_text(str(result.n_stripping))
        self._result_labels["feed_stage"].set_text(str(result.feed_stage))
        self._result_labels["r_min"].set_text(f"{result.r_min:.4f}")
        self._result_labels["n_min"].set_text(str(result.n_min))
        self._result_labels["r_actual"].set_text(f"{result.r_actual:.4f}")

        if result.r_actual < result.r_min:
            status_text = "⚠ R < R_min !"
            color = "red"
        elif not result.converged:
            status_text = "⚠ 未完全收敛"
            color = "orange"
        else:
            status_text = "✓ 收敛正常"
            color = "green"
        self._result_labels["status"].set_markup(
            f'<span foreground="{color}">{status_text}</span>'
        )
        self._drawing_area.queue_draw()

    def _load_preset(self, name):
        data = PRESETS[name]
        for key in ("xF", "xD", "xB", "R", "q", "alpha"):
            self._entries[key].set_text(str(data[key]))

    def _export_plot(self):
        if self._result is None:
            self._show_error("请先计算，再导出图片。")
            return

        dialog = Gtk.FileChooserDialog(
            title="导出图片",
            parent=self.window,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_button("取消", Gtk.ResponseType.CANCEL)
        dialog.add_button("保存", Gtk.ResponseType.ACCEPT)
        dialog.set_do_overwrite_confirmation(True)

        png_filter = Gtk.FileFilter()
        png_filter.set_name("PNG 图片 (*.png)")
        png_filter.add_pattern("*.png")
        dialog.add_filter(png_filter)

        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("PDF (*.pdf)")
        pdf_filter.add_pattern("*.pdf")
        dialog.add_filter(pdf_filter)

        svg_filter = Gtk.FileFilter()
        svg_filter.set_name("SVG (*.svg)")
        svg_filter.add_pattern("*.svg")
        dialog.add_filter(svg_filter)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            path = dialog.get_filename()
            ext = os.path.splitext(path)[1].lower()
            try:
                if ext == ".pdf":
                    self._plotter.export_pdf(path)
                elif ext == ".svg":
                    self._plotter.export_svg(path)
                else:
                    self._plotter.export_png(path)
                self._show_info("导出成功", f"图片已保存至:\n{path}")
            except Exception as e:
                self._show_error(f"导出失败: {str(e)}")
        dialog.destroy()

    def _show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.run()
        dialog.destroy()

    def _show_info(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

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
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="使用说明",
        )
        dialog.format_secondary_text(msg)
        dialog.run()
        dialog.destroy()

    def run(self):
        self.app.run(None)


def main():
    app = DistillationGUI()
    app.run()


if __name__ == "__main__":
    main()
