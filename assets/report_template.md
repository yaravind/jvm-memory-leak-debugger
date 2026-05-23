# JVM Memory Leak Analysis

Severity: {{severity}}
Dump phase: {{dump_phase}}
OOM proximity: {{oom_proximity_pct}}

## Root Cause

{{root_cause}}

## GC Evidence

- Full GC count: {{full_gc_count}}
- To-space exhausted count: {{to_space_exhausted_count}}
- Live-set drift: {{live_set_drift_mb}}
- Dump timestamp source: {{dump_timestamp_source}}

## Heap Suspects

- MAT analysis status: {{heap_analysis_status}}
- Heap evidence gap: {{heap_analysis_error}}

{{heap_suspects}}

## Recommendations

{{recommendations}}

## Artifacts

- Machine-readable report: {{json_report_path}}
- Human-readable report: {{md_report_path}}

Template variables are illustrative. `reporter.py` currently renders Markdown
directly from `report.json`; keep this template aligned with the public report
contract if renderer templating is introduced later.
