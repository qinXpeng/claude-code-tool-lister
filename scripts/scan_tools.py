#!/usr/bin/env python
"""Scan all tools available to Claude Code — skills, plugins, MCPs, CLIs, commands.

Outputs a structured markdown report to stdout.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Fix Windows GBK encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

CLAUDE_HOME = Path.home() / ".claude"


def parse_yaml_frontmatter(text: str) -> dict:
    """Parse YAML-style frontmatter between --- markers. Returns dict of top-level keys."""
    result = {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return result
    end = 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end == 0:
        return result
    for line in lines[1:end]:
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            result[key] = val
    return result


def scan_skills(skills_dir: Path) -> list[dict]:
    """Scan skills directory for installed skills."""
    results = []
    if not skills_dir.exists():
        return results
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        frontmatter = {}
        meta = {}
        meta_path = d / "_meta.json"
        skill_md = d / "SKILL.md"

        # Parse SKILL.md frontmatter (primary source for name/description)
        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding="utf-8")
                frontmatter = parse_yaml_frontmatter(content)
            except OSError:
                pass

        # _meta.json as fallback
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # description priority: frontmatter > _meta.json
        desc = frontmatter.get("description") or meta.get("description", "")
        version = frontmatter.get("version") or meta.get("version", "")

        results.append({
            "name": d.name,
            "description": desc,
            "version": version,
        })
    return results


def scan_commands(commands_dir: Path) -> list[dict]:
    """Scan slash commands directory."""
    results = []
    if not commands_dir.exists():
        return results
    for f in sorted(commands_dir.glob("*.md")):
        desc = ""
        try:
            content = f.read_text(encoding="utf-8")
            frontmatter = parse_yaml_frontmatter(content)
            desc = frontmatter.get("description", "")
        except OSError:
            pass
        results.append({
            "name": f"/{f.stem}",
            "description": desc,
        })
    return results


def scan_plugins() -> list[dict]:
    """Scan installed plugins."""
    results = []
    plugins_json = CLAUDE_HOME / "plugins" / "installed_plugins.json"
    if not plugins_json.exists():
        return results
    try:
        data = json.loads(plugins_json.read_text(encoding="utf-8"))
        for plugin_id, entries in data.get("plugins", {}).items():
            for entry in entries:
                results.append({
                    "name": plugin_id,
                    "version": entry.get("version", ""),
                    "scope": entry.get("scope", ""),
                })
    except (json.JSONDecodeError, OSError):
        pass
    return results


def scan_mcp_servers() -> list[dict]:
    """Scan active MCP server configurations."""
    results = []
    seen = set()

    # 1. Read ~/.claude.json for user-level MCP servers
    claude_json = CLAUDE_HOME.parent / ".claude.json"
    if claude_json.exists():
        try:
            data = json.loads(claude_json.read_text(encoding="utf-8"))
            for name, config in data.get("mcpServers", {}).items():
                if name in seen:
                    continue
                seen.add(name)
                cmd = config.get("command", "")
                args = " ".join(config.get("args", []))
                results.append({
                    "name": name,
                    "command": cmd,
                    "args": args,
                })
        except (json.JSONDecodeError, OSError):
            pass

    # 2. Walk cache/** for .mcp.json files (plugin MCPs)
    cache_dir = CLAUDE_HOME / "plugins" / "cache"
    if cache_dir.exists():
        for mcp_json in cache_dir.glob("**/.mcp.json"):
            try:
                mcp_data = json.loads(mcp_json.read_text(encoding="utf-8"))
                for name, config in mcp_data.items():
                    if name in seen:
                        continue
                    seen.add(name)
                    results.append({
                        "name": name,
                        "command": config.get("command", ""),
                        "args": " ".join(config.get("args", [])),
                    })
            except (json.JSONDecodeError, OSError):
                pass

    # 3. Fallback: browser-bridge token exists but no config found
    bb_token = CLAUDE_HOME / "browser-bridge-token"
    if bb_token.exists() and "browser-bridge" not in seen:
        results.append({
            "name": "browser-bridge",
            "command": "browser-bridge (token found, MCP not registered)",
            "args": "",
        })

    return results


# Known useful CLIs to check
KNOWN_CLIS = [
    ("gh", "GitHub CLI"),
    ("git", "Git version control"),
    ("python", "Python interpreter"),
    ("python3", "Python 3 interpreter"),
    ("node", "Node.js runtime"),
    ("npm", "Node package manager"),
    ("pnpm", "pnpm package manager"),
    ("yarn", "Yarn package manager"),
    ("bun", "Bun runtime"),
    ("docker", "Docker CLI"),
    ("kubectl", "Kubernetes CLI"),
    ("gcloud", "Google Cloud CLI"),
    ("aws", "AWS CLI"),
    ("az", "Azure CLI"),
    ("terraform", "Terraform IaC"),
    ("go", "Go compiler"),
    ("cargo", "Rust package manager"),
    ("rustc", "Rust compiler"),
    ("java", "Java runtime"),
    ("javac", "Java compiler"),
    ("gcc", "GNU C compiler"),
    ("make", "Make build tool"),
    ("cmake", "CMake build system"),
    ("curl", "HTTP client"),
    ("wget", "HTTP downloader"),
    ("jq", "JSON processor"),
    ("rg", "ripgrep search"),
    ("fd", "fd file finder"),
    ("fzf", "Fuzzy finder"),
    ("ssh", "SSH client"),
    ("scp", "Secure copy"),
    ("rsync", "Remote sync"),
    ("npx", "Node package runner"),
    ("pip", "Python package installer"),
    ("uv", "Python package manager (uv)"),
    ("deno", "Deno runtime"),
    ("psql", "PostgreSQL CLI"),
    ("mysql", "MySQL CLI"),
    ("sqlite3", "SQLite CLI"),
    ("redis-cli", "Redis CLI"),
    ("mongosh", "MongoDB Shell"),
    ("skillhub", "Claude Code skill marketplace CLI"),
    ("heroku", "Heroku CLI"),
    ("fly", "Fly.io CLI"),
    ("vercel", "Vercel CLI"),
    ("netlify", "Netlify CLI"),
    ("cf", "Cloudflare CLI"),
    ("doctl", "DigitalOcean CLI"),
    ("supabase", "Supabase CLI"),
    ("firebase", "Firebase CLI"),
    ("dotnet", ".NET CLI"),
    ("gradle", "Gradle build tool"),
    ("mvn", "Maven build tool"),
]


def _find_cmd(cmd: str) -> str | None:
    """Like shutil.which but also finds extension-less files on Windows."""
    path = shutil.which(cmd)
    if path:
        return path
    # On Windows, shutil.which only matches PATHEXT extensions. Fall back to
    # checking PATH manually for extension-less executables (e.g. bash scripts).
    if sys.platform == "win32":
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for d in path_dirs:
            candidate = Path(d) / cmd
            try:
                if candidate.is_file():
                    return str(candidate)
            except OSError:
                pass
    return None


def scan_system_clis() -> list[dict]:
    """Scan PATH for known useful CLIs."""
    results = []
    for cmd, desc in KNOWN_CLIS:
        path = _find_cmd(cmd)
        if path:
            # Try to get version (best-effort, 2s timeout)
            version = ""
            try:
                r = subprocess.run(
                    [cmd, "--version"], capture_output=True, text=True, timeout=2
                )
                version = r.stdout.strip().splitlines()[0][:80]
            except Exception:
                pass
            results.append({
                "name": cmd,
                "description": desc,
                "path": path,
                "version": version,
            })
    return results


def main():
    skills = scan_skills(CLAUDE_HOME / "skills")
    commands = scan_commands(CLAUDE_HOME / "commands")
    plugins = scan_plugins()
    mcps = scan_mcp_servers()
    clis = scan_system_clis()

    print("# Claude Code Tool Inventory\n")
    print(f"*Generated by tool-lister skill — {len(skills)} skills, {len(commands)} commands, {len(plugins)} plugins, {len(mcps)} MCPs, {len(clis)} system CLIs*\n")

    print("## 🔌 MCP Servers\n")
    if mcps:
        print("| Name | Command | Args |")
        print("|------|---------|------|")
        for m in mcps:
            print(f"| **{m['name']}** | `{m['command']}` | `{m['args']}` |")
    else:
        print("*(none)*")
    print()

    print("## 🧩 Plugins\n")
    if plugins:
        print("| Plugin | Version | Scope |")
        print("|--------|---------|-------|")
        for p in plugins:
            print(f"| `{p['name']}` | {p['version']} | {p['scope']} |")
    else:
        print("*(none)*")
    print()

    print("## ⚡ Slash Commands\n")
    if commands:
        for c in commands:
            print(f"- **{c['name']}** — {c['description']}")
    else:
        print("*(none)*")
    print()

    print("## 🎯 Skills\n")
    if skills:
        for s in skills:
            v = f" (v{s['version']})" if s['version'] else ""
            print(f"- **{s['name']}**{v} — {s['description']}")
    else:
        print("*(none)*")
    print()

    print("## 🖥️ System CLIs\n")
    if clis:
        print("| CLI | Description | Version | Path |")
        print("|-----|-------------|---------|------|")
        for c in clis:
            v = c['version'][:60] if c['version'] else "-"
            print(f"| `{c['name']}` | {c['description']} | {v} | `{c['path']}` |")
    else:
        print("*(none)*")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
