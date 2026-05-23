# Release Evidence Snapshot

Last updated: 2026-05-23 18:10 EDT

This snapshot records what has been proven from the current
`codex/maturity-roadmap` worktree and what still needs external evidence before
the maturity goal can be called complete.

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

## Partially Proven

| Area | Current evidence | Missing evidence |
| --- | --- | --- |
| Cross-platform core | `.github/workflows/test-skill.yml` defines Linux, macOS, and Windows smoke coverage for Python 3.9 and 3.12, installed CLI checks, package smoke, adapter smoke, and real GC fixture tests. | Live successful `Test JVM Memory Leak Debugger Skill` GitHub Actions run URL from this branch. |
| MAT runtime portability | `.github/workflows/mat-runtime-smoke.yml` and `make test-mat-runtime` verify the pinned MAT archive download/unpack path without a heap dump. The workflow supports push/PR-triggered branch evidence and manual reruns after it exists on the default branch. Local no-download diagnostics work, but this host's Java points at Java 11. | Live successful `MAT Runtime Smoke` GitHub Actions run URL, or equivalent Linux/macOS/Windows host logs with Java 17 and network access. |

## External State Checked

On 2026-05-23 17:58 EDT, `gh run list` found no
`Test JVM Memory Leak Debugger Skill` runs for branch
`codex/maturity-roadmap`. The same check could not find a remote
`MAT Runtime Smoke` workflow yet, which is expected until
`.github/workflows/mat-runtime-smoke.yml` is committed and pushed.

## Do Not Claim Yet

- Do not claim Windows MAT readiness from source-only tests. Use the
  push/PR-triggered MAT runtime workflow, the manual MAT runtime workflow, or a
  Windows host running `make test-mat-runtime`.
- Do not claim hosted MCP runtime readiness until the Python 3.11
  `adapter-smoke` job in `Test JVM Memory Leak Debugger Skill` has a successful
  live run URL, even though local Python 3.12 MCP smoke now passes.
- Do not mark the maturity goal complete until the cross-platform core workflow
  and MAT runtime smoke workflow have live successful run URLs recorded.

## Next Evidence To Capture

1. Push the maturity branch after explicit commit/push authorization.
2. Run `Test JVM Memory Leak Debugger Skill` on GitHub Actions and record the
   successful run URL.
3. Use the push/PR-triggered `MAT Runtime Smoke` GitHub Actions run, or rerun it
   manually after the workflow exists on the default branch, and record the
   successful run URL.
4. Confirm the `adapter-smoke` job in `Test JVM Memory Leak Debugger Skill`
   passed, because it is the hosted Python 3.11 MCP proof.

Use the runbook in `docs/architecture/RELEASE_READINESS_CHECKLIST.md` to list,
start, watch, and inspect the required GitHub Actions runs:
`gh run list`, `gh workflow run "MAT Runtime Smoke"`, `gh run watch`, and
`gh run view --log-failed`. Capture final evidence URLs with
`gh run view <run-id> --json url`.
