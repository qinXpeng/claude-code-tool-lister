# Claude Code Tool Lister

> Instantly scan and inventory everything installed for Claude Code — MCP servers, plugins, slash commands, skills, and system CLIs in PATH.

## Why

Claude Code accumulates tools over time: skills from skillhub, plugins from marketplaces, MCP servers, custom slash commands, and system-level CLIs like `gh`, `docker`, `python`. Keeping track of what's actually available is tedious.

This skill gives you a **single command** that scans and reports the complete inventory in a structured markdown table.

## What it scans

| Category | Source |
|----------|--------|
| 🔌 MCP Servers | `~/.claude/plugins/cache/**/.mcp.json`, `browser-bridge` |
| 🧩 Plugins | `~/.claude/plugins/installed_plugins.json` |
| ⚡ Slash Commands | `~/.claude/commands/*.md` |
| 🎯 Skills | `~/.claude/skills/*/SKILL.md` |
| 🖥️ System CLIs | PATH scan for 50+ known tools (`gh`, `git`, `docker`, `node`, `python`, `kubectl`, `curl`, etc.) |

## Install

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/qinpe/claude-code-tool-lister.git ~/.claude/skills/tool-lister
```

Or use skillhub:

```bash
skillhub install claude-code-tool-lister --dir ~/.claude/skills
```

## Usage

In Claude Code, just type:

```
/tool-lister
```

Or invoke the script directly:

```bash
python ~/.claude/skills/tool-lister/scripts/scan_tools.py
```

### Sample output

```
# Claude Code Tool Inventory

27 skills · 8 commands · 2 plugins · 2 MCPs · 13 system CLIs

## 🔌 MCP Servers
| Name | Command | Args |
|------|---------|------|
| playwright | npx | @playwright/mcp@latest |
| browser-bridge | built-in | — |

## 🧩 Plugins
| playwright@claude-plugins-official | unknown | user |
| last30days@last30days-skill | 3.3.2 | user |

## ⚡ Slash Commands
/spec · /plan · /build · /test · /review · /code-simplify · /ship · /webperf

## 🎯 Skills
akshare-stock · api-and-interface-design · test-driven-development · ... (27 total)

## 🖥️ System CLIs
gh(2.94) · git(2.54) · python(3.14) · node(24.16) · docker(28.5) · kubectl · ...
```

## Requirements

- Python 3.8+ (stdlib only, zero dependencies)
- Claude Code

## License

MIT
