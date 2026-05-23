# JVM Memory Leak Debugger Maturity PRD

## Goal

Make `jvm-memory-leak-debugger` a portable JVM memory-leak diagnosis skill and
CLI that can be used from Codex, Claude, GitHub Copilot, MCP hosts, HTTP
adapters, and plain shell workflows on macOS, Linux, and Windows.

The durable output contract remains `report.json`; `report.md` is the
human-readable rendering of the same facts.

## Current Issue Backlog

Existing GitHub issues reviewed on 2026-05-23:

| Priority | Issues | Theme |
| --- | --- | --- |
| P1-critical | #1, #2, #3 | MAT portability, dependency declaration, generic/pluggable recommendations |
| P2-high | #4, #5, #6, #7 | Response size, dump-time correctness, MAT temp cleanup, manifest dispatch correctness |
| P3-medium | #8, #9, #10 | Adapter duplication and cleanup |
| P4-low | #11, #12, #13, #14 | Parser maintainability, parser robustness, cleanup, local path parameterization |

No new issues should be created until existing P1/P2 issues are updated with
implementation status and any discovered scope changes.

Use `docs/architecture/ISSUE_RESOLUTION_MATRIX.md` for the current
issue-by-issue local resolution evidence and remaining external proof.

## Release Principles

- The core toolchain must remain Python-stdlib-only where practical.
- Optional hosting adapters declare their own dependencies and stay thin.
- MAT integration must use Eclipse MAT rather than parsing `.hprof` binaries.
- Missing artifacts must be explicit errors or warnings, never fabricated data.
- Missing or failed heap analysis must be explicit in `report.json` and
  `report.md`; an empty suspects list alone is not enough evidence.
- Harness manifests must call stable public functions that return
  JSON-serialisable dictionaries.
- `report.json` changes require schema and test updates.
- Contract validation must remain dependency-free for core outputs so harnesses
  can verify reports without installing adapter packages.
- Release readiness must be evidence-based. Use
  `docs/architecture/RELEASE_READINESS_CHECKLIST.md` to record which local,
  package, adapter, cross-platform, and MAT runtime checks have been proven.

## Milestones

### M1: Harness Contract And Dependency Baseline

Resolve the filed issues that prevent basic runtime adoption.

Acceptance criteria:

- `skill.json` dispatches every declared tool to an existing public callable.
- Dependency manifests document server and MCP adapter packages.
- MAT tool responses do not include raw HTML page text by default.
- The durable report schema rejects raw MAT page text fields such as
  `raw_text_by_page`.
- MAT temporary workspaces are cleaned up on success, failure, and timeout.
- `make test` and `make validate-manifests` pass.

Tracked by: #2, #4, #6, #7.

### M2: Cross-Platform MAT Runtime

Make heap suspect extraction usable on Linux and macOS first, with Windows
behavior documented and either supported directly or clearly gated.

Status: partially implemented on `codex/maturity-roadmap` for pinned MAT ZIP
selection, SHA-256 verification, Java discovery, first-run `curl` readiness,
install-layout detection, an artifact-free `--check-runtime` diagnostic, and
configurable `mat_home` for managed MAT installations. A manual `MAT Runtime
Smoke` workflow and local `make test-mat-runtime` target can gather live
download/unpack evidence without needing a heap dump. Still needs those live
Linux/Windows workflow results before release.

Acceptance criteria:

- MAT install/discovery has no user-machine hardcoded paths.
- macOS, Linux, and Windows use pinned `.zip` distributions without
  macOS-only extraction tools.
- Java 17 discovery checks explicit env vars first, then platform-native
  discovery, then `PATH`.
- MAT URLs and checksums are pinned per platform/architecture.
- Tests cover platform selection without downloading MAT.
- CLI users can check local Java/MAT/platform readiness without needing a heap
  dump, GC log, or network download.
- Runtime diagnostics report whether `curl` is available for first-run MAT
  downloads and avoid claiming first-run readiness when neither curl nor an
  existing MAT install is available.
- Maintainers can run a no-heap MAT runtime smoke that downloads, verifies,
  unpacks, and validates the pinned MAT archive on Linux, macOS, and Windows.
- `extract_heap_suspects` and `generate_report` accept `mat_home` for harnesses
  that provide a managed MAT installation.

Tracked by: #1, #14.

### M3: Portable Recommendation Engine

Separate generic leak/GC diagnosis from user-project-specific fixes.

Status: implemented on `codex/maturity-roadmap` for generic built-ins,
`--patterns-file`, `PATTERNS_FILE`, schema/docs/examples, and
`pattern_source` reporting. Custom pattern files now fail early for invalid
regexes, duplicate ids, matcherless rules, unknown GC conditions, and invalid
GC threshold values.

Acceptance criteria:

- Built-in patterns are generic JVM/G1/MAT recommendations.
- User patterns can be loaded from a JSON file through CLI args and adapter
  parameters.
- Project-specific code pointers are absent from built-in recommendations.
- Pattern schema and examples are documented.
- `report.json` records which pattern source produced each recommendation.
- Invalid custom patterns fail before report generation emits an incomplete or
  misleading recommendation set.

Tracked by: #3.

### M4: Timestamp And Correlation Correctness

Improve dump-to-GC correlation for transferred production artifacts.

Status: implemented on `codex/maturity-roadmap` for explicit dump-time
overrides, HPROF header timestamp parsing, mtime fallback warnings, schema
updates, and tests. The durable report contract now requires dump timestamp
provenance fields so harnesses can distinguish HPROF header, explicit override,
and file-mtime fallback behavior.

Acceptance criteria:

- HPROF header timestamp is preferred when available.
- File mtime is an explicit fallback with a warning in `report.json`.
- CLI and adapters accept an explicit dump-time override.
- Tests cover embedded timestamp, override, and mtime fallback.
- `schemas/memory_leak_report.json` requires dump timestamp source and warning
  fields in `correlation`.

Tracked by: #5.

### M5: Shared Tool Registry

Make Codex, Claude/MCP, HTTP, and CLI surfaces consistent.

Status: implemented on `codex/maturity-roadmap` with `tools/dispatch.py` as
the shared callable registry and `tools/pipeline.py` as the reusable full-report
pipeline. FastAPI routes are registered from the registry, MCP tool wrappers
delegate to the registry, and the CLI invokes the `generate_report` registry
entry.

Acceptance criteria:

- A shared tool registry owns callable names, parameter defaults, and error
  shaping.
- MCP and HTTP adapters register from the same registry.
- CLI uses the same implementation path for tool behavior.
- Adapter-specific dependencies remain optional.

Tracked by: #8, #9, #10.

### M6: Contributor Cleanup

Remove local-machine assumptions and small public API inconsistencies that make
the repo feel harder to adopt.

Status: implemented locally on `codex/maturity-roadmap`. Severity is public and
part of the report contract (#10), pytest path setup is centralized in
`pytest.ini` (#13), example artifact paths are parameterized (#14), duplicate
Python/script MAT entry points were removed while keeping the distinct artifact
validation helper (#9), and overlapping GC pause regex handling was
consolidated (#11). Manifest regression guards keep those cleanup decisions in
place.

### M7: Skill Package Completeness

Make the repository usable as an actual agent skill package, not only a Python
tooling repo.

Status: implemented locally on `codex/maturity-roadmap` for non-empty
`instructions/system_prompt.md`, targeted references, conversation examples,
skill card, report-shape asset, stale script-reference cleanup, repo-root CI
paths, concrete harness examples, installed-command guidance, HTTP `/tools`
catalog discovery, and manifest/registry contract tests. `make
validate-manifests` now checks the skill-facing package files are non-empty,
harness examples are parseable JSON, and deleted script entry points are not
referenced from public skill docs.

Acceptance criteria:

- `SKILL.md` is concise and points to only existing scripts, references, and
  assets.
- `instructions/system_prompt.md` gives hosted agents enough operating guidance
  to use the public tool surface safely.
- Reference files cover artifact capture, G1 interpretation, recommendation
  patterns, and MAT setup without forcing all details into `SKILL.md`.
- Examples demonstrate full analysis, GC-only triage, and transferred dump
  timestamp handling.
- CI runs from the repository root and validates the same manifest/package gates
  used locally.
- `skill.json`, MCP wrappers, HTTP routes, CLI options, and direct dispatch stay
  aligned for shared parameters such as MAT heap and timeout settings.
- Manifest tests guard shared runtime parameters including `mat_home`,
  `timeout_s`, `patterns_file`, and `dump_time` across public tool definitions,
  CLI affordances, and MCP wrapper signatures.
- Harness examples cover MCP, direct local dispatch without MCP, and HTTP bridge
  hosting for remote or non-Python agents.
- Harness examples cover installed console-command configuration, and a
  preflight checklist gives operators repeatable install/runtime checks before
  wiring the skill into a new host.
- HTTP bridge exposes both the full skill manifest and a compact `/tools`
  catalog so non-MCP hosts can discover callable routes without importing
  Python modules.

### M8: Python Packaging And Installability

Make the core CLI installable as a normal Python tool while preserving optional
adapter dependencies.

Status: implemented locally on `codex/maturity-roadmap` with
`pyproject.toml`, the `jvm-memory-leak-debugger`,
`jvm-memory-leak-debugger-api`, and `jvm-memory-leak-debugger-mcp` console
scripts, optional `mcp`, `server`, and `all` extras, README install guidance,
installed skill bundle data under `share/jvm-memory-leak-debugger`, ADR 0002,
and package smoke evidence from a non-editable install outside the source
checkout.

Acceptance criteria:

- `pip install -e .` exposes a `jvm-memory-leak-debugger` command for local CLI
  usage.
- `pip install . --no-deps` installs the console command and skill bundle data
  for non-editable package consumers.
- Core package dependencies remain empty so CLI users do not need MCP/FastAPI.
- Optional extras cover MCP and HTTP bridge hosting.
- Manifest/package tests guard the console script and optional dependency names.
- Adapter extras expose installed launch commands so hosts do not need to point
  at source-checkout `server.py` or `mcp_server.py` paths.
- Installed adapters can locate `skill.json`, instructions, schemas, examples,
  references, harness examples, and ADRs outside a source checkout.
- Installed package data includes host preflight guidance and installed-command
  harness examples.

### M9: Cross-Platform CI Evidence

Prove the portable core works on the operating systems named in the goal before
claiming release readiness.

Status: partially implemented on `codex/maturity-roadmap` with a GitHub Actions
cross-platform smoke matrix for Linux, macOS, and Windows on Python 3.9 and
3.12. The smoke matrix validates the manifest/dispatch contract, GC parser,
editable install, installed console command, runtime diagnostics, and
importability of the packaged core modules without requiring MAT download or a
real heap dump.

Acceptance criteria:

- CI includes at least one Linux, macOS, and Windows job.
- Cross-platform jobs avoid large `.hprof` artifacts and MAT downloads.
- Cross-platform jobs verify the installed CLI entry point, not only source-tree
  execution.
- Cross-platform jobs verify the MAT runtime diagnostic can identify the
  platform-specific pinned MAT archive without downloading it.
- Manual release workflow can verify the pinned MAT archive downloads,
  SHA-256-checks, unpacks, and exposes an Equinox launcher on Linux, macOS, and
  Windows without requiring a heap dump.
- Linux jobs still run the broader fast test suite and real GC-log E2E tests.
- CI verifies a non-editable package install can find bundled skill files from a
  working directory outside the repository.
- Release sign-off records live GitHub Actions run URLs for the cross-platform
  package/core matrix and the manual MAT runtime smoke workflow.
- Full heap replay remains available as external release evidence, but is not a
  default release gate unless a maintained trusted heap artifact is available.

### M10: Optional Adapter Runtime Evidence

Verify the optional HTTP and MCP hosting layers are operational when their
extras are installed, while keeping the core CLI dependency-free.

Status: implemented locally on `codex/maturity-roadmap` with optional FastAPI
and MCP smoke tests plus a GitHub Actions `adapter-smoke` job that installs
`.[server,mcp]`, verifies installed adapter command `--help` output, and runs
`make test-adapters`. Latest local adapter smoke was run from the current
worktree with an optional-dependency Python 3.12 venv:
`PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters`
passed all 8 adapter tests, including 6 HTTP adapter tests and 2 MCP wrapper
tests. Hosted MCP runtime proof still needs the Python 3.11 `adapter-smoke`
job URL from the main GitHub Actions workflow before release sign-off.

Acceptance criteria:

- Core tests still pass without FastAPI or MCP installed.
- Adapter tests are skipped or isolated from core-only environments.
- HTTP smoke covers `/health`, `/skill.json`, one successful tool route, and a
  dispatch validation error.
- HTTP smoke covers `/tools` as a compact route catalog for remote function
  hosts.
- MCP smoke covers wrapper dispatch for GC parsing and dump-time correlation.
- CI installs optional adapter extras and runs the adapter smoke suite.
- Installed adapter command help is verified before starting any long-running
  server process.

### M11: Output Contract Validation

Keep the durable JSON contracts enforceable without pulling in optional
dependencies.

Status: implemented locally on `codex/maturity-roadmap` with a small
dependency-free schema validator for the subset used by this repo's schemas,
tests that validate real GC parser output plus generated `report.json`, and
pipeline enforcement that validates the full report contract before writing
`report.json`. Heap analysis status and errors are part of the durable report
contract so skipped or failed MAT analysis is visible to humans and harnesses.

Acceptance criteria:

- `analyze_gc_log` output from the real GC fixture validates against
  `schemas/gc_analysis_result.json`.
- Generated `report.json` validates against `schemas/memory_leak_report.json`,
  including local `$ref` resolution.
- `generate_report` fails before emitting `report.json` when the generated
  payload violates the report contract.
- `report.json` and `report.md` explicitly surface skipped or failed MAT heap
  analysis instead of silently returning an empty suspects list.
- Contract validation requires only Python stdlib and pytest for tests.
- `make validate-contracts` runs the focused contract suite.

## Open Decisions

- None currently recorded.

## Resolved Decisions

- Windows MAT strategy is resolved by
  `docs/adr/0001-use-pinned-cross-platform-mat-zip-distributions.md`: use the
  native Windows x86_64 Eclipse MAT ZIP distribution as the primary supported
  Windows path. WSL with the Linux package remains fallback guidance for
  Windows ARM64 or hosts that provide a managed MAT installation, but release
  readiness must still be proven through the manual MAT runtime smoke workflow
  or an equivalent Windows host run.
- Custom recommendation pattern language is resolved by
  `docs/adr/0003-use-schema-backed-custom-recommendation-patterns.md`: keep
  built-in recommendations generic and support schema-backed JSON extension
  files with regex evidence matchers plus structured GC threshold matchers.
- Full heap replay release policy is resolved by
  `docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md`: keep
  `make test-e2e-full` and conditional CI support for trusted external heap
  artifacts, but do not require a committed or default-CI `.hprof` artifact for
  release readiness.
