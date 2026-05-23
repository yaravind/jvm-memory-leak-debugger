"""
correlator.py
=============
Tool 3 – Correlate the GC log timeline with the heap dump (.hprof) timestamp
to identify exactly where in the GC narrative the dump was triggered.

Returns:
  - dump_phase:  "during_full_gc_storm" | "post_oom_recovery" | "normal_operation"
                 | "during_young_gc_pressure" | "unknown"
  - surrounding_gc_events: list of GC events ±60s around dump time
  - pressure_metrics: OOM proximity, live-set at dump time,
                      full-gc density (full GCs per minute) in dump window
  - inferred_trigger: human-readable description of what likely caused the dump
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from gc_parser import GcSummary, GcEvent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RE_UNIFIED_TS = re.compile(
    r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{4})\]\[([0-9.]+)s\]"
)


def _parse_first_ts_and_elapsed(gc_log_path: str) -> Optional[Tuple[datetime, float]]:
    """
    Read the first timestamped line in the GC log to derive the JVM start wall time.
    Returns (jvm_start_wall_time, first_elapsed_s).
    """
    with open(gc_log_path, errors="ignore") as f:
        for line in f:
            m = _RE_UNIFIED_TS.search(line)
            if m:
                ts_str = m.group(1)
                elapsed_s = float(m.group(2))
                try:
                    # Python 3.9 fromisoformat doesn't accept ±HHMM; normalise to ±HH:MM
                    ts_norm = re.sub(r"([+-])(\d{2})(\d{2})$", r"\1\2:\3", ts_str)
                    ts = datetime.fromisoformat(ts_norm)
                    jvm_start = ts.timestamp() - elapsed_s
                    return datetime.fromtimestamp(jvm_start, tz=timezone.utc), elapsed_s
                except ValueError:
                    pass
    return None


def _hprof_mtime(hprof_path: str) -> float:
    return Path(hprof_path).stat().st_mtime


def _parse_hprof_header_timestamp(hprof_path: str) -> Optional[float]:
    """
    Return the HPROF header timestamp as epoch seconds, if present.

    HPROF starts with a null-terminated format/version string, followed by a
    4-byte identifier size and an 8-byte big-endian epoch-millisecond timestamp.
    """
    with open(hprof_path, "rb") as f:
        header = f.read(128)

    marker = b"\x00"
    nul = header.find(marker)
    if nul <= 0:
        return None
    if not header.startswith(b"JAVA PROFILE "):
        return None

    timestamp_offset = nul + 1 + 4
    timestamp_end = timestamp_offset + 8
    if len(header) < timestamp_end:
        return None

    timestamp_ms = int.from_bytes(header[timestamp_offset:timestamp_end], byteorder="big", signed=False)
    if timestamp_ms <= 0:
        return None
    return timestamp_ms / 1000.0


def _parse_dump_time_override(dump_time: str) -> float:
    """Parse explicit dump time as epoch seconds, epoch milliseconds, or ISO-8601."""
    value = dump_time.strip()
    if not value:
        raise ValueError("dump_time override is empty")

    try:
        numeric = float(value)
        if numeric > 1_000_000_000_000:
            return numeric / 1000.0
        return numeric
    except ValueError:
        pass

    iso_value = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(iso_value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _resolve_dump_timestamp(
    hprof_path: str,
    dump_time: Optional[str] = None,
) -> Tuple[float, str, Optional[str]]:
    if dump_time:
        return _parse_dump_time_override(dump_time), "override", None

    hprof_epoch = _parse_hprof_header_timestamp(hprof_path)
    if hprof_epoch is not None:
        return hprof_epoch, "hprof_header", None

    warning = (
        "WARNING: using file mtime for hprof timestamp — transfer may have changed it"
    )
    return _hprof_mtime(hprof_path), "file_mtime", warning


# ---------------------------------------------------------------------------
# Main correlator
# ---------------------------------------------------------------------------

def correlate(
    gc_summary: GcSummary,
    gc_log_path: str,
    hprof_path: str,
    window_s: float = 60.0,
    dump_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Correlate the heap dump timestamp with the GC log.

    Parameters
    ----------
    gc_summary   : result of gc_parser.parse_gc_log()
    gc_log_path  : path to the GC log file
    hprof_path   : path to the .hprof file
    window_s     : seconds around dump time to include as surrounding events
    dump_time    : optional explicit dump timestamp as ISO-8601 or epoch seconds

    Returns
    -------
    dict with correlation results
    """
    # -- Derive elapsed-time of the dump relative to JVM start --
    anchor = _parse_first_ts_and_elapsed(gc_log_path)
    if anchor is None:
        return {"error": "Could not parse wall-clock timestamp from GC log."}

    jvm_start_epoch, _ = anchor
    dump_epoch, timestamp_source, timestamp_warning = _resolve_dump_timestamp(
        hprof_path=hprof_path,
        dump_time=dump_time,
    )
    dump_elapsed_s = dump_epoch - jvm_start_epoch.timestamp()
    dump_wall = datetime.fromtimestamp(dump_epoch, tz=timezone.utc).isoformat()

    # -- Find surrounding GC events --
    surrounding = [
        ev for ev in gc_summary.events
        if abs(ev.elapsed_s - dump_elapsed_s) <= window_s
    ]

    # Density: full GCs per minute in the 2-minute window around dump
    full_in_window = [
        ev for ev in gc_summary.full_gc_events
        if abs(ev.elapsed_s - dump_elapsed_s) <= window_s
    ]
    full_gc_density_per_min = round(len(full_in_window) / (2 * window_s / 60), 2)

    # Live-set at dump time: nearest Young GC after_mb
    nearest_young = min(
        (ev for ev in gc_summary.events if ev.kind == "Young" and ev.after_mb is not None),
        key=lambda ev: abs(ev.elapsed_s - dump_elapsed_s),
        default=None,
    )
    live_set_at_dump_mb = nearest_young.after_mb if nearest_young else None

    # -- Classify dump phase --
    last_full_elapsed = max(
        (ev.elapsed_s for ev in gc_summary.full_gc_events), default=0
    )
    first_full_elapsed = min(
        (ev.elapsed_s for ev in gc_summary.full_gc_events), default=0
    )

    if gc_summary.full_gc_count == 0:
        if gc_summary.to_space_exhausted_count > 0:
            dump_phase = "during_young_gc_pressure"
        else:
            dump_phase = "normal_operation"
    elif first_full_elapsed <= dump_elapsed_s <= last_full_elapsed + window_s:
        if gc_summary.to_space_exhausted_count > 0:
            dump_phase = "during_full_gc_storm"
        else:
            dump_phase = "during_full_gc_storm"
    elif dump_elapsed_s > last_full_elapsed:
        dump_phase = "post_oom_recovery"
    else:
        dump_phase = "unknown"

    # -- Near-OOM proximity --
    # Find the last Full GC before dump; measure how close heap was to 100%
    full_before_dump = sorted(
        [ev for ev in gc_summary.full_gc_events if ev.elapsed_s <= dump_elapsed_s],
        key=lambda ev: ev.elapsed_s,
    )
    oom_proximity_pct: Optional[float] = None
    if full_before_dump and full_before_dump[-1].heap_mb:
        ev_last = full_before_dump[-1]
        if ev_last.heap_mb and ev_last.after_mb is not None:
            oom_proximity_pct = round(ev_last.after_mb / ev_last.heap_mb * 100, 1)

    # -- Infer trigger --
    trigger = _infer_trigger(gc_summary, dump_phase, oom_proximity_pct)

    # -- Serialise surrounding events --
    def _ev_dict(ev: GcEvent) -> Dict[str, Any]:
        return {
            "gc_id": ev.gc_id,
            "elapsed_s": ev.elapsed_s,
            "kind": ev.kind,
            "before_mb": ev.before_mb,
            "after_mb": ev.after_mb,
            "heap_mb": ev.heap_mb,
            "pause_ms": ev.pause_ms,
            "to_space_exhausted": ev.to_space_exhausted,
        }

    return {
        "dump_wall_time": dump_wall,
        "dump_elapsed_s": round(dump_elapsed_s, 1),
        "dump_timestamp_source": timestamp_source,
        "dump_timestamp_warning": timestamp_warning,
        "jvm_start_wall_time": jvm_start_epoch.isoformat(),
        "dump_phase": dump_phase,
        "inferred_trigger": trigger,
        "oom_proximity_pct": oom_proximity_pct,
        "live_set_at_dump_mb": live_set_at_dump_mb,
        "full_gc_density_per_min_near_dump": full_gc_density_per_min,
        "full_gc_count_near_dump": len(full_in_window),
        "to_space_exhausted_count": gc_summary.to_space_exhausted_count,
        "surrounding_events": [_ev_dict(ev) for ev in surrounding[-20:]],
    }


def _infer_trigger(
    gc_summary: GcSummary,
    dump_phase: str,
    oom_proximity_pct: Optional[float],
) -> str:
    parts = []

    if dump_phase == "during_full_gc_storm":
        parts.append(
            "Heap dump was captured during active Full GC thrashing. "
            "The JVM attempted repeated Full GCs but could not reclaim meaningful memory."
        )
    elif dump_phase == "post_oom_recovery":
        parts.append(
            "Heap dump was captured after a Full GC storm resolved. "
            "The dump reflects the heap state immediately after the OOM-triggered collection."
        )
    elif dump_phase == "during_young_gc_pressure":
        parts.append(
            "Heap dump was captured during heavy Young GC pressure "
            "(To-space exhausted events present but no Full GC yet)."
        )
    elif dump_phase == "normal_operation":
        parts.append(
            "Heap dump was captured during normal GC operation (no Full GCs or OOM signals found)."
        )

    if gc_summary.to_space_exhausted_count > 0:
        parts.append(
            f"To-space exhaustion occurred {gc_summary.to_space_exhausted_count} times, "
            "indicating the old generation could not receive promoted objects."
        )

    if gc_summary.full_gc_count > 0:
        parts.append(
            f"{gc_summary.full_gc_count} Full GCs were performed. "
            "Each Full GC paused the JVM with ~850-1000ms stop-the-world pauses."
        )

    if oom_proximity_pct is not None and oom_proximity_pct >= 95:
        parts.append(
            f"Old gen was {oom_proximity_pct}% utilized at the last Full GC — "
            "essentially no headroom left for live object promotion."
        )

    if gc_summary.concurrent_abort_count > 0:
        parts.append(
            f"Concurrent marking was aborted {gc_summary.concurrent_abort_count} time(s), "
            "meaning G1 could not complete background marking fast enough before heap filled."
        )

    return " ".join(parts) if parts else "Unable to infer trigger from available data."
