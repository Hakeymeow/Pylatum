# Plan: Upgrade Chart to Plotly

## TL;DR

> **快速摘要**: 在 Python 端使用 Plotly 生成交互式图表 HTML，嵌入 index.html 显示
> 
> **交付物**: 
> - calc_gui.py (新增 Plotly HTML 生成)
> - index.html (显示 Plotly 图表)
> 
> **估计工作量**: 小 | **并行执行**: 否

---

## Context

### 原始请求
用户要求升级图表，使用 Plotly 生成 HTML 嵌入到 index.html

### 技术背景
- pywebview 支持加载 HTML 字符串或 URL
- Plotly Python 可以生成独立 HTML 文件
- 当前使用 JavaScript Canvas 绘制

### 依赖
- 需要添加 `plotly` 到 pyproject.toml 依赖

---

## Work Objectives

### 核心目标
用 Plotly 交互式图表替代现有 Canvas 图表

### 完成定义
- [ ] Plotly 图表在 GUI 中显示
- [ ] 图表支持缩放、悬停提示等交互
- [ ] 点击计算后图表更新

### 必须有
- 平衡线 (红色)
- 精馏线 (蓝色)
- q 线 (黄色)
- 提溯线 (绿色)
- 阶梯 (紫色虚线)
- 对角线 (灰色)

### 禁止 (防护栏)
- 无离线 CDN (使用 plotly 生成的完整 HTML)

---

## Execution Strategy

### Wave 1
```
1. calc_gui.py - 新增 Plotly HTML 生成方法
2. index.html - 替换 Canvas 为 Plotly 容器
```

---

## TODOs

- [ ] 1. **添加 plotly 依赖**

  **实现**:
  - 在 pyproject.toml 添加 plotly

- [ ] 2. **calc_gui.py - 新增 Plotly HTML 生成**

  **实现**:
  - 新增 `plotly_chart(R, q, alpha, xD, xF, xW)` 方法
  - 返回 Plotly 生成的完整 HTML 字符串

- [ ] 3. **index.html - 显示 Plotly 图表**

  **实现**:
  - 移除 Canvas
  - 添加 div 容器
  - 调用 Plotly API 渲染图表

---

## Success Criteria

### 验证命令
```bash
cd /home/PomeloFish/Code/PlateNum/hybrid
uv sync
uv run python calc_gui.py
```

### 最终检查表
- [ ] Plotly 图表显示
- [ ] 支持缩放、悬停交互
- [ ] 点击计算后图表更新