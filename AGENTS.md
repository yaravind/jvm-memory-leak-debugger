# Agent Operating Guide

## Project Intent

`jvm-memory-leak-debugger` is an agent skill and standalone Python CLI for
diagnosing JVM out-of-memory failures from two artifacts:

- a `.hprof` heap dump
- a G1 unified GC log

The skill identifies GC pressure, correlates the heap dump timestamp to the GC
timeline, runs Eclipse Memory Analyzer (MAT) for heap suspects, matches known
leak patterns, and writes:

- `report.json` as the machine-readable source of truth
- `report.md` as the human-readable report

The public tool surface is defined in `skill.json`:

- `analyze_gc_log`
- `extract_heap_suspects`
- `correlate_dump_to_gc`
- `generate_report`

## Structure

- `tools/debug_memory_leak.py` is the primary orchestrator. It parses the GC
  log, correlates the dump, optionally runs MAT, builds recommendations, and
  writes reports.
- `tools/gc_parser.py`, `tools/correlator.py`, `tools/mat_runner.py`, and
  `tools/reporter.py` contain the core behavior.
- `mcp_server.py` and `server.py` are thin runtime adapters for Claude MCP and
  HTTP/FastAPI-style tool hosting.
- `schemas/` contains JSON output contracts for GC analysis and full memory
  leak reports.
- `tests/fixtures/gc-16615.log` is a real incident fixture used by the E2E GC
  tests.
- `scripts/` contains standalone wrappers and helper scripts for local use.

## Development Conventions

- Prefer Python stdlib-only changes for core tools. Optional runtime adapters
  may depend on their own packages, such as `mcp`, `fastapi`, or `uvicorn`.
- Treat `report.json` as the durable output contract. Markdown report changes
  should preserve the same underlying structured facts.
- Do not parse `.hprof` binaries directly. Use Eclipse MAT through
  `tools/mat_runner.py` or the MAT helper script.
- Do not fabricate heap, GC, or artifact statistics when required inputs are
  missing. Surface the missing artifact clearly.
- Keep runtime adapters thin. Shared behavior belongs in `tools/`.
- Avoid staging or committing changes unless the user explicitly asks.

## Verification

Use these commands from the repository root:

```bash
make test
make validate-manifests
make test-e2e-gc
```

`make test-e2e-full` requires a real `.hprof` through `HPROF_PATH` or a
fixture symlink and should only be used when that artifact is available.

Baseline verification on 2026-05-23:

- `make test` passed with 26 selected tests and 3 full E2E tests deselected.
- `make validate-manifests` passed.

## Current Audit Notes

- `instructions/system_prompt.md` is currently empty, even though `SKILL.md`
  and `mcp_server.py` treat it as the agent instruction source.
- `references/*.md`, `assets/*.md`, and
  `examples/conversation_examples.md` are currently 0-byte placeholders.
- `.github/workflows/test-skill.yml` assumes the project path is
  `skills/jvm-memory-leak-debugger`, while this checkout root is
  `/Users/ayarram/Developer/jvm-memory-leak-debugger`.
- `scripts/run_mat.sh` and `tools/mat_runner.py` use different MAT versions and
  installation conventions. Treat that as a documented caveat unless the task
  is specifically to reconcile MAT setup.

## Existing Interfaces

- CLI: `python3 tools/debug_memory_leak.py --hprof ... --gc-log ...`
- Script wrappers: `scripts/`
- MCP tools: `mcp_server.py`
- HTTP endpoints: `server.py`
- JSON contracts: `schemas/`
