# Release Readiness Checklist

This checklist keeps release sign-off evidence tied to the project goal: a
portable JVM memory leak debugging skill that works from shell, Codex, Claude,
GitHub Copilot-style hosts, MCP, and non-MCP adapters on Linux, macOS, and
Windows.

Use `docs/architecture/RELEASE_EVIDENCE.md` for the latest evidence snapshot
and remaining external proof requirements. Use
`docs/architecture/MATURITY_COMPLETION_AUDIT.md` for the requirement-by-
requirement completion audit.

## Required Evidence

| Area | Required proof | Current evidence | Status |
| --- | --- | --- | --- |
| Core CLI | Stdlib-only lint fallback, core tests, manifest validation, and real GC fixture tests pass from a source checkout. | `make lint`, `make test`, `make validate-manifests`, `make validate-contracts`, and `make test-e2e-gc`. | Ready locally |
| Durable report contract | Generated `report.json` validates against `schemas/memory_leak_report.json`; skipped or failed heap analysis is explicit in JSON and Markdown. | `make validate-contracts` plus CLI smoke with `--skip-mat` and `--dump-time`. | Ready locally |
| Python packaging | Non-editable install exposes console commands and bundled skill resources outside the repository. | `make package-smoke`, `package-smoke` CI job, and local non-editable install smoke. | Ready locally |
| Harness portability | MCP, HTTP, direct-dispatch, and installed-command examples point at the public tool surface. | `tests/test_manifest.py`, `harnesses/*.example.json`, and `references/harness_configuration.md`. | Ready locally |
| Optional adapters | HTTP and MCP wrappers install through optional extras and route through shared dispatch. | Local Python 3.12 optional venv: `PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters` passed 8 tests, including 6 HTTP adapter tests and 2 MCP wrapper tests. CI `adapter-smoke` still provides hosted Python 3.11 confirmation. | Ready locally; still capture CI adapter-smoke via the main workflow |
| Cross-platform core | Linux, macOS, and Windows run manifest, parser, dispatch, install, CLI, and runtime-diagnostic smoke checks. | `.github/workflows/test-skill.yml` matrix. | Requires live GitHub Actions run |
| MAT runtime | Linux, macOS, and Windows download, SHA-256 verify, unpack, and locate the pinned Eclipse MAT launcher without a heap dump. | `.github/workflows/mat-runtime-smoke.yml` manual workflow and `make test-mat-runtime`. | Requires live GitHub Actions run |
| Real heap analysis | At least one maintained `.hprof` artifact proves MAT suspect extraction and report generation end to end when trusted heap evidence is available. | `make test-e2e-full` when `HPROF_PATH` is available. ADR 0004 keeps this as external release evidence, not a required default release gate. | External optional evidence |

## Release Gate Commands

Run these from the repository root before creating a release PR:

```bash
make release-check
```

`make release-check` runs `make lint`, `make test`, `make validate-manifests`,
`make validate-contracts`, `make test-e2e-gc`, and `make package-smoke`. The
lint target uses `pyflakes` when available and falls back to stdlib
`py_compile` when it is not.

When optional adapter dependencies are available:

```bash
make test-adapters
```

When Java 17 and network access are available on a release host:

```bash
make check-runtime
make test-mat-runtime
```

For a full incident replay with a real heap dump:

```bash
HPROF_PATH=/path/to/java_pidNNN.hprof make test-e2e-full
```

Per `docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md`,
full heap replay is not required for the default release gate unless a
maintained trusted heap artifact is available.

## GitHub Release Evidence

Before marking the maturity goal complete, record the successful run URLs for:

- `Test JVM Memory Leak Debugger Skill`
- `MAT Runtime Smoke`

The MAT workflow is intentionally manual because it downloads external Eclipse
MAT archives. It does not require or upload heap dumps.

After the maturity branch is committed and pushed, capture the required
evidence with GitHub CLI:

```bash
gh run list --repo yaravind/jvm-memory-leak-debugger \
  --workflow "Test JVM Memory Leak Debugger Skill" \
  --branch codex/maturity-roadmap \
  --limit 1 \
  --json databaseId,status,conclusion,url

gh workflow run "MAT Runtime Smoke" \
  --repo yaravind/jvm-memory-leak-debugger \
  --ref codex/maturity-roadmap

gh run list --repo yaravind/jvm-memory-leak-debugger \
  --workflow "MAT Runtime Smoke" \
  --branch codex/maturity-roadmap \
  --limit 1 \
  --json databaseId,status,conclusion,url
```

For each run, wait for completion with `gh run watch <run-id>` and inspect
failures with `gh run view <run-id> --log-failed`. Capture the final URL with:

```bash
gh run view <run-id> --repo yaravind/jvm-memory-leak-debugger --json url
```

Record the successful `url` values in
`docs/architecture/RELEASE_EVIDENCE.md`.

## Handoff Notes

- Do not claim Windows MAT readiness from source-only tests; use the manual MAT
  runtime workflow or a Windows host running `make test-mat-runtime`.
- Keep `report.json` as the source of truth for harnesses. Markdown output is a
  rendering for humans.
- Treat missing heap evidence as a reportable analysis gap, not a successful
  empty-suspects result.
- Update this checklist whenever a release gate changes.
