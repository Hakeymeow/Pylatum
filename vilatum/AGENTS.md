# Agent 工作规则

## 1. Git 分支聚焦

Agent 在工作过程中仅专注于当前已检出的 Git 分支，不读取、不比较、不依赖其他分支的任何内容。

## 2. 约定式提交

Git commit message 遵守[约定式提交（Conventional Commits）](https://www.conventionalcommits.org/)规范，格式如下：

```
<type>(<scope>): <description>
```

**scope 字段必填**，且使用 `vo-*` 格式。例如：

- `vo-core`
- `vo-api`
- `vo-cli`
- `vo-hooks`

完整示例：

```
feat(vo-core): add user authentication middleware
fix(vo-api): correct rate limit header parsing
chore(vo-cli): update dev dependencies
```

## 3. 依赖管理

Agent 使用 `uv` 管理项目依赖。所有依赖操作（安装、更新、移除、锁定版本等）均通过 `uv` 命令完成，不使用 `pip`、`pipenv`、`poetry` 等其他工具。

## 4. 工作区限定

Agent 仅在 `vibe-omo` 工作区内执行文件读写、代码生成、命令执行等操作。不得在 `vibe-omo` 目录之外创建、修改或删除任何文件。

### 例外：uv.lock

`uv.lock` 文件不受上述工作区限定规则限制。Agent 因执行 `uv` 命令导致父目录下 `uv.lock` 的创建或修改是允许的，且应将 `uv.lock` 纳入版本管理。

## 5. README.md 内容保护

Agent 不可修改 `README.md` 中 `## Session Record` 部分内的超链接。Agent 可覆盖或修改自己创建的内容，但 `## Session Record` 中的已有超链接不得被覆盖或变更。新内容应在 `## Session Record` 之后追加。
