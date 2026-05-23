"""
gc_parser.py
============
Tool 1 – Parse a JVM unified GC log (G1 format, -Xlog:gc*:file=...) and return
a structured summary suitable for correlation and reporting.

Handles:
  - Heap configuration (collector, max heap, region size)
  - Young / Full GC pause statistics (count, min/max/avg/p95/total)
  - To-space exhausted events
  - Metadata GC threshold triggers (rapid class-loading pressure)
  - Concurrent cycle aborts
  - Heap usage trend (live-set growth per Young GC)
  - Full GC timeline with before/after heap sizes
  - Final heap state at JVM exit
  - Correlation timestamp for matching GC log to heap dump
"""

import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class GcEvent:
    gc_id: int
    elapsed_s: float
    kind: str           # "Young" | "Full" | "Concurrent" | "Remark" | "Cleanup"
    reason: str         # e.g. "G1 Evacuation Pause", "Metadata GC Threshold"
    before_mb: Optional[float] = None
    after_mb: Optional[float] = None
    heap_mb: Optional[float] = None
    pause_ms: Optional[float] = None
    to_space_exhausted: bool = False
    concurrent_abort: bool = False


@dataclass
class HeapConfig:
    collector: str = "unknown"
    max_heap_mb: int = 0
    region_size_mb: int = 0
    compressed_oops: bool = False


@dataclass
class GcSummary:
    config: HeapConfig
    total_duration_s: float
    young_gc_count: int
    full_gc_count: int
    to_space_exhausted_count: int
    concurrent_abort_count: int
    metadata_gc_threshold_count: int

    # Pause stats  (ms)
    young_pauses: List[float]
    full_pauses: List[float]

    # Full GC timeline (for convergence / divergence analysis)
    full_gc_events: List[GcEvent]

    # Live-set growth  – retained after each Young GC (MB)
    young_after_mb: List[float]

    # Metaspace
    final_metaspace_used_kb: int = 0

    # Heap state at exit
    heap_exit_used_mb: float = 0.0
    heap_exit_total_mb: float = 0.0

    # Raw events for downstream use
    events: List[GcEvent] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_RE_HEADER = re.compile(
    r"\[(?P<ts>[^\]]+)\]\[(?P<elapsed>[0-9.]+)s\]\[info\]\[(?P<tag>[^\]]+)\]\s+(?P<msg>.*)"
)

_RE_PAUSE_YOUNG = re.compile(
    r"GC\((?P<id>\d+)\) Pause Young \((?P<reason>[^)]+)\) \((?P<detail>[^)]*)\)"
    r"|GC\((?P<id2>\d+)\) Pause Young \((?P<reason2>[^)]+)\)"
)

_RE_PAUSE_SUMMARY = re.compile(
    r"GC\((?P<id>\d+)\) Pause (?P<kind>Young|Full|Remark|Cleanup).*?"
    r"(?P<before>\d+)M->(?P<after>\d+)M\((?P<heap>\d+)M\) (?P<pause>[0-9.]+)ms"
)

_RE_PAUSE_FULL_SUMMARY = re.compile(
    r"GC\((?P<id>\d+)\) Pause Full.*?"
    r"(?P<before>\d+)M->(?P<after>\d+)M\((?P<heap>\d+)M\) (?P<pause>[0-9.]+)ms"
)

_RE_TO_SPACE = re.compile(r"GC\((?P<id>\d+)\) To-space exhausted")
_RE_CONCURRENT_ABORT = re.compile(r"GC\((?P<id>\d+)\) Concurrent Mark Abort")
_RE_METADATA_THRESHOLD = re.compile(r"Metadata GC Threshold")
_RE_USING_G1 = re.compile(r"Using G1")
_RE_REGION_SIZE = re.compile(r"Heap region size: (?P<size>\d+)M")
_RE_HEAP_ADDR = re.compile(r"size: (?P<size>\d+) MB")
_RE_HEAP_EXIT = re.compile(r"garbage-first heap\s+total (?P<total>\d+)K, used (?P<used>\d+)K")
_RE_META_EXIT = re.compile(r"Metaspace\s+used (?P<used>\d+)K")
_RE_CONCURRENT_CYCLE_MS = re.compile(r"GC\((?P<id>\d+)\) Concurrent Cycle (?P<ms>[0-9.]+)ms")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_gc_log(path: str) -> GcSummary:
    """Parse a JVM G1 unified GC log file and return a GcSummary."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"GC log not found: {path}")

    config = HeapConfig()
    events: List[GcEvent] = []
    young_pauses: List[float] = []
    full_pauses: List[float] = []
    full_gc_events: List[GcEvent] = []
    young_after_mb: List[float] = []
    to_space_ids: set = set()
    concurrent_abort_ids: set = set()
    metadata_threshold_count = 0
    heap_exit_used_mb = 0.0
    heap_exit_total_mb = 0.0
    final_metaspace_kb = 0
    first_elapsed = None
    last_elapsed = 0.0

    # Index GC events by id for enrichment
    event_by_id: Dict[int, GcEvent] = {}

    with open(path, errors="ignore") as f:
        for line in f:
            line = line.rstrip()
            m = _RE_HEADER.match(line)
            if not m:
                continue

            elapsed = float(m.group("elapsed"))
            tag = m.group("tag").strip()
            msg = m.group("msg").strip()

            if first_elapsed is None:
                first_elapsed = elapsed
            last_elapsed = elapsed

            # ---- Heap config ----
            if _RE_USING_G1.search(msg):
                config.collector = "G1"
            rs = _RE_REGION_SIZE.search(msg)
            if rs:
                config.region_size_mb = int(rs.group("size"))
            ha = _RE_HEAP_ADDR.search(msg)
            if ha and config.max_heap_mb == 0:
                config.max_heap_mb = int(ha.group("size"))
            if "Compressed Oops" in msg:
                config.compressed_oops = True

            # ---- Metadata GC threshold ----
            if _RE_METADATA_THRESHOLD.search(msg):
                metadata_threshold_count += 1

            # ---- To-space exhausted ----
            tse = _RE_TO_SPACE.search(msg)
            if tse:
                to_space_ids.add(int(tse.group("id")))

            # ---- Concurrent abort ----
            ca = _RE_CONCURRENT_ABORT.search(msg)
            if ca:
                concurrent_abort_ids.add(int(ca.group("id")))

            # ---- Pause summaries ----
            ps = _RE_PAUSE_SUMMARY.search(msg)
            if ps:
                gc_id = int(ps.group("id"))
                kind = ps.group("kind")
                ev = GcEvent(
                    gc_id=gc_id,
                    elapsed_s=elapsed,
                    kind=kind,
                    reason="",
                    before_mb=float(ps.group("before")),
                    after_mb=float(ps.group("after")),
                    heap_mb=float(ps.group("heap")),
                    pause_ms=float(ps.group("pause")),
                )
                event_by_id[gc_id] = ev
                events.append(ev)
                if kind == "Young":
                    young_pauses.append(ev.pause_ms)
                    young_after_mb.append(ev.after_mb)
                elif kind == "Full":
                    full_pauses.append(ev.pause_ms)
                    full_gc_events.append(ev)

            pf = _RE_PAUSE_FULL_SUMMARY.search(msg)
            if pf and "Pause Full" in msg and not ps:
                gc_id = int(pf.group("id"))
                ev = GcEvent(
                    gc_id=gc_id,
                    elapsed_s=elapsed,
                    kind="Full",
                    reason="G1 Evacuation Pause",
                    before_mb=float(pf.group("before")),
                    after_mb=float(pf.group("after")),
                    heap_mb=float(pf.group("heap")),
                    pause_ms=float(pf.group("pause")),
                )
                event_by_id[gc_id] = ev
                events.append(ev)
                full_pauses.append(ev.pause_ms)
                full_gc_events.append(ev)

            # ---- Heap exit ----
            he = _RE_HEAP_EXIT.search(msg)
            if he:
                heap_exit_total_mb = int(he.group("total")) / 1024
                heap_exit_used_mb = int(he.group("used")) / 1024

            # ---- Metaspace exit ----
            me = _RE_META_EXIT.search(msg)
            if me:
                final_metaspace_kb = int(me.group("used"))

    # Enrich events with to-space / concurrent-abort flags
    for ev in events:
        if ev.gc_id in to_space_ids:
            ev.to_space_exhausted = True
        if ev.gc_id in concurrent_abort_ids:
            ev.concurrent_abort = True

    total_duration = last_elapsed - (first_elapsed or 0)

    return GcSummary(
        config=config,
        total_duration_s=round(total_duration, 3),
        young_gc_count=len(young_pauses),
        full_gc_count=len(full_pauses),
        to_space_exhausted_count=len(to_space_ids),
        concurrent_abort_count=len(concurrent_abort_ids),
        metadata_gc_threshold_count=metadata_threshold_count // 2,  # start+summary each logged
        young_pauses=young_pauses,
        full_pauses=full_pauses,
        full_gc_events=full_gc_events,
        young_after_mb=young_after_mb,
        final_metaspace_used_kb=final_metaspace_kb,
        heap_exit_used_mb=round(heap_exit_used_mb, 1),
        heap_exit_total_mb=round(heap_exit_total_mb, 1),
        events=events,
    )


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def _stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"count": 0, "min": 0, "max": 0, "avg": 0, "p95": 0, "total": 0}
    sorted_v = sorted(values)
    p95_idx = max(0, int(len(sorted_v) * 0.95) - 1)
    return {
        "count": len(values),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "avg": round(statistics.mean(values), 2),
        "p95": round(sorted_v[p95_idx], 2),
        "total": round(sum(values), 1),
    }


def gc_summary_to_dict(s: GcSummary) -> Dict[str, Any]:
    """Convert GcSummary to a plain dict for JSON serialisation."""
    full_gc_timeline = []
    for ev in s.full_gc_events:
        full_gc_timeline.append({
            "gc_id": ev.gc_id,
            "elapsed_s": ev.elapsed_s,
            "before_mb": ev.before_mb,
            "after_mb": ev.after_mb,
            "heap_mb": ev.heap_mb,
            "pause_ms": ev.pause_ms,
        })

    # Live-set growth: compare after_mb over sliding window of 10 young GCs
    live_set_drift_mb = None
    if len(s.young_after_mb) >= 20:
        first10 = statistics.mean(s.young_after_mb[:10])
        last10 = statistics.mean(s.young_after_mb[-10:])
        live_set_drift_mb = round(last10 - first10, 1)

    return {
        "config": {
            "collector": s.config.collector,
            "max_heap_mb": s.config.max_heap_mb,
            "region_size_mb": s.config.region_size_mb,
            "compressed_oops": s.config.compressed_oops,
        },
        "runtime_s": s.total_duration_s,
        "young_gc": _stats(s.young_pauses),
        "full_gc": _stats(s.full_pauses),
        "full_gc_count": s.full_gc_count,
        "to_space_exhausted_count": s.to_space_exhausted_count,
        "concurrent_abort_count": s.concurrent_abort_count,
        "metadata_gc_threshold_triggers": s.metadata_gc_threshold_count,
        "live_set_drift_mb": live_set_drift_mb,
        "full_gc_timeline": full_gc_timeline,
        "final_metaspace_used_kb": s.final_metaspace_used_kb,
        "heap_exit_used_mb": s.heap_exit_used_mb,
        "heap_exit_total_mb": s.heap_exit_total_mb,
    }

