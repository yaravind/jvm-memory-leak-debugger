# Maturity Completion Audit

Last updated: 2026-05-23 18:06 EDT

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
| Stay portable across Linux, macOS, and Windows. | MAT distribution selection supports Linux x86_64/AArch64, macOS x86_64/AArch64, and Windows x86_64. `.github/workflows/test-skill.yml` defines a Linux/macOS/Windows matrix. `.github/workflows/mat-runtime-smoke.yml` defines a manual Linux/macOS/Windows MAT download/unpack smoke. | Requires live GitHub Actions run URLs |
| Work as a standalone CLI. | `pyproject.toml` and `setup.py` expose `jvm-memory-leak-debugger`; package smoke verifies installed CLI `--help` from a non-editable install outside the source checkout. | Ready locally |
| Work with MCP hosts such as Claude. | Optional `.[mcp]` extra and `jvm-memory-leak-debugger-mcp` command are present. Local Python 3.12 optional-dependency smoke passed 2 MCP wrapper tests. `harnesses/claude_desktop_config.example.json` documents Claude configuration. | Ready locally; hosted Python 3.11 adapter-smoke URL still required for release sign-off |
| Work without MCP. | Direct dispatch, HTTP bridge, installed-command harnesses, standalone CLI, Codex direct-dispatch, and Copilot HTTP examples all point at the public tool surface. | Ready locally |
| Configure with Codex, Claude, GitHub Copilot, and other harnesses. | `harnesses/codex_skill.example.json`, `harnesses/claude_desktop_config.example.json`, `harnesses/copilot_extension.example.json`, `harnesses/direct_function_dispatch.example.json`, `harnesses/http_bridge.example.json`, and `harnesses/installed_commands.example.json` are documented, JSON-validated, and included in package smoke. | Ready locally |
| Keep recommendations broadly useful across JVM applications. | Built-in recommendation patterns are generic; custom schema-backed pattern files are supported through `--patterns-file` or `PATTERNS_FILE`. ADR 0003 records the extension contract. | Ready locally |
| Avoid fabricated data when artifacts or MAT evidence are missing. | Heap analysis status and errors are part of the durable report contract; skipped or failed MAT analysis is surfaced in JSON and Markdown. Tests cover missing heap evidence behavior. | Ready locally |
| Keep release readiness evidence-based. | `docs/architecture/RELEASE_EVIDENCE.md`, `docs/architecture/RELEASE_READINESS_CHECKLIST.md`, and this audit record local proof, external gaps, and non-claims. | Ready locally |
| Avoid default public CI dependence on sensitive heap dumps. | ADR 0004 keeps full heap replay as external release evidence via `make test-e2e-full` or conditional CI when trusted heap artifacts exist. | Ready locally |

## Current Blocking Evidence

The maturity goal must remain open until these externally verifiable items are
captured from the committed branch:

1. Successful `Test JVM Memory Leak Debugger Skill` GitHub Actions run URL for
   `codex/maturity-roadmap`, including the cross-platform smoke matrix and the
   Python 3.11 `adapter-smoke` job.
2. Successful `MAT Runtime Smoke` GitHub Actions run URL for
   `codex/maturity-roadmap`, or equivalent Linux/macOS/Windows host logs with
   Java 17 and network access.

As of the latest local check, `gh run list` returned no
`Test JVM Memory Leak Debugger Skill` runs for `codex/maturity-roadmap`, and the
remote repo could not find `MAT Runtime Smoke` because the workflow file is not
committed and pushed yet.

## Completion Rule

Do not mark the maturity goal complete until the release evidence snapshot
contains successful run URLs for both external workflows above. Local
`make release-check` is necessary but not sufficient for the full objective
because Windows/macOS/Linux hosted proof and live MAT download/unpack proof are
explicit goal requirements.
