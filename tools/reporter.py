"""
reporter.py
===========
Tool 4 – Produce a structured JSON artifact and a human-readable Markdown report
from the outputs of gc_parser, mat_runner, and correlator.

The JSON is the machine-readable source of truth.
The Markdown surfaces the most actionable findings for a human operator.
"""

import json
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
    with open(p, "w") as f:
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


def _severity_badge(gc: Dict[str, Any], corr: Dict[str, Any]) -> str:
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

_KNOWN_PATTERNS: List[Dict[str, Any]] = [
    {
        "id": "unbounded_jdbc_read",
        "match_class": r"JdbcDatasetReader|readResultSet",
        "match_stack": r"readResultSet|JdbcDatasetReader",
        "title": "Unbounded JDBC ResultSet fully materialised into memory",
        "description": (
            "`JdbcDatasetReader.readResultSet()` streams an entire SQL table into a "
            "`VectorBuilder[DataRow]` with no row limit. Each row is stored as an immutable "
            "`HashMap[String, Option[String]]` producing ~6× object-count overhead per row "
            "(Tuple2 + HashMap1 + HashTrieMap + Some + String + byte[] per cell). "
            "With tens of millions of rows this exhausts even an 8 GB heap."
        ),
        "fixes": [
            "Add a configurable `maxRows` guard in `readResultSet()` — fail fast with a "
            "clear `IllegalStateException` if the row count exceeds the limit.",
            "Replace `Map[String, Option[String]]` in `DataRow` with an `Array`-backed "
            "structure keyed by column ordinal to eliminate per-row HashMap allocation overhead.",
            "Consider lazy/streaming processing: process rows in a streaming `foldLeft` "
            "rather than fully materialising into a `Vector`.",
            "Add query validation: detect `SELECT *` without a `LIMIT` clause and emit a "
            "WARNING or configurable hard-stop.",
            "If the query is intentional for large datasets, consider a Spark-mode execution "
            "path where the dataset is processed in partitions rather than fully in-driver memory.",
        ],
        "code_pointer": "src/main/scala/com/tccc/dna/diff/engine/local/JdbcDatasetReader.scala:97-105",
    },
    {
        "id": "vectorbuilder_leak",
        "match_class": r"VectorBuilder",
        "match_stack": r"VectorBuilder",
        "title": "scala.collection.immutable.VectorBuilder retaining entire dataset",
        "description": (
            "A single `VectorBuilder` on the `main` thread accumulated the entire result set "
            "in the dominator tree. The builder is never flushed until `result()` is called, "
            "which only happens after all rows are read — making the entire dataset live "
            "simultaneously in memory."
        ),
        "fixes": [
            "Use an iterator-based pipeline instead of a builder when processing large result sets.",
            "If the full `Vector` is required downstream, cap input rows before building it.",
        ],
        "code_pointer": "src/main/scala/com/tccc/dna/diff/engine/local/JdbcDatasetReader.scala:97",
    },
    {
        "id": "immutable_hashmap_overhead",
        "match_class": r"HashMap\$HashMap1|HashMap\$HashTrieMap",
        "match_stack": r"",
        "title": "Excessive immutable HashMap per-row overhead",
        "description": (
            "Each `DataRow` uses `Map[String, Option[String]]` which Scala implements as a "
            "linked `HashMap1` / `HashTrieMap` tree. At 44M+ rows this creates ~60M+ "
            "`HashMap1` objects, ~60M `Tuple2`, ~60M `Some`, and ~60M `String` instances, "
            "totalling ~5-6 GB for a dataset that could be represented in ~500 MB with "
            "columnar or array-backed storage."
        ),
        "fixes": [
            "Replace `DataRow(values: Map[String, Option[String]])` with "
            "`DataRow(ordinals: Array[Option[String]], schema: DatasetSchema)` — "
            "reduce per-row allocation from ~6 objects to 1 array.",
            "Use primitive-aware encoders for numeric columns to avoid boxing.",
        ],
        "code_pointer": "src/main/scala/com/tccc/dna/diff/domain/DataRow.scala",
    },
    {
        "id": "to_space_exhausted",
        "match_class": r"",
        "match_stack": r"",
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
            "The long-term fix is row-capped or streaming JDBC reads.",
        ],
        "code_pointer": None,
    },
]


def _match_patterns(suspects: List[Dict[str, Any]], gc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
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

    # Always include to_space_exhausted if present
    if gc_data.get("to_space_exhausted_count", 0) > 0:
        for p in _KNOWN_PATTERNS:
            if p["id"] == "to_space_exhausted":
                matched.append(p)
                seen_ids.add(p["id"])

    for pattern in _KNOWN_PATTERNS:
        if pattern["id"] in seen_ids:
            continue
        class_ok = not pattern["match_class"] or re.search(pattern["match_class"], combined)
        stack_ok = not pattern["match_stack"] or re.search(pattern["match_stack"], combined)
        if class_ok and stack_ok:
            matched.append(pattern)
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
) -> Dict[str, Any]:
    """Assemble the full structured report dict."""
    suspects = mat_findings.get("suspects", [])
    histogram = mat_findings.get("histogram", [])
    recommendations = _match_patterns(suspects, {**mat_findings, **gc_data})

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "inputs": {
            "hprof": hprof_path,
            "gc_log": gc_log_path,
        },
        "gc_analysis": gc_data,
        "heap_dump_analysis": {
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
    lines.append(f"| Item | Value |")
    lines.append(f"|------|-------|")
    lines.append(f"| Heap dump | `{report['inputs']['hprof']}` |")
    lines.append(f"| GC log    | `{report['inputs']['gc_log']}` |")
    lines.append(f"| Severity  | {_severity_badge(gc, corr)} |")
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
    with open(p, "w") as f:
        f.write(content)
    return str(p)

