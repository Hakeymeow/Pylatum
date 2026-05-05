# Agent 工作规则

## 1. Git 分支聚焦

Agent 在工作过程中仅专注于当前已检出的 Git 分支，不读取、不比较、不依赖其他分支的任何内容。

## 2. 约定式提交

Git commit message 遵守[约定式提交（Conventional Commits）](https://www.conventionalcommits.org/)规范，格式如下：

```
<type>(<scope>): <description>
```

**scope 字段必填**，且使用 `vi-*` 格式。例如：

- `vi-core` — 计算引擎（core.py）
- `vi-gui` — GTK3 界面（gui.py）
- `vi-plotter` — Cairo 渲染器（plotter.py）
- `vi-distillation` — 蒸馏子包整体
- `vi-hooks` — 未使用，保留
- `vi-cli` — 未使用，保留

完整示例：

```
feat(vi-core): add user authentication middleware
fix(vi-gui): correct rate limit header parsing
chore(vi-distillation): update dependencies
```

## 3. 依赖管理

Agent 使用 `uv` 管理项目依赖。所有依赖操作（安装、更新、移除、锁定版本等）均通过 `uv` 命令完成，不使用 `pip`、`pipenv`、`poetry` 等其他工具。

- 添加依赖：`uv add <package>`（在工作区根目录 `/home/PomeloFish/Code/Pylatum` 执行）
- 移除依赖：`uv remove <package>`
- 同步环境：`uv sync`
- 查看依赖树：`uv tree`

## 4. 工作区限定

Agent 仅在 `vilatum` 工作区内执行文件读写、代码生成、命令执行等操作。不得在 `vilatum` 目录之外创建、修改或删除任何文件。不需要在根目录生成`AGENTS.md`。

### 例外：uv.lock

`uv.lock` 文件不受上述工作区限定规则限制。Agent 因执行 `uv` 命令导致父目录下 `uv.lock` 的创建或修改是允许的，且应将 `uv.lock` 纳入版本管理。`uv.lock` 位于工作区根目录 `/home/PomeloFish/Code/Pylatum/uv.lock`，而非 `vilatum/` 内部。

## 5. README.md 内容保护

Agent 不可修改 `README.md` 中 `## Record of Sessions` 部分内的超链接。Agent 可覆盖或修改自己创建的内容，但 `## Record of Sessions` 中的已有超链接不得被覆盖或变更。新内容应在 `## Record of Sessions` 之后追加。

## 6. 包结构

```
vilatum/src/vilatum/distillation/
├── __init__.py   导出: McCabeThiele, McCabeThieleResult, CairoPlotter
├── core.py       McCabe-Thiele 计算引擎（McCabeThiele 类 + McCabeThieleResult dataclass）
├── gui.py        GTK3 桌面应用（DistillationGUI 类, main() 入口）
└── plotter.py    Cairo 纯渲染器（CairoPlotter, 无 matplotlib 依赖）
```

### 入口点

`[project.scripts]` 中注册了 `vi-gui` 命令：

```
vi-gui = "vilatum.distillation.gui:main"
```

运行方式：`uv run vi-gui`（需 display 环境）。

## 7. 测试

使用 `pytest` 作为测试框架。

- **运行所有测试**：`uv run pytest`（在 `/home/PomeloFish/Code/Pylatum` 工作区根目录执行）
- **运行单个测试文件**：`uv run pytest vilatum/tests/test_plotter.py`
- **运行单个测试类**：`uv run pytest vilatum/tests/test_plotter.py::TestFullChart`

### 测试注意事项

- 部分 GUI 测试需要 DISPLAY 环境变量（使用 `xvfb-run` 无头运行）
- 执行 `uv sync` 安装 editable 包后再运行测试
- `conftest.py` 提供共享 fixtures：`result_benzene_toluene`、`result_ethanol_water`、`result_q_lt_1`、`render_surface`
- 绘图器测试使用 Cairo `ImageSurface` 进行像素级断言验证渲染结果

## 8. 技术栈

| 方面 | 详情 |
|------|------|
| Python | `>=3.13`（`.python-version` 锁定） |
| 包管理 | `uv`（工作区根目录 `/home/PomeloFish/Code/Pylatum` 执行命令） |
| 构建系统 | setuptools `>=75`，`build-backend = "setuptools.build_meta"` |
| 包布局 | src-layout：代码在 `vilatum/src/vilatum/` |
| 运行时依赖 | `numpy>=2.0`、`pygobject>=3.56.2`（含 `pycairo`） |
| 开发依赖 | `pytest>=9.0.3` |
| PyPI 镜像 | `https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/`（默认 uv index） |
| 代码规范 | 无 linting/formatter/CI/pre-commit/tox/Makefile 配置 |

### 系统依赖

`pygobject`（GTK3 绑定）需要系统安装以下库：
- GTK3 开发库（`libgtk-3-dev`）
- Cairo 开发库（`libcairo2-dev`）
- GLib 开发库（`libglib2.0-dev`）
- GObject  introspection（`libgirepository1.0-dev`）
- Pango 开发库（`libpango1.0-dev`）

## 9. 已知注意事项

- **`vibe_omo` → `vilatum` 重命名**：已完成。测试文件中的 import 已统一改为 `vilatum.distillation.*`。
- **工作区边界**：`hylatum/` 目录是与 `vilatum` 同级的工作区成员，Agent 不应读取或修改其中内容。
- **异步渲染**：GUI 中的图表通过 GTK DrawingArea 和 Cairo 绘制，无 matplotlib 依赖。
- **导出格式**：`CairoPlotter` 支持 PNG、PDF、SVG 三种导出格式。
