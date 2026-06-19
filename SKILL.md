---
name: tool-lister
description: Scans and inventories all tools available to Claude Code — MCP servers, plugins, slash commands, skills, and system CLIs in PATH. Use when asked "what tools are installed", "list capabilities", or when you need a full inventory before starting work.
---

# tool-lister

Scan and inventory all tools available to Claude Code:
- MCP servers (browser-bridge, playwright, etc.)
- Installed plugins
- Slash commands (/spec, /plan, /build, etc.)
- Skills (from ~/.claude/skills/ and ~/.agents/skills/)
- System-level CLIs in PATH (gh, git, docker, python, node, etc.)

## When to use

Invoke this skill when:
- The user asks "what tools are installed", "what can I use", "list skills/plugins/MCPs"
- You need to know the full tool inventory before starting a task
- Starting a new session and need a quick overview of capabilities
- The user asks for "capabilities", "installed tools", "available commands"

## How to invoke

Run the scan script:

```bash
python /c/Users/qinpe/.agents/skills/tool-lister/scripts/scan_tools.py
```

## Script location

`scripts/scan_tools.py` — pure Python, no dependencies beyond stdlib.

## Output format (MANDATORY)

When presenting results, **MUST** follow this exact format. List every single item — no abbreviations, no "and more", no grouping that hides names.

### Overall header

```
## 全部工具清单 — N skills · N commands · N plugins · N MCPs · N CLIs
```

### Section 1: MCP Servers

Table with columns: # | 名称 | 命令 | 参数

```
### 🔌 MCP Servers (N)

| # | 名称 | 命令 | 参数 |
|---|------|------|------|
| 1 | **name** | `command` | `args` |
```

### Section 2: Plugins

Table with columns: # | 插件 | 版本 | 来源 | 作用域

```
### 🧩 Plugins (N)

| # | 插件 | 版本 | 来源 | 作用域 |
|---|------|------|------|--------|
| 1 | `name@marketplace` | version | marketplace | scope |
```

### Section 3: Slash Commands

Numbered list with description. Split into two groups:
- 开发流程: /spec /plan /build /test
- 审查与发布: /review /code-simplify /ship /webperf

```
### ⚡ Slash Commands (N)

| # | 命令 | 用途 |
|---|------|------|
| 1 | `/spec` | 结构化需求规格，先写规格再写代码 |
| 2 | `/plan` | 拆分为小任务，含依赖排序和验收标准 |
...
```

### Section 4: Skills

**MUST sub-categorize** skills into these groups, each with numbered entries continuing across groups:

1. **自定义** — user-installed skills (akshare-stock, fliggy-travel-new, 12306, etc.)
2. **需求与设计** — interview-me, idea-refine, spec-driven-development, planning-and-task-breakdown
3. **构建与实现** — incremental-implementation, source-driven-development, doubt-driven-development, context-engineering, frontend-ui-engineering, api-and-interface-design
4. **测试与调试** — test-driven-development, browser-testing-with-devtools, debugging-and-error-recovery
5. **代码审查** — code-review-and-quality, code-simplification, security-and-hardening, performance-optimization
6. **发布与运维** — git-workflow-and-versioning, ci-cd-and-automation, deprecation-and-migration, documentation-and-adrs, observability-and-instrumentation, shipping-and-launch
7. **元技能** — using-agent-skills

Format each sub-category as:

```
### 🎯 Skills — 分类名 (N)

| # | 名称 | 版本 | 描述 |
|---|------|------|------|
| 1 | **name** | v1.0.0 | One-line description in Chinese/English matching the skill's own description |
```

Rules:
- **Every skill gets its own numbered row.** No "和 more" or grouping.
- Description = 1 line max, taken from the skill's frontmatter or _meta.json.
- Version column: show only if version exists; use `—` if none.
- The numbering continues across sub-categories (1–30, not resetting per group).

### Section 5: System CLIs

Table with columns: # | CLI | 版本 | 路径

```
### 🖥️ System CLIs (N)

| # | CLI | 版本 | 路径 |
|---|-----|------|------|
| 1 | `gh` | 2.94.0 | `C:\Program Files\GitHub CLI\gh.EXE` |
```

### Footer

```
**总计：N skills（X 自定义 + Y 内置）· N 命令 · N 插件 · N MCP · N CLI**
```
