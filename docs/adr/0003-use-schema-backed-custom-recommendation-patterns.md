# 0003: Use Schema-Backed Custom Recommendation Patterns

## Status

Accepted

## Context

The debugger must be useful across many JVM applications, not only the incident
or codebase that produced the original examples. Hardcoded project-specific
recommendations make the skill noisy for unrelated users and force operators to
edit Python code when they need organization-specific remediation guidance.

The recommendation contract also needs to remain portable across Codex, Claude,
GitHub Copilot-style hosts, direct CLI usage, HTTP adapters, and MCP wrappers.
Those hosts can all pass file paths and read JSON artifacts, but they should not
need to import Python modules or understand private reporter internals.

## Decision

Keep built-in recommendation patterns generic, and load project-specific rules
from a JSON pattern file supplied through `--patterns-file` or `PATTERNS_FILE`.
The file format is defined by `schemas/recommendation_patterns.json` and allows
either a top-level pattern array or an object with a `patterns` array.

Custom patterns may match MAT evidence with case-insensitive regex fields:
`match_class`, `match_stack`, and `match_text`. They may also match GC pressure
through the structured `gc` threshold object, currently including
`min_to_space_exhausted`, `min_full_gc_count`, and
`min_concurrent_abort_count`.

Every custom pattern must provide stable output fields (`id`, `title`,
`description`, and `fixes`) and at least one matcher. Pattern ids are unique
across built-in and custom sources. Invalid regexes, unknown GC conditions,
negative thresholds, duplicate ids, and unknown fields fail before report
generation starts.

## Consequences

Generic users get project-neutral recommendations by default.

Teams can add precise code pointers and remediation playbooks without forking
the skill or changing the Python package.

The JSON schema becomes part of the durable extension contract and must be kept
in package data, examples, docs, and tests whenever the language changes.

The language intentionally stays small: it supports regex evidence matching and
numeric GC thresholds, but not arbitrary expressions or executable hooks. More
powerful matching would require another ADR because it would affect safety,
portability, and host compatibility.
