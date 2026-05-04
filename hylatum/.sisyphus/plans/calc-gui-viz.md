# McCabe-Thiele Visualization for GUI

## TL;DR

> **快速摘要**: 为 calc_gui.py 添加 McCabe-Thiele 图可视化 (平衡线+操作线+阶梯)，使用 JavaScript Canvas
> 
> **交付物**: 
> - calc_gui.py (新增 visualization API)
> - index.html (新增 Canvas + 绘图逻辑)
> 
> **估计工作量**: 中 | **并行执行**: 否 (顺序)

---

## Context

### 原始请求
用户要求参照 demo.py 在界面中添加可视化

### 访谈总结
**关键讨论**:
- 可视化内容: 完整图解 (平衡线+操作线+阶梯)
- 技术方案: JavaScript Canvas
- 更新时机: 点击计算后更新
- 阶梯显示: 显示所有理论板

### 技术背景
- calc_gui.py 已完成，包含 6 个参数输入和计算功能
- demo.py 展示了 McCabe-Thiele 图的数学逻辑
- pywebview 支持 JavaScript Canvas 渲染

---

## Work Objectives

### 核心目标
在 calc_gui.py 的 Web 界面中添加 McCabe-Thiele 图可视化

### 具体交付物
- calc_gui.py: 新增 `visualization()` API 方法，返回所有线条数据点
- index.html: 新增 Canvas 元素 + 绘制 McCabe-Thiele 图的 JavaScript
- 集成: 计算完成后自动更新图表

### 完成定义
- [ ] 点击计算后 Canvas 显示完整 McCabe-Thiele 图
- [ ] 图表包含: 对角线 + 平衡线 + 3条操作线 + 阶梯
- [ ] 无控制台错误

### 必须有
- 对角线 y=x (灰色)
- 平衡线 y = αx/(1+(α-1)x) (红色)
- 精馏线 y = R/(R+1)*x + xD/(R+1) (蓝色)
- q线 y = q/(q-1)*x - xF/(q-1) (黄色)
- 提馏线 (连接点与 xW) (绿色)
- 阶梯 (水平/垂直线) (紫色/橙色)

### 禁止 (防护栏)
- 无实时更新 (用户要求点击后更新)
- 无复杂动画 (保持简洁)

---

## Execution Strategy

### Wave 1 (Python API - 立即开始)
```
1. calc_gui.py - 新增 visualization() API
```

### Wave 2 (JavaScript Canvas - 依赖 Wave 1)
```
2. index.html - 新增 Canvas + 绘图逻辑
```

### Wave 3 (集成 - 依赖 Wave 2)
```
3. 计算后自动更新图表
```

---

## TODOs

- [x] 1. **calc_gui.py - 新增 visualization API**

  **实现**:
  - 新增 `visualization(R, q, alpha, xD, xF, xW)` 方法
  - 返回所有线条数据点: diagonal, equilibrium, rectifying, qline, stripping, stepping
  - 暴露给 pywebview.api

- [x] 2. **index.html - 新增 Canvas + 绘图**

  **实现**:
  - 新增 Canvas 元素 (500x500px)
  - 编写 drawMcCabeThiele(data) 函数
  - 绘制所有线条组件
  - 绑定到 Calculate 按钮

- [x] 3. **集成 - 自动更新图表**

  **实现**:
  - Calculate 点击后调用 visualization()
  - 调用 Canvas 绘制函数

---

## Success Criteria

### 验证命令
```bash
cd /home/PomeloFish/Code/PlateNum/hybrid
uv run python calc_gui.py
# 输入参数 → 点击计算 → 查看图表
```

### 最终检查表
- [x] Canvas 显示所有 6 种线条
- [x] 点击计算后图表更新
- [x] 阶梯显示完整理论板数