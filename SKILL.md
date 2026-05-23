---
name: jvm-memory-leak-debugger
version: 1.0.0
description: >
  Use when diagnosing JVM OutOfMemoryError, heap leaks, G1 Full GC storms, or
  memory-retention incidents from a .hprof heap dump and JVM unified GC log.
  Runs as a portable agent skill, MCP toolset, HTTP bridge, or standalone CLI.
author: data-diff
license: MIT
tags:
  - java
  - jvm
  - memory
  - debugging
  - performance
  - gc
  - heap
  - scala
  - devtools
compatibility:
  - github-copilot
  - openai-codex
  - claude-mcp
  - standalone-cli
runtime: python3
python_min: "3.9"
entry_point: tools/debug_memory_leak.py
manifest: skill.json
---

# JVM Memory Leak Debugger

Diagnoses JVM out-of-memory failures from a `.hprof` heap dump and G1 GC log.
Use this skill whenever a JVM process crashes with `OutOfMemoryError` or
exhibits severe Full GC storms and you need to identify the root cause fast.

---

## When to Use This Skill

- A JVM process exited with `java.lang.OutOfMemoryError: Java heap space`
- G1 GC log shows repeated Full GC events reclaiming near-zero memory
- Test suite or long-running Spark/JDBC job OOMs and you have a `.hprof` dump
- You want structured, machine-readable evidence for a post-mortem report

---

## Workflow

### Step 1 — Locate the artifacts

Ask the user for:
1. The `.hprof` heap dump path (e.g. `target/jvm-logs/java_pid16615.hprof`)
2. The JVM GC log path (e.g. `target/jvm-logs/gc-16615.log`)

If either file is missing, ask for it and direct the user to
`references/jvm_flags.md`.

### Step 2 — Run GC log analysis first

Call `analyze_gc_log` with the GC log path.

Interpret the result:
- **`full_gc_count` ≥ 10** → severe memory pressure, likely a true leak
- **`to_space_exhausted_count` > 0** → G1 ran out of evacuation space; always
  precedes a Full GC cascade
- **`live_set_drift_mb` > 500** → heap growing unboundedly between Young GCs
- **`oom_proximity_pct` ≥ 99** → heap was completely exhausted at dump time

### Step 3 — Correlate dump to GC timeline

Call `correlate_dump_to_gc` to classify when the dump was captured relative to
the GC storm. Possible phases:

| `dump_phase` | Meaning |
|---|---|
| `during_full_gc_storm` | Dump taken mid-storm — high confidence leak |
| `post_oom_recovery` | Dump captured after GC storm ended |
| `normal_operation` | No GC pressure at dump time — may be a false positive |

### Step 4 — Extract heap suspects (Eclipse MAT)

Call `extract_heap_suspects`. MAT may take 10–30 minutes on large dumps.

For local setup checks, run `python3 tools/debug_memory_leak.py
--check-runtime` before asking for a full heap analysis. Use `mat_home` when a
host provides a managed Eclipse MAT installation outside the default temp
directory.

If MAT was already run and a `*_Leak_Suspects.zip` exists beside the `.hprof`,
pass `skip_mat=true` to `generate_report` instead.

Focus on:
- **`retained_pct` ≥ 90** → single object tree owns nearly all heap
- **`stack_frames`** → trace back to the calling code
- **`object_graph_classes`** → identify which collection type is accumulating

### Step 5 — Generate full report

Call `generate_report` for the end-to-end pipeline, or run the standalone CLI:

```bash
python3 tools/debug_memory_leak.py --hprof /path/to/dump.hprof --gc-log /path/to/gc.log
```

This writes:
- `report.json` — machine-readable artifact (source of truth)
- `report.md` — human-readable markdown with timeline, suspects, recommendations

### Step 6 — Summarise findings to the user

Structure your response as:

1. **Severity** badge (CRITICAL / HIGH / MEDIUM / LOW)
2. **Root cause** in one sentence
3. **Top 3 recommendations** with code pointers
4. Link to `report.md` for full details

---

## Output Format

Always emit a structured summary block before prose:

```
## JVM Memory Leak Analysis

**Severity:** 🔴 CRITICAL
**Dump phase:** during_full_gc_storm
**OOM proximity:** 100%

### Root Cause
<one-sentence root cause>

### Top Recommendations
1. <title> — `<code_pointer>`
2. <title>
3. <title>

Full report: <md_report_path>
```

---

## Constraints

- Do **not** attempt to parse `.hprof` binary directly — always use MAT via
  `extract_heap_suspects`.
- Do **not** read raw GC log lines manually — always use `analyze_gc_log`.
- If both artifact files are missing, stop and ask the user to provide them.
  Do not fabricate memory statistics.
- If MAT fails to run, surface the error, complete the GC log analysis, and
  point the user to `references/mat_installation.md` for Java/MAT setup.
- Keep summaries concise. Do not repeat every histogram row — top 5 max.
- Severity labels are derived deterministically from GC metrics — do not
  override them on intuition alone.

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/validate_artifacts.sh` | Checks `.hprof` and GC log are present and non-empty |
| `tools/debug_memory_leak.py` | Standalone CLI and `generate_report` callable |

---

## References

| Reference | Description |
|-----------|-------------|
| `references/jvm_flags.md` | JVM flags required to produce `.hprof` and GC logs |
| `references/g1gc_phases.md` | G1 GC phase glossary |
| `references/fix_patterns.md` | Known leak patterns with symptoms and remediation |
| `references/mat_installation.md` | Eclipse MAT installation and headless operation guide |
| `references/harness_configuration.md` | Codex, Copilot, Claude MCP, HTTP, and direct dispatch hosting guide |
| `references/preflight_checklist.md` | Host/operator checks before wiring the skill into a harness |

---

## Assets Reference

| Asset | Description |
|-------|-------------|
| `assets/report_template.md` | Markdown report shape reference for future renderer templating |
| `assets/skill_card.md` | One-page skill summary card for team wikis |
