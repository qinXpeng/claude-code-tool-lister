---
name: tool-lister
description: Scans and inventories all tools available to Claude Code — MCP servers, plugins, slash commands, skills, and system CLIs in PATH. Use when asked "what tools are installed", "list capabilities", or when you need a full inventory before starting work.
---

# tool-lister

Scan and inventory all tools available to Claude Code:
- MCP servers (browser-bridge, playwright, etc.)
- Installed plugins
- Slash commands (/spec, /plan, /build, etc.)
- Skills (from ~/.claude/skills/)
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
python ~/.claude/skills/tool-lister/scripts/scan_tools.py
```

The script outputs a structured markdown report. Present the results to the user in a clean format.

## Script location

`scripts/scan_tools.py` — pure Python, no dependencies beyond stdlib.
