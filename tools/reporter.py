"""
reporter.py
===========
Tool 4 – Produce a structured JSON artifact and a human-readable Markdown report
from the outputs of gc_parser, mat_runner, and correlator.

The JSON is the machine-readable source of truth.
The Markdown surfaces the most actionable findings for a human operator.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# JSON artifact writer
# ---------------------------------------------------------------------------

def write_json_report(data: Dict[str, Any], output_path: str) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return str(p)


# ---------------------------------------------------------------------------
# Markdown generation helpers
# ---------------------------------------------------------------------------

def _mb(v: Optional[float]) -> str:
    if v is None:
        return "N/A"
    if v >= 1024:
        return f"{v / 1024:.1f} GB"
    return f"{v:.0f} MB"


def _ms(v: Optional[float]) -> str:
    if v is None:
        return "N/A"
    return f"{v:.1f} ms"


def _pct(v: Optional[float]) -> str:
    if v is None:
        return "N/A"
    return f"{v:.1f}%"


def severity_badge(gc: Dict[str, Any], corr: Dict[str, Any]) -> str:
    """Return a severity label: CRITICAL / HIGH / MEDIUM / LOW."""
    full_count = gc.get("full_gc_count", 0)
    tse = gc.get("to_space_exhausted_count", 0)
    oom_pct = corr.get("oom_proximity_pct") or 0
    if full_count >= 10 or oom_pct >= 99:
        return "🔴 CRITICAL"
    if full_count >= 2 or tse >= 5:
        return "🟠 HIGH"
    if tse > 0 or full_count >= 1:
        return "🟡 MEDIUM"
    return "🟢 LOW"


# ---------------------------------------------------------------------------
# Fix recommendations
# ---------------------------------------------------------------------------

_BUILTIN_PATTERN_SOURCE = "builtin"
_PATTERN_PUBLIC_FIELDS = ("id", "title", "description", "fixes", "code_pointer", "pattern_source")

_BUILTIN_PATTERNS: List[Dict[str, Any]] = [
    {
        "id": "large_thread_local_retention",
        "match_class": r"Thread|java\.lang\.Thread|main",
        "match_stack": r"",
        "match_text": r"keeps local variables|Thread Stack|local variables",
        "title": "Thread-local retention is keeping a large object graph live",
        "description": (
            "MAT reports that a thread stack or local variable is retaining most of the "
            "heap. This usually means a request, batch job, query, parser, or collection "
            "builder has materialised a large data set and has not released it yet."
        ),
        "fixes": [
            "Inspect the stack frames for the retaining thread and identify the operation "
            "that owns the live collection or object graph.",
            "Replace full materialisation with streaming, pagination, chunked processing, "
            "or bounded batching where possible.",
            "Clear or narrow the lifetime of large local variables before long waits, "
            "blocking calls, or retries.",
            "Add an input-size guard so unexpected production data volume fails with a "
            "clear error before exhausting heap.",
        ],
        "code_pointer": None,
    },
    {
        "id": "collection_builder_retention",
        "match_class": r"VectorBuilder|ArrayList|HashMap|HashSet|ListBuffer|StringBuilder|ByteArrayOutputStream",
        "match_stack": r"",
        "match_text": r"",
        "title": "Collection or buffer builder is retaining accumulated data",
        "description": (
            "A collection, map, string, byte buffer, or builder appears in the retained "
            "object graph. Builders are expected to hold everything added to them until "
            "they are flushed, drained, or converted, so they commonly expose unbounded "
            "batching and aggregation problems."
        ),
        "fixes": [
            "Bound the collection size and fail fast when the limit is exceeded.",
            "Process records incrementally instead of retaining the entire input in one builder.",
            "For unavoidable large results, spill to disk or use a distributed/partitioned "
            "execution path instead of driver memory.",
        ],
        "code_pointer": None,
    },
    {
        "id": "map_entry_overhead",
        "match_class": r"HashMap|LinkedHashMap|ConcurrentHashMap|TreeMap|Tuple2|Map\$|HashTrieMap",
        "match_stack": r"",
        "match_text": r"",
        "title": "Map-heavy representation is amplifying per-entry memory cost",
        "description": (
            "Map implementations can create several objects per logical entry. When a "
            "heap dump is dominated by map nodes, entries, tuples, boxed values, or "
            "strings, the logical payload may be much smaller than the retained heap."
        ),
        "fixes": [
            "Replace per-row or per-cell maps with array-backed, columnar, ordinal, or "
            "primitive-aware structures for hot paths.",
            "Intern or deduplicate repeated keys and categorical values only after measuring the tradeoff.",
            "Prefer compact domain objects over generic maps when the schema is known.",
        ],
        "code_pointer": None,
    },
    {
        "id": "to_space_exhausted",
        "match_class": r"",
        "match_stack": r"",
        "match_text": r"",
        "gc": {"min_to_space_exhausted": 1},
        "title": "Repeated To-space exhaustion causing Full GC cascade",
        "description": (
            "G1 GC reported repeated 'To-space exhausted' events, meaning the JVM had no "
            "survivor/old-gen space to evacuate live objects into during Young GC. Each "
            "To-space event triggered a Full GC (stop-the-world compaction), resulting in "
            "~850-1000ms application pauses. The Full GCs following To-space events reclaimed "
            "almost nothing (8192M→8190M) indicating near-total heap retention."
        ),
        "fixes": [
            "Reduce the live-set size (see object graph fixes above) — this is the root cause.",
            "As a short-term mitigation, increase `-Xmx` to give G1 more headroom, but note "
            "this only delays the OOM if the source data volume grows further.",
            "The long-term fix is reducing the retained live set: stream, partition, cap, "
            "or compact the workload that is keeping objects live.",
        ],
        "code_pointer": None,
    },
]


def load_patterns(patterns_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return built-in patterns plus optional user-supplied JSON patterns."""
    patterns = [_with_source(p, _BUILTIN_PATTERN_SOURCE) for p in _BUILTIN_PATTERNS]
    seen_ids = {p["id"] for p in patterns}
    path = patterns_file or os.environ.get("PATTERNS_FILE")
    if not path:
        return patterns

    custom_path = Path(path)
    with open(custom_path) as f:
        loaded = json.load(f)

    custom_patterns = loaded.get("patterns") if isinstance(loaded, dict) else loaded
    if not isinstance(custom_patterns, list):
        raise ValueError("patterns file must contain a list or an object with a 'patterns' list")

    source = str(custom_path)
    validated_custom = []
    for idx, pattern in enumerate(custom_patterns):
        validated = _validate_pattern(pattern, source, idx)
        if validated["id"] in seen_ids:
            raise ValueError(f"duplicate pattern id: {validated['id']}")
        seen_ids.add(validated["id"])
        validated_custom.append(validated)
    return patterns + validated_custom


def _with_source(pattern: Dict[str, Any], source: str) -> Dict[str, Any]:
    enriched = dict(pattern)
    enriched["pattern_source"] = source
    return enriched


def _validate_pattern(pattern: Dict[str, Any], source: str, index: int = 0) -> Dict[str, Any]:
    label = f"pattern[{index}]"
    if not isinstance(pattern, dict):
        raise ValueError(f"{label} must be an object")
    for field in ("id", "title", "description", "fixes"):
        if field not in pattern:
            raise ValueError(f"{label} missing required field: {field}")
    if not isinstance(pattern["fixes"], list) or not all(isinstance(f, str) for f in pattern["fixes"]):
        raise ValueError(f"{label} fixes must be a list of strings")

    validated = {
        "id": str(pattern["id"]),
        "title": str(pattern["title"]),
        "description": str(pattern["description"]),
        "fixes": list(pattern["fixes"]),
        "code_pointer": pattern.get("code_pointer"),
        "match_class": str(pattern.get("match_class", "")),
        "match_stack": str(pattern.get("match_stack", "")),
        "match_text": str(pattern.get("match_text", "")),
        "gc": pattern.get("gc", {}),
        "pattern_source": source,
    }
    if validated["code_pointer"] is not None:
        validated["code_pointer"] = str(validated["code_pointer"])
    if not isinstance(validated["gc"], dict):
        raise ValueError(f"{label} gc field must be an object when present")
    _validate_gc_conditions(validated["gc"], label)
    _validate_regex_fields(validated, label)
    if not any(validated.get(field) for field in ("match_class", "match_stack", "match_text")) and not validated["gc"]:
        raise ValueError(
            f"{label} must define at least one matcher: match_class, match_stack, match_text, or gc"
        )
    return validated


def _validate_gc_conditions(conditions: Dict[str, Any], label: str) -> None:
    allowed = {"min_to_space_exhausted", "min_full_gc_count", "min_concurrent_abort_count"}
    for key, value in conditions.items():
        if key not in allowed:
            raise ValueError(f"{label} gc contains unsupported condition: {key}")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{label} gc.{key} must be a non-negative integer")


def _validate_regex_fields(pattern: Dict[str, Any], label: str) -> None:
    for field in ("match_class", "match_stack", "match_text"):
        value = pattern.get(field, "")
        if not value:
            continue
        try:
            re.compile(value)
        except re.error as e:
            raise ValueError(f"{label} {field} is not a valid regex: {e}") from e


def _public_recommendation(pattern: Dict[str, Any]) -> Dict[str, Any]:
    return {field: pattern.get(field) for field in _PATTERN_PUBLIC_FIELDS if field in pattern}


def _gc_conditions_match(pattern: Dict[str, Any], gc_data: Dict[str, Any]) -> bool:
    conditions = pattern.get("gc") or {}
    min_to_space = conditions.get("min_to_space_exhausted")
    if min_to_space is not None and gc_data.get("to_space_exhausted_count", 0) < min_to_space:
        return False
    min_full_gc = conditions.get("min_full_gc_count")
    if min_full_gc is not None and gc_data.get("full_gc_count", 0) < min_full_gc:
        return False
    min_abort = conditions.get("min_concurrent_abort_count")
    if min_abort is not None and gc_data.get("concurrent_abort_count", 0) < min_abort:
        return False
    return True


def _regex_matches(pattern: str, text: str) -> bool:
    return not pattern or re.search(pattern, text, re.IGNORECASE) is not None


def _match_patterns(
    suspects: List[Dict[str, Any]],
    gc_data: Dict[str, Any],
    patterns: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Return applicable fix recommendations based on suspect classes and stack frames."""
    matched: List[Dict[str, Any]] = []
    seen_ids: set = set()

    all_class_text = " ".join(
        " ".join(str(v) for v in s.values()) for s in suspects
    )
    all_stack_text = " ".join(
        " ".join(s.get("stack_frames", [])) for s in suspects
    )
    histogram_text = " ".join(
        e.get("class", "") for e in gc_data.get("histogram", [])
    )
    combined = all_class_text + " " + all_stack_text + " " + histogram_text

    active_patterns = patterns if patterns is not None else load_patterns()
    for pattern in active_patterns:
        if pattern["id"] in seen_ids:
            continue
        gc_ok = _gc_conditions_match(pattern, gc_data)
        class_ok = _regex_matches(pattern.get("match_class", ""), combined)
        stack_ok = _regex_matches(pattern.get("match_stack", ""), all_stack_text)
        text_ok = _regex_matches(pattern.get("match_text", ""), combined)
        if gc_ok and class_ok and stack_ok and text_ok:
            matched.append(_public_recommendation(pattern))
            seen_ids.add(pattern["id"])

    return matched


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def build_report(
    gc_data: Dict[str, Any],
    mat_findings: Dict[str, Any],
    correlation: Dict[str, Any],
    hprof_path: str,
    gc_log_path: str,
    patterns_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Assemble the full structured report dict."""
    suspects = mat_findings.get("suspects", [])
    histogram = mat_findings.get("histogram", [])
    patterns = load_patterns(patterns_file)
    recommendations = _match_patterns(suspects, {**mat_findings, **gc_data}, patterns)
    severity = severity_badge(gc_data, correlation)

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "severity": severity,
        "inputs": {
            "hprof": hprof_path,
            "gc_log": gc_log_path,
        },
        "gc_analysis": gc_data,
        "heap_dump_analysis": {
            "analysis_status": mat_findings.get("analysis_status", "unknown"),
            "error": mat_findings.get("error"),
            "suspects": suspects,
            "histogram": histogram[:20],
            "suspects_zip": mat_findings.get("suspects_zip"),
        },
        "correlation": correlation,
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------

def write_markdown_report(report: Dict[str, Any], output_path: str) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    gc = report["gc_analysis"]
    corr = report["correlation"]
    suspects = report["heap_dump_analysis"]["suspects"]
    histogram = report["heap_dump_analysis"]["histogram"]
    recs = report["recommendations"]
    heap_status = report["heap_dump_analysis"].get("analysis_status", "unknown")
    heap_error = report["heap_dump_analysis"].get("error")

    lines: List[str] = []

    def h(level: int, text: str):
        lines.append("\n" + "#" * level + " " + text + "\n")

    def p_line(text: str):
        lines.append(text)

    def blank():
        lines.append("")

    # ---- Title ----
    lines.append("# JVM Memory Leak Debug Report")
    lines.append(f"\n_Generated: {report['generated_at']}_\n")
    lines.append("| Item | Value |")
    lines.append("|------|-------|")
    lines.append(f"| Heap dump | `{report['inputs']['hprof']}` |")
    lines.append(f"| GC log    | `{report['inputs']['gc_log']}` |")
    lines.append(f"| Severity  | {report.get('severity', severity_badge(gc, corr))} |")
    blank()

    # ---- Executive summary ----
    h(2, "Executive Summary")
    cfg = gc.get("config", {})
    corr_phase = corr.get("dump_phase", "unknown")
    p_line(
        f"The JVM ran for **{gc.get('runtime_s', '?')} seconds** using **{cfg.get('collector', '?')}** "
        f"with a **{_mb(cfg.get('max_heap_mb'))} max heap**."
    )
    blank()
    p_line(corr.get("inferred_trigger", ""))
    blank()

    # Key numbers table
    yg = gc.get("young_gc", {})
    fg = gc.get("full_gc", {})
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Young GC count | {yg.get('count', 0)} |")
    lines.append(f"| Young GC avg pause | {_ms(yg.get('avg'))} |")
    lines.append(f"| Young GC max pause | {_ms(yg.get('max'))} |")
    lines.append(f"| Full GC count | {gc.get('full_gc_count', 0)} |")
    lines.append(f"| Full GC avg pause | {_ms(fg.get('avg'))} |")
    lines.append(f"| Full GC max pause | {_ms(fg.get('max'))} |")
    lines.append(f"| Total Full GC pause time | {_ms(fg.get('total'))} |")
    lines.append(f"| To-space exhausted events | {gc.get('to_space_exhausted_count', 0)} |")
    lines.append(f"| Concurrent mark aborts | {gc.get('concurrent_abort_count', 0)} |")
    lines.append(f"| Live-set drift (first→last Young GC) | {_mb(gc.get('live_set_drift_mb'))} |")
    lines.append(f"| Heap at dump | {_mb(corr.get('live_set_at_dump_mb'))} live / {_mb(cfg.get('max_heap_mb'))} max |")
    lines.append(f"| OOM proximity at last Full GC | {_pct(corr.get('oom_proximity_pct'))} |")
    lines.append(f"| Dump phase | `{corr_phase}` |")
    blank()

    # ---- Full GC timeline ----
    full_timeline = gc.get("full_gc_timeline", [])
    if full_timeline:
        h(2, "Full GC Storm Timeline")
        p_line(
            f"First Full GC at **{full_timeline[0].get('elapsed_s')}s**, "
            f"last at **{full_timeline[-1].get('elapsed_s')}s** "
            f"({round(full_timeline[-1].get('elapsed_s', 0) - full_timeline[0].get('elapsed_s', 0), 1)}s window)."
        )
        blank()
        lines.append("| GC# | Elapsed (s) | Before → After | Heap | Pause (ms) |")
        lines.append("|-----|-------------|----------------|------|------------|")
        for ev in full_timeline[:30]:
            lines.append(
                f"| {ev.get('gc_id')} | {ev.get('elapsed_s')} "
                f"| {_mb(ev.get('before_mb'))} → {_mb(ev.get('after_mb'))} "
                f"| {_mb(ev.get('heap_mb'))} "
                f"| {_ms(ev.get('pause_ms'))} |"
            )
        if len(full_timeline) > 30:
            p_line(f"\n_…and {len(full_timeline) - 30} more Full GC events._")
        blank()

    # ---- Leak suspects ----
    h(2, "Heap Dump: Leak Suspects")
    if heap_status:
        p_line(f"**MAT analysis status:** `{heap_status}`")
        blank()
    if heap_error:
        p_line(f"**Heap evidence gap:** {heap_error}")
        blank()
    if not suspects:
        p_line("_No suspects extracted. Check the suspects_zip for manual inspection._")
    for s in suspects[:3]:
        h(3, f"Suspect #{s.get('suspect_number', '?')}")
        p_line(f"**Retained heap:** {_mb(s.get('retained_bytes', 0) / 1_048_576 if s.get('retained_bytes') else None)} "
               f"({_pct(s.get('retained_pct'))})")
        blank()

        if s.get("description"):
            p_line(f"_{s['description'][:400]}_")
            blank()

        if s.get("accumulation_point"):
            p_line(f"**Accumulation point:** `{s['accumulation_point']}`")
            blank()

        frames = s.get("stack_frames", [])
        if frames:
            p_line("**Key stack frames:**")
            lines.append("```")
            for frame in frames[:20]:
                lines.append(frame)
            lines.append("```")
            blank()

        graph = s.get("object_graph_classes", [])
        if graph:
            p_line("**Object graph — top classes in dominator tree:**")
            lines.append("```")
            for g in graph[:15]:
                lines.append(g)
            lines.append("```")
            blank()

    # ---- Class histogram ----
    if histogram:
        h(2, "Class Histogram (Top Retained)")
        lines.append("| Class | Objects | Shallow | Retained |")
        lines.append("|-------|---------|---------|---------|")
        for entry in histogram[:20]:
            cls = entry.get("class", "?")
            obj = f"{entry.get('objects', 0):,}"
            sha = _mb(entry.get("shallow_bytes", 0) / 1_048_576)
            ret = _mb(entry.get("retained_bytes", 0) / 1_048_576)
            lines.append(f"| `{cls}` | {obj} | {sha} | {ret} |")
        blank()

    # ---- Recommendations ----
    h(2, "Recommendations")
    if not recs:
        p_line("_No specific recommendations matched. Review heap dump manually._")
    for i, rec in enumerate(recs, 1):
        h(3, f"#{i} — {rec['title']}")
        p_line(rec["description"])
        blank()
        if rec.get("code_pointer"):
            p_line(f"**Code pointer:** `{rec['code_pointer']}`")
            blank()
        p_line("**Fixes:**")
        for fix in rec["fixes"]:
            lines.append(f"- {fix}")
        blank()

    # ---- Footer ----
    h(2, "Artifacts")
    lines.append("| Artifact | Path |")
    lines.append("|----------|------|")
    lines.append(f"| Heap dump | `{report['inputs']['hprof']}` |")
    lines.append(f"| GC log | `{report['inputs']['gc_log']}` |")
    if report["heap_dump_analysis"].get("suspects_zip"):
        lines.append(f"| MAT Suspects ZIP | `{report['heap_dump_analysis']['suspects_zip']}` |")
    blank()
    p_line("_Open the MAT Suspects ZIP in a browser or Eclipse Memory Analyzer for interactive exploration._")
    blank()
    p_line("_Report generated by `tools/mem-leak-debugger/debug_memory_leak.py`._")

    content = "\n".join(lines)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return str(p)
