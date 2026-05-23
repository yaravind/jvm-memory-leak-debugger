# Release Evidence Snapshot

Last updated: 2026-05-23 18:42 EDT

This snapshot records what has been proven from the current
`codex/maturity-roadmap` worktree and from hosted GitHub Actions release
evidence.

For a requirement-by-requirement audit of the original goal, see
`docs/architecture/MATURITY_COMPLETION_AUDIT.md`.
For the GitHub issue-by-issue implementation evidence, see
`docs/architecture/ISSUE_RESOLUTION_MATRIX.md`.

## Proven Locally

| Area | Evidence |
| --- | --- |
| Local release gate | `make release-check` passed from the current worktree after adding the packaged issue-resolution matrix. It runs `make lint`, `make test`, `make validate-manifests`, `make validate-contracts`, `make test-e2e-gc`, and `make package-smoke`. |
| Contributor lint | `make lint` passed through `make release-check`. `pyflakes` was not installed, so the helper used the dependency-free `py_compile` fallback; in other words, the py_compile fallback covered 13 Python files. |
| Core tests | `make test` passed through `make release-check`: 97 selected tests, 2 optional adapter skips, and 3 full E2E tests deselected. |
| Manifest/package contracts | `make validate-manifests` passed through `make release-check`. |
| Durable JSON contracts | `make validate-contracts` passed through `make release-check`; report validation includes generated report output, dump timestamp provenance, and raw MAT page text rejection. |
| Real GC fixture | `make test-e2e-gc` passed through `make release-check`: 15 selected real-GC tests and 3 full E2E tests deselected. |
| Non-editable package smoke | `make package-smoke` passed through `make release-check`. The smoke venv reported Python 3.9.6 and setuptools 58.0.4; the isolated PEP 517 install hit a network restriction fetching build dependencies, then the smoke script printed the explicit `--no-build-isolation` fallback message and verified installed CLI/API/MCP help commands plus bundled skill data, including Codex and Copilot harness examples. |
| Installed commands | Package smoke verified `jvm-memory-leak-debugger --help`, `jvm-memory-leak-debugger-api --help`, and `jvm-memory-leak-debugger-mcp --help` from a temporary non-editable install. |
| Installed skill bundle | Package smoke resolved bundled skill data from a temporary venv, including `skill.json`, instructions, report and recommendation schemas, `examples/custom_patterns.json`, `references/fix_patterns.md`, Codex/Copilot/Claude/direct/HTTP/installed-command harness examples, architecture docs, `docs/architecture/MATURITY_COMPLETION_AUDIT.md`, `docs/architecture/ISSUE_RESOLUTION_MATRIX.md`, ADR 0003 for the custom recommendation pattern contract, and ADR 0004 for full heap replay evidence policy. |
| Optional HTTP/MCP adapters | `PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters` passed 8 tests in a Python 3.12 optional-dependency venv: 6 HTTP adapter tests and 2 MCP wrapper tests. |
| Full heap replay policy | `docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md` records that full `.hprof` replay remains supported through `make test-e2e-full`, but is external release evidence rather than a required default release gate unless a maintained trusted heap artifact is available. |

## Proven On GitHub Actions

| Area | Evidence |
| --- | --- |
| Cross-platform core, package, lint, adapters, and real GC fixture | `Test JVM Memory Leak Debugger Skill` passed for commit `1954e9b` on `codex/maturity-roadmap`: https://github.com/yaravind/jvm-memory-leak-debugger/actions/runs/26345458844. The run included pyflakes lint, package smoke, Python 3.11 optional adapter smoke, real GC-log E2E jobs, and Linux/macOS/Windows cross-platform smoke for Python 3.9 and 3.12. |
| MAT runtime portability | `MAT Runtime Smoke` passed for commit `1954e9b` on `codex/maturity-roadmap`: https://github.com/yaravind/jvm-memory-leak-debugger/actions/runs/26345458850. The run downloaded, SHA-256 verified, unpacked, and validated the pinned Eclipse MAT distribution on Ubuntu, macOS, and Windows with Java 17 and no heap dump. |

## External State Checked

On 2026-05-23 18:42 EDT, `gh run watch` confirmed successful completion for
both required hosted workflows on branch `codex/maturity-roadmap`.

## Residual Release Notes

- The default release gate still does not run `make test-e2e-full` with a real
  `.hprof`; ADR 0004 keeps that as external replay evidence unless a maintained
  trusted heap artifact is available.
- GitHub Actions emitted Node.js 20 deprecation annotations for upstream
  `actions/*` dependencies. They did not fail either workflow.

## Evidence Capture Commands

Use the runbook in `docs/architecture/RELEASE_READINESS_CHECKLIST.md` to refresh
or re-check GitHub Actions runs:
`gh run list`, `gh workflow run "MAT Runtime Smoke"`, `gh run watch`, and
`gh run view --log-failed`. Capture final evidence URLs with
`gh run view <run-id> --json url`.
