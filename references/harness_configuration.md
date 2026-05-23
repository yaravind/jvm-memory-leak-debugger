# Harness Configuration Guide

The skill can run with or without MCP. Keep all hosts pointed at the same public
tool contract in `skill.json` and the same shared implementation in
`tools/dispatch.py`.

Supported host styles:

| Host style | Entry point | Notes |
| --- | --- | --- |
| Standalone CLI | `python3 tools/debug_memory_leak.py` or `jvm-memory-leak-debugger` | No optional packages required |
| Direct function dispatch | `tools/dispatch.py` | Use `dispatch_tool(name, params)` from a Python harness |
| Claude MCP | `jvm-memory-leak-debugger-mcp` or `mcp_server.py` | Requires Python 3.10+ and `requirements-mcp.txt` or `.[mcp]` |
| HTTP/FastAPI bridge | `jvm-memory-leak-debugger-api` or `server.py` | Requires `requirements-server.txt` or `.[server]` |
| Codex, Copilot, or other function hosts | `skill.json` plus `dispatch_tool` or `/tools/{name}` | Choose direct dispatch for local agents and HTTP for remote hosts |

Configuration examples live in `harnesses/`:

- `claude_desktop_config.example.json`
- `codex_skill.example.json`
- `copilot_extension.example.json`
- `direct_function_dispatch.example.json`
- `http_bridge.example.json`
- `installed_commands.example.json`

Operational guidance:

- Prefer direct function dispatch when the agent and artifacts are on the same
  machine.
- Prefer `pip install -e .` for local development, `.[mcp]` for MCP hosts, and
  `.[server]` for HTTP bridge hosts.
- Prefer installed commands (`jvm-memory-leak-debugger`,
  `jvm-memory-leak-debugger-api`, and `jvm-memory-leak-debugger-mcp`) in
  reusable harness configuration so hosts do not depend on source-checkout
  paths.
- Use Python 3.10+ for MCP hosts because the current MCP SDK requires it. The
  core CLI and HTTP bridge continue to support Python 3.9+.
- Prefer MCP when a host already supports MCP and local file access is needed.
- Prefer `harnesses/codex_skill.example.json` for Codex-style local tool
  loading where the agent can read local heap and GC artifacts directly.
- Prefer `harnesses/copilot_extension.example.json` for GitHub Copilot
  Extension-style deployments that need HTTPS routes and a compact `/tools`
  catalog.
- Prefer the HTTP bridge when the agent host cannot import local Python modules.
- HTTP hosts can read `GET /skill.json` for the full skill manifest or
  `GET /tools` for a compact route catalog with each tool's POST route and
  parameter schema.
- Do not expose heap dumps or GC logs over a network bridge unless the transport
  and host storage meet the application's security requirements.
- Keep custom recommendation patterns in a separate JSON file and pass the path
  as `patterns_file` or `PATTERNS_FILE`.
- Run `references/preflight_checklist.md` before handing the skill to a new
  harness or operator.
