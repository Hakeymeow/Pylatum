# Vilatum

[**English**](README.md)

**McCabe-Thiele 精馏塔理论塔板数计算工具** — 基于纯 Cairo 渲染的化工分离工程教学与设计辅助软件，使用纯AI编程开发。

计算精馏塔在给定分离要求下的理论塔板数、最小回流比、最佳进料位置，并生成 McCabe-Thiele 图解的 GTK3 桌面应用。无需 matplotlib，所有图表通过 Cairo 直接绘制。

---

## 功能

- **McCabe-Thiele 图解法计算引擎** — 相对挥发度法计算气液平衡曲线、精馏段/提馏段操作线、q 线方程、逐板图解理论板数
- **最小回流比计算** — 自动求解 q 线与平衡线交点
- **全回流最小理论板数** — Fenske 方程验证
- **GTK3 图形界面** — 参数输入、预设案例、实时绘图、结果展示（支持中文）
- **纯 Cairo 渲染** — 无 matplotlib 依赖，支持 PNG / PDF / SVG 三种导出格式
- **可切换计算器模式** — 隐藏图表，仅保留计算面板，适合快速试算

## 化工原理

### McCabe-Thiele 图解法

McCabe-Thiele 法是二元精馏理论塔板数计算的经典图解方法，由 Warren L. McCabe 和 Ernest Thiele 于 1925 年提出。该方法基于两个关键假设：

- **恒摩尔流假设** — 精馏段和提馏段内的气液相摩尔流量分别恒定
- **等摩尔汽化热假设** — 每冷凝一摩尔蒸气所需热量等于汽化一摩尔液体所需热量

### 气液平衡 (VLE)

对于理想二元混合物，平衡时气相组成 *y* 与液相组成 *x* 之间的关系可由相对挥发度 *α* 表达（拉乌尔定律）：

$$
y = \frac{\alpha x}{1 + (\alpha - 1) x}
$$

其中 *α* 为轻关键组分的相对挥发度。平衡曲线（*y* 对 *x* 作图）在 *α* > 1 时向下弯曲，*α* = 1 时与 45° 对角线重合（无法分离）。

### 操作线

**精馏段**（进料以上）操作线描述塔顶的物料平衡：

$$
y = \frac{R}{R + 1} x + \frac{x_D}{R + 1}
$$

其中 *R* 为回流比，*x_D* 为馏出液组成。

**提馏段**（进料以下）操作线描述塔底的物料平衡：

$$
y = \frac{L'}{L' - W} x - \frac{W x_B}{L' - W}
$$

其中 *L'* 为提馏段液相流量，*W* 为釜液流量，*x_B* 为釜液组成。

### q 线（进料线）

q 线描述进料板处气液流量的变化：

$$
y = \frac{q}{q - 1} x - \frac{x_F}{q - 1}
$$

参数 *q* 代表进料的热状态：

| q 值 | 进料状态 |
|------|---------|
| q > 1 | 过冷液体 — 更多液体进入提馏段 |
| q = 1 | 饱和液体 — 泡点进料 |
| 0 < q < 1 | 气液混合物 |
| q = 0 | 饱和蒸气 — 露点进料 |
| q < 0 | 过热蒸气 — 更多蒸气进入精馏段 |

q 线与平衡曲线的交点决定了**最小回流比** *R_min*，即实现指定分离要求所需的最小回流比。

### 逐板图解（阶梯构造）

从对角线上 *x_D* 点出发，交替进行以下操作：

1. 水平移动至操作线（得到操作线上的 *y*）
2. 竖直移动至平衡曲线（得到一个平衡级后的新 *x*）

每个完整的阶梯代表一个理论板。当 *x* 降至 *x_B* 以下时结束。阶梯数减一（扣除再沸器）即为理论塔板数。

### Fenske 方程（全回流）

在全回流（*R* → ∞）条件下，最小理论板数 *N_min* 由 Fenske 方程给出：

$$
N_{\min} = \frac{\log\left[\frac{x_D}{1 - x_D} \cdot \frac{1 - x_B}{x_B}\right]}{\log \alpha}
$$

该值作为下限校验：有限回流比下的实际塔板数必定大于 *N_min*。

## 快速开始

### 系统依赖

```bash
# Ubuntu/Debian
sudo apt install libgtk-3-dev libcairo2-dev libglib2.0-dev \
                 libgirepository1.0-dev libpango1.0-dev
```

### 安装与运行

```bash
# 使用 uv（推荐）
uv sync
uv run vi-gui

# 或使用 pip
pip install -e .
vi-gui
```

> 若无 display 环境，可使用 `xvfb-run uv run vi-gui` 无头运行。

## 用法

### GUI 模式

启动后界面包含左侧参数面板和右侧 McCabe-Thiele 图表：

1. 输入操作参数：进料组成 xF、馏出液组成 xD、釜液组成 xB、回流比 R、进料热状态 q、相对挥发度 α
2. 选择**预设案例**快速填充参数（苯-甲苯、乙醇-水、甲醇-水、丙酮-苯）
3. 点击**开始计算**或按 `Enter` 键执行
4. 在**视图**菜单中切换图表显示（计算器模式）
5. 通过**文件 → 导出图片**或 `Ctrl+E` 导出图表为 PNG / PDF / SVG

### 编程调用

```python
from vilatum.distillation import McCabeThiele, CairoPlotter

# 创建计算器（苯-甲苯体系）
calc = McCabeThiele(xF=0.45, xD=0.97, xB=0.02, R=2.0, q=1.0, alpha=2.50)
result = calc.calculate()

print(f"理论塔板数 N = {result.n_stages}")
print(f"精馏段塔板数 = {result.n_rectifying}")
print(f"提馏段塔板数 = {result.n_stripping}")
print(f"最佳进料位置 = {result.feed_stage}")
print(f"最小回流比 R_min = {result.r_min:.4f}")
print(f"最小理论板数 N_min = {result.n_min}")

# 导出图表
plotter = CairoPlotter(result)
plotter.export_png("mccabe-thiele.png")
plotter.export_pdf("mccabe-thiele.pdf")
plotter.export_svg("mccabe-thiele.svg")
```

## 包结构

```
vilatum/
├── pyproject.toml
├── src/vilatum/
│   ├── __init__.py
│   └── distillation/
│       ├── __init__.py    # 导出 McCabeThiele, McCabeThieleResult, CairoPlotter
│       ├── core.py        # McCabe-Thiele 计算引擎
│       ├── gui.py         # GTK3 桌面应用
│       └── plotter.py     # Cairo 纯渲染器
└── tests/
    ├── conftest.py        # 共享 fixtures
    ├── test_plotter.py    # 绘图器测试（含像素级断言）
    └── test_gui.py        # GUI 冒烟测试
```

## API 参考

### `McCabeThiele`

参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `xF` | float | 进料中轻组分摩尔分数 (0 < xF < 1) |
| `xD` | float | 馏出液中轻组分摩尔分数 (xF < xD < 1) |
| `xB` | float | 釜液中轻组分摩尔分数 (0 < xB < xF) |
| `R` | float | 实际回流比 (> 0) |
| `q` | float | 进料热状态参数 |
| `alpha` | float | 相对挥发度 (> 1) |
| `n_eq_points` | int | 平衡曲线离散点数 (默认 1001) |

q 值含义：

| q 值 | 含义 |
|------|------|
| q > 1 | 过冷液体 |
| q = 1 | 饱和液体 |
| 0 < q < 1 | 气液混合物 |
| q = 0 | 饱和蒸汽 |
| q < 0 | 过热蒸汽 |

### `McCabeThieleResult`

返回的计算结果 dataclass，包含理论塔板数、操作线参数、逐板坐标等全部信息。

### `CairoPlotter`

| 方法 | 说明 |
|------|------|
| `draw(ctx, width, height)` | 渲染到任意 Cairo Context |
| `export_png(path, width, height)` | 导出 PNG |
| `export_pdf(path, width, height)` | 导出 PDF |
| `export_svg(path, width, height)` | 导出 SVG |

## 测试

```bash
# 运行全部测试
uv run pytest

# 运行单个测试文件
uv run pytest vilatum/tests/test_plotter.py

# 运行 GUI 测试（需要 display）
xvfb-run uv run pytest vilatum/tests/test_gui.py
```

## 技术栈

| 方面 | 详情 |
|------|------|
| Python | >= 3.13 |
| 包管理 | uv |
| 构建系统 | setuptools >= 75 |
| 运行时依赖 | numpy >= 2.0, PyGObject >= 3.56.2 (含 PyCairo) |
| 开发依赖 | pytest >= 9.0.3 |
| 图形后端 | Cairo (无 matplotlib) |
| GUI 框架 | GTK3 (PyGObject) |

## 许可证

[MIT](../LICENSE)

---

## Record of Sessions
- [[/init#1]](https://opncd.ai/share/G9PLazNs): 为AI agent制定基本的开发规则。
- [[implementation]](https://opncd.ai/share/ZK85qRaR): 开发程序。
- [[feat: optional chart#1]](https://opncd.ai/share/rYakUmXb): 为图形界面中的可视化图表增加折叠功能，但似乎被AI误解了。 
- [[feat: optional chart#2]](https://opncd.ai/share/hN0h1xHE): 从上一个会话中分支出来的会话，将提示词中的“可折叠”更改为“可选”。
- [[/init#2]](https://opncd.ai/share/eE9OggzI): 更新AGENTS.md。
