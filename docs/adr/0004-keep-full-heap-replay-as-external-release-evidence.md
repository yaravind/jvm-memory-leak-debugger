# 0004: Keep Full Heap Replay As External Release Evidence

## Status

Accepted

## Context

The project goal is a portable JVM memory leak debugging skill that works from
CLI, Codex, Claude, GitHub Copilot-style hosts, MCP, HTTP, and direct function
dispatch on Linux, macOS, and Windows.

End-to-end MAT analysis with a real `.hprof` heap dump is valuable evidence, but
heap dumps are often very large, sensitive, application-specific, and unsuitable
for committed fixtures or ordinary public CI. The checked-in real GC fixture
already proves GC parsing, correlation behavior, report generation, schema
validation, and recommendation output without exposing heap contents. The
manual MAT runtime workflow separately proves that supported hosts can download,
verify, unpack, and locate the pinned Eclipse MAT launcher without requiring a
heap dump.

## Decision

Do not require a committed or default-CI `.hprof` artifact for release
readiness. Keep full heap replay as external release evidence that runs only
when a maintained heap artifact is available through trusted storage.

The default release gate remains:

- dependency-free lint fallback
- unit and manifest tests
- durable JSON contract validation
- real GC-log E2E tests
- non-editable package smoke
- optional adapter smoke when extras are installed
- live cross-platform GitHub Actions evidence
- live MAT runtime download/unpack evidence

`make test-e2e-full` and the `e2e-full` GitHub Actions job remain available for
maintainers who can provide `HPROF_PATH` or configure `HPROF_AVAILABLE=true`
with a trusted external heap artifact. A release may include that evidence, but
the absence of a public heap artifact does not block the default maturity gate.

## Consequences

The repo can stay portable and publicly usable without storing or downloading
sensitive multi-GB heap dumps. Release evidence must be explicit about what was
proved by real GC fixtures, what was proved by MAT runtime smoke, and whether
any external full heap replay was run for a particular release.

Maintainers who need stronger incident replay assurance can still run
`HPROF_PATH=/path/to/java_pidNNN.hprof make test-e2e-full` or configure the
conditional CI job against private artifact storage.
