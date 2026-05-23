# Issue Resolution Matrix

Last updated: 2026-05-23 18:42 EDT

This matrix maps the initial GitHub review issues to the current
`codex/maturity-roadmap` worktree. It is a handoff aid: GitHub issues may remain
open until changes are committed, pushed, reviewed, and closed, but each row
records the local implementation evidence now present in the repo.

## P1 Critical

| Issue | Local resolution evidence | Remaining proof |
| --- | --- | --- |
| #1 `mat_runner.py` is macOS-only; add Linux support and remove hardcoded machine paths | `tools/mat_runner.py` supports pinned MAT ZIP selection for Linux x86_64/AArch64, macOS x86_64/AArch64, and Windows x86_64; Java 17 discovery; `curl` readiness diagnostics; managed `mat_home`; `make test-mat-runtime`; `.github/workflows/mat-runtime-smoke.yml`; ADR 0001; ADR 0004. Hosted MAT runtime smoke passed: https://github.com/yaravind/jvm-memory-leak-debugger/actions/runs/26345458850. | None beyond normal review. |
| #2 Add requirements/dependency manifest | `requirements.txt`, `requirements-server.txt`, `requirements-mcp.txt`, `pyproject.toml`, `setup.py`, console scripts, optional extras, package smoke, release evidence, and completion audit are present and packaged. Hosted package/core workflow passed: https://github.com/yaravind/jvm-memory-leak-debugger/actions/runs/26345458844. | None beyond normal review. |
| #3 Hardcoded project-specific recommendation patterns | Built-ins are generic; custom patterns are schema-backed through `--patterns-file` and `PATTERNS_FILE`; `schemas/recommendation_patterns.json`, `examples/custom_patterns.json`, `references/fix_patterns.md`, and ADR 0003 document the extension contract. | None beyond normal review and CI. |

## P2 High

| Issue | Local resolution evidence | Remaining proof |
| --- | --- | --- |
| #4 `raw_text_by_page` bloats MAT responses | MAT parsing omits raw page text; report schema rejects `heap_dump_analysis.raw_text_by_page`; tests cover parser output and schema rejection. | None beyond normal review and CI. |
| #5 HPROF mtime is unreliable dump timestamp | Correlation prefers HPROF header timestamp, supports explicit `dump_time`, records timestamp provenance, and warns on mtime fallback. Report schema requires provenance. | None beyond normal review and CI. |
| #6 MAT temp workspace cleanup | `run_mat` cleans temporary workspaces on process-start failure and timeout; timeout path terminates/kills the process and captures MAT log context. | None beyond normal review and CI. |
| #7 `skill.json` references missing callable | `gc_parser.parse_and_summarize` exists; manifest tests import every declared module/function pair; shared dispatch registry matches `skill.json`. | None beyond normal review and CI. |

## P3 Medium

| Issue | Local resolution evidence | Remaining proof |
| --- | --- | --- |
| #8 Tool wiring duplicated across deployment surfaces | `tools/dispatch.py` provides the shared registry; HTTP and MCP adapters route through shared dispatch; harness examples cover Codex, Claude, Copilot, direct dispatch, HTTP, and installed commands. Hosted Python 3.11 optional adapter smoke passed in https://github.com/yaravind/jvm-memory-leak-debugger/actions/runs/26345458844. | None beyond normal review. |
| #9 Wrapper scripts add noise | Stale wrappers were removed; `tools/debug_memory_leak.py` is the standalone CLI; manifest tests guard public docs against references to deleted wrappers. | None beyond normal review and CI. |
| #10 `_severity_badge` / report output contract | Severity is part of public report output; schema validation enforces generated `report.json`; heap evidence gaps are explicit in JSON and Markdown. | None beyond normal review and CI. |

## P4 Low

| Issue | Local resolution evidence | Remaining proof |
| --- | --- | --- |
| #11 Overlapping GC pause regex patterns | Pause summary parsing is consolidated; manifest regression guard asserts `_RE_PAUSE_FULL_SUMMARY` remains absent. | None beyond normal review and CI. |
| #12 Brittle MAT HTML parser | Parser prefers structurally marked `problem-suspect` regions and ignores navigation/outside text; tests cover noisy page content and parse failures. | None beyond normal review and CI. |
| #13 Redundant root-level `conftest.py` | Root and test `conftest.py` shims are removed; `pytest.ini` owns `pythonpath = tools`; manifest tests guard this cleanup. | None beyond normal review and CI. |
| #14 Hardcoded Makefile paths | `HPROF_PATH`, `GC_LOG_PATH`, and `OUTPUT_DIR` are parameterized; regression tests guard against the old hardcoded `../../target` path. | None beyond normal review and CI. |

## Completion Notes

Do not close issues from this matrix alone if project policy requires PR review,
but the maturity release evidence now includes successful external workflow URLs
for:

- `Test JVM Memory Leak Debugger Skill`
- `MAT Runtime Smoke`

Use `docs/architecture/MATURITY_COMPLETION_AUDIT.md` and
`docs/architecture/RELEASE_EVIDENCE.md` for the current proof boundary.
