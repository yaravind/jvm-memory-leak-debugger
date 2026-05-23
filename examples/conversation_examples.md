# Conversation Examples

## Full Incident Analysis

User:

```text
Analyze /var/log/app/java_pid8123.hprof with /var/log/app/gc-8123.log.
```

Agent flow:

1. Call `generate_report` with the heap dump and GC log paths.
2. Wait for MAT when needed.
3. Return severity, dump phase, root cause, top recommendations, and report
   paths.

Response shape:

```text
## JVM Memory Leak Analysis

Severity: CRITICAL
Dump phase: during_full_gc_storm
OOM proximity: 100%

Root cause:
The heap dump was captured during a Full GC storm and MAT shows one retained
object graph dominating the heap.

Top recommendations:
1. Bound or stream the retaining collection.
2. Reduce map-heavy per-entry overhead in the retained path.
3. Increase heap only as a temporary mitigation.

Full report: /var/log/app/report.md
```

## GC Log Triage Only

User:

```text
I only have the GC log right now: build/jvm-logs/gc-9441.log
```

Agent flow:

1. Call `analyze_gc_log`.
2. Explain whether the GC log indicates leak-like pressure.
3. Ask for the heap dump before making MAT-backed object-graph claims.

## Transferred Heap Dump

User:

```text
The dump was copied from prod, so its file timestamp is wrong. The OOM happened
at 2026-05-22T16:18:36-04:00.
```

Agent flow:

1. Pass the provided time as `dump_time`.
2. Prefer the override over file mtime.
3. Mention `dump_timestamp_source` if the final report depends on it.
