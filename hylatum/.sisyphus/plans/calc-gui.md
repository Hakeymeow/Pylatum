# Plan: calc.py GUI 前端界面

## TL;DR

> **快速摘要**: 使用 pywebview 为 calc.py 创建桌面 GUI，输入参数后返回理论板数结果
> 
> **交付物**: 
> - calc_gui.py (主程序)
> - index.html (前端界面)
> 
> **估计工作量**: 小 | **并行执行**: 否 (顺序执行)

---

## Context

### 原始请求
用户调用 Read tool 读取 calc.py 后要求制作前端界面 calc_gui.py

### 访谈总结
**关键讨论**:
- 界面风格: 基础表单+结果面板
- 参数验证: 提交时验证  
- 输出格式: 纯数值结果 (Nt, Nf, Nr, Ns)

### 技术背景
- pywebview[gtk] 已在 pyproject.toml 依赖中
- calc.py 是纯计算库，无状态，单次调用

---

## Work Objectives

### 核心目标
为 calc.py 创建 pywebview GUI，用户输入参数后返回理论板数计算结果

### 具体交付物
- calc_gui.py: 启动 pywebview 窗口，暴露计算 API 给前端
- index.html: 输入表单 + 结果显示面板

### 完成定义
- [ ] 双击 calc_gui.py 打开窗口
- [ ] 输入 6 个参数后点击计算返回正确结果
- [ ] 结果与 calc.py 命令行行为一致

### 必须有
- 参数输入: R, q, alpha, xD, xF, xW
- 输出: Nt, Nf, Nr, Ns (理论板数)

### 禁止 (防护栏)
- 无复杂实时验证 (用户要求提交时验证)
- 无中间过程数据 (用户要求纯数值)
- 无复杂 UI 样式

---

## Execution Strategy

### Wave 1 (立即开始 - 核心)
```
1. calc_gui.py - pywebview 窗口 + 暴露 calc 函数给 JS API
2. index.html - 基础表单 + 结果面板
```

---

## TODOs

- [x] 1. **calc_gui.py - 主程序**

  **实现**:
  - 导入 webview, calc 模块
  - 创建 `calculate(R, q, alpha, xD, xF, xW)` 函数调用 calc.py 并返回结果
  - 暴露给 pywebview.api
  - 启动窗口加载 index.html

- [x] 2. **index.html - 前端界面**

  **实现**:
  - 6 个输入框: R, q, α (alpha), xD, xF, xW
  - 计算按钮
  - 结果表格: Nt, Nf, Nr, Ns
  - 使用 pywebview.api.calculate() 调用后端

---

## Success Criteria

### 验证命令
```bash
cd /home/PomeloFish/Code/PlateNum/hybrid
python calc_gui.py
# 窗口应打开，输入参数后显示结果
```

### 最终检查表
- [x] calc_gui.py 运行无报错
- [x] 结果与 calc.py 命令行输出一致