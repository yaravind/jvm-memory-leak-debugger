# Preflight Checklist

Use this checklist before wiring the skill into Codex, Claude, GitHub Copilot,
or another harness.

Core install:

```bash
python3 -m pip install -e . --no-deps
jvm-memory-leak-debugger --help
jvm-memory-leak-debugger --check-runtime --json
```

Package install:

```bash
make package-smoke
```

This verifies a non-editable install from outside the repository, including the
installed CLI, HTTP adapter command, MCP adapter command, and bundled skill
resources.

Optional HTTP bridge:

```bash
python3 -m pip install -e ".[server]"
jvm-memory-leak-debugger-api --help
```

After starting the HTTP bridge, check:

- `GET /health`
- `GET /skill.json`
- `GET /tools`
- `POST /tools/analyze_gc_log` with a small GC log fixture

Optional MCP host:

```bash
python3 -m pip install -e ".[mcp]"
jvm-memory-leak-debugger-mcp --help
```

Runtime readiness:

- `--check-runtime` should report `platform_supported: true`.
- `java_17_plus` must be true before MAT analysis can run.
- `curl_available` must be true for first-run MAT download unless `mat_home`
  points at an existing MAT installation.
- `can_auto_install_mat` should be true on supported Linux, macOS, and Windows
  platforms when MAT is not already installed.
- Run `make test-mat-runtime` or the manual `MAT Runtime Smoke` workflow when
  release-readiness evidence requires live MAT download/unpack validation.

Artifact handling:

- Keep `.hprof` files and GC logs on trusted storage.
- Prefer direct dispatch or MCP when the agent and artifacts are on the same
  machine.
- Use the HTTP bridge only when the transport and host storage are acceptable
  for heap dumps and GC logs.
