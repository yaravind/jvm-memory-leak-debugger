# Maturity Completion Audit

Last updated: 2026-05-23 18:42 EDT

This audit maps the original maturity goal to current evidence from the
`codex/maturity-roadmap` worktree. It is intentionally stricter than a feature
summary: a requirement is complete only when current evidence proves it.

For issue-by-issue evidence from the initial GitHub review backlog, see
`docs/architecture/ISSUE_RESOLUTION_MATRIX.md`.

## Requirement Matrix

| Requirement | Current evidence | Status |
| --- | --- | --- |
| Diagnose JVM memory leaks from `.hprof` heap dumps and G1 GC logs. | `generate_report` orchestrates GC parsing, dump correlation, optional MAT suspect extraction, recommendation matching, and report writing. `make test-e2e-gc`, `make validate-contracts`, and `make release-check` pass from the current worktree. | Ready locally |
| Produce durable machine-readable and human-readable outputs. | `report.json` validates against `schemas/memory_leak_report.json`; `report.md` surfaces the same structured facts. Contract tests cover generated reports, heap analysis status, dump timestamp provenance, and raw MAT page text rejection. | Ready locally |
| Stay portable across Linux, macOS, and Windows. | MAT distribution selection supports Linux x86_64/AArch64, macOS x86_64/AArch64, and Windows x86_64. `Test JVM Memory Leak Debugger Skill` passed on Linux, macOS, and Windows for Python 3.9 and 3.12. `MAT Runtime Smoke` passed on Linux, macOS, and Windows with Java 17 and real pinned MAT download/unpack. | Ready with hosted evidence |
| Work as a standalone CLI. | `pyproject.toml` and `setup.py` expose `jvm-memory-leak-debugger`; package smoke verifies installed CLI `--help` from a non-editable install outside the source checkout. | Ready locally |
| Work with MCP hosts such as Claude. | Optional `.[mcp]` extra and `jvm-memory-leak-debugger-mcp` command are present. Local Python 3.12 optional-dependency smoke passed 2 MCP wrapper tests. The hosted Python 3.11 optional adapter smoke passed in `Test JVM Memory Leak Debugger Skill`. `harnesses/claude_desktop_config.example.json` documents Claude configuration. | Ready with hosted evidence |
| Work without MCP. | Direct dispatch, HTTP bridge, installed-command harnesses, standalone CLI, Codex direct-dispatch, and Copilot HTTP examples all point at the public tool surface. | Ready locally |
| Configure with Codex, Claude, GitHub Copilot, and other harnesses. | `harnesses/codex_skill.example.json`, `harnesses/claude_desktop_config.example.json`, `harnesses/copilot_extension.example.json`, `harnesses/direct_function_dispatch.example.json`, `harnesses/http_bridge.example.json`, and `harnesses/installed_commands.example.json` are documented, JSON-validated, and included in package smoke. | Ready locally |
| Keep recommendations broadly useful across JVM applications. | Built-in recommendation patterns are generic; custom schema-backed pattern files are supported through `--patterns-file` or `PATTERNS_FILE`. ADR 0003 records the extension contract. | Ready locally |
| Avoid fabricated data when artifacts or MAT evidence are missing. | Heap analysis status and errors are part of the durable report contract; skipped or failed MAT analysis is surfaced in JSON and Markdown. Tests cover missing heap evidence behavior. | Ready locally |
| Keep release readiness evidence-based. | `docs/architecture/RELEASE_EVIDENCE.md`, `docs/architecture/RELEASE_READINESS_CHECKLIST.md`, and this audit record local proof, external gaps, and non-claims. | Ready locally |
| Avoid default public CI dependence on sensitive heap dumps. | ADR 0004 keeps full heap replay as external release evidence via `make test-e2e-full` or conditional CI when trusted heap artifacts exist. | Ready locally |

## Hosted Evidence Captured

The required externally verifiable items are captured from the committed branch:

1. `Test JVM Memory Leak Debugger Skill` passed for commit `1954e9b` on
   `codex/maturity-roadmap`, including the cross-platform smoke matrix and the
   Python 3.11 optional adapter smoke job:
   https://github.com/yaravind/jvm-memory-leak-debugger/actions/runs/26345458844
2. `MAT Runtime Smoke` passed for commit `1954e9b` on `codex/maturity-roadmap`,
   proving Linux/macOS/Windows MAT download/unpack with Java 17:
   https://github.com/yaravind/jvm-memory-leak-debugger/actions/runs/26345458850

The audit still treats full `.hprof` replay as external evidence per ADR 0004,
not as a required default release gate.

## Completion Rule

The maturity goal can be marked complete when the release evidence snapshot
contains the successful run URLs above and the branch remains pushed. Local
`make release-check` remains the repeatable pre-push gate; the hosted workflow
URLs provide the Linux/macOS/Windows and live MAT download/unpack proof required
by the original objective.
