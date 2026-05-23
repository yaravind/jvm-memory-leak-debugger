"""
test_gc_parser.py — Unit tests for gc_parser tool
"""
import sys
import os
import pytest

import gc_parser


SAMPLE_GC_LOG = """\
[2026-05-22T16:12:21.714-0400][0.013s][info][gc,heap     ] Heap region size: 2M
[2026-05-22T16:12:21.727-0400][0.013s][info][gc          ] Using G1
[2026-05-22T16:12:23.967-0400][2.253s][info][gc,start    ] GC(0) Pause Young (Normal) (G1 Evacuation Pause)
[2026-05-22T16:12:23.969-0400][2.255s][info][gc          ] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 34M->15M(576M) 2.023ms
[2026-05-22T16:17:22.445-0400][300.733s][info][gc        ] GC(286) Pause Full (G1 Evacuation Pause) 8192M->7580M(8192M) 853.231ms
[2026-05-22T16:17:22.445-0400][300.740s][info][gc        ] GC(287) To-space exhausted
[2026-05-22T16:17:23.447-0400][301.736s][info][gc        ] GC(288) Pause Full (G1 Evacuation Pause) 8190M->8190M(8192M) 995.000ms
[2026-05-22T16:17:23.450-0400][301.738s][info][gc,marking ] GC(289) Concurrent Mark Abort
"""

import tempfile


def _write_log(content):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    f.write(content)
    f.close()
    return f.name


def test_gc_parser_basic():
    path = _write_log(SAMPLE_GC_LOG)
    summary = gc_parser.parse_gc_log(path)
    data = gc_parser.gc_summary_to_dict(summary)
    os.unlink(path)

    assert data["config"]["collector"] == "G1"
    assert data["config"]["region_size_mb"] == 2
    assert data["young_gc"]["count"] == 1
    assert data["full_gc_count"] == 2
    assert data["to_space_exhausted_count"] == 1
    assert data["concurrent_abort_count"] == 1


def test_full_gc_stats():
    path = _write_log(SAMPLE_GC_LOG)
    summary = gc_parser.parse_gc_log(path)
    data = gc_parser.gc_summary_to_dict(summary)
    os.unlink(path)

    assert data["full_gc"]["max"] == pytest.approx(995.0, abs=0.1)
    assert data["full_gc"]["min"] == pytest.approx(853.231, abs=0.1)
    assert data["full_gc"]["count"] == 2


def test_full_gc_timeline():
    path = _write_log(SAMPLE_GC_LOG)
    summary = gc_parser.parse_gc_log(path)
    data = gc_parser.gc_summary_to_dict(summary)
    os.unlink(path)

    timeline = data["full_gc_timeline"]
    assert len(timeline) == 2
    assert timeline[0]["gc_id"] == 286
    assert timeline[0]["before_mb"] == pytest.approx(8192)
    assert timeline[0]["after_mb"] == pytest.approx(7580)


def test_runtime_duration():
    path = _write_log(SAMPLE_GC_LOG)
    summary = gc_parser.parse_gc_log(path)
    data = gc_parser.gc_summary_to_dict(summary)
    os.unlink(path)

    # First line at 0.013s, last at 301.738s → duration ~301.7s
    assert data["runtime_s"] > 300


def test_empty_log():
    path = _write_log("")
    summary = gc_parser.parse_gc_log(path)
    data = gc_parser.gc_summary_to_dict(summary)
    os.unlink(path)

    assert data["full_gc_count"] == 0
    assert data["young_gc"]["count"] == 0

