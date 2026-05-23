"""
test_correlator.py - Unit tests for dump timestamp resolution.
"""
import os
from datetime import datetime, timezone

import pytest

import correlator
import gc_parser


SAMPLE_GC_LOG = """\
[2026-05-22T16:12:21.714-0400][0.013s][info][gc          ] Using G1
[2026-05-22T16:12:23.967-0400][2.253s][info][gc,start    ] GC(0) Pause Young (Normal) (G1 Evacuation Pause)
[2026-05-22T16:12:23.969-0400][2.255s][info][gc          ] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 34M->15M(576M) 2.023ms
[2026-05-22T16:17:22.445-0400][300.733s][info][gc        ] GC(286) Pause Full (G1 Evacuation Pause) 8192M->7580M(8192M) 853.231ms
"""


def _write_gc_log(tmp_path):
    path = tmp_path / "gc.log"
    path.write_text(SAMPLE_GC_LOG)
    return path


def _write_hprof(tmp_path, epoch_ms):
    path = tmp_path / "dump.hprof"
    path.write_bytes(
        b"JAVA PROFILE 1.0.2\x00"
        + (4).to_bytes(4, byteorder="big")
        + int(epoch_ms).to_bytes(8, byteorder="big")
        + b"\x00\x00"
    )
    return path


def test_parse_hprof_header_timestamp(tmp_path):
    epoch_ms = 1_779_474_742_714
    hprof = _write_hprof(tmp_path, epoch_ms)

    assert correlator._parse_hprof_header_timestamp(str(hprof)) == pytest.approx(epoch_ms / 1000)


def test_correlate_prefers_hprof_header_timestamp_over_mtime(tmp_path):
    gc_log = _write_gc_log(tmp_path)
    gc_summary = gc_parser.parse_gc_log(str(gc_log))
    first_ts = datetime.fromisoformat("2026-05-22T16:12:21.714-04:00").timestamp()
    dump_epoch = first_ts + 300.733
    hprof = _write_hprof(tmp_path, int(dump_epoch * 1000))

    wrong_mtime = first_ts + 9_999
    os.utime(hprof, (wrong_mtime, wrong_mtime))

    result = correlator.correlate(gc_summary, str(gc_log), str(hprof), window_s=5)

    assert result["dump_timestamp_source"] == "hprof_header"
    assert result["dump_timestamp_warning"] is None
    assert result["dump_elapsed_s"] == pytest.approx(300.7, abs=0.1)
    assert result["full_gc_count_near_dump"] == 1


def test_correlate_dump_time_override_wins_over_hprof_header(tmp_path):
    gc_log = _write_gc_log(tmp_path)
    gc_summary = gc_parser.parse_gc_log(str(gc_log))
    first_ts = datetime.fromisoformat("2026-05-22T16:12:21.714-04:00").timestamp()
    hprof = _write_hprof(tmp_path, int((first_ts + 300.733) * 1000))

    override = datetime.fromtimestamp(first_ts + 2.255, tz=timezone.utc).isoformat()
    result = correlator.correlate(
        gc_summary,
        str(gc_log),
        str(hprof),
        window_s=5,
        dump_time=override,
    )

    assert result["dump_timestamp_source"] == "override"
    assert result["dump_elapsed_s"] == pytest.approx(2.3, abs=0.1)
    assert result["surrounding_events"][0]["kind"] == "Young"


def test_correlate_falls_back_to_mtime_with_warning(tmp_path):
    gc_log = _write_gc_log(tmp_path)
    gc_summary = gc_parser.parse_gc_log(str(gc_log))
    first_ts = datetime.fromisoformat("2026-05-22T16:12:21.714-04:00").timestamp()
    hprof = tmp_path / "not-really.hprof"
    hprof.write_bytes(b"not a valid hprof")
    dump_epoch = first_ts + 2.255
    os.utime(hprof, (dump_epoch, dump_epoch))

    result = correlator.correlate(gc_summary, str(gc_log), str(hprof), window_s=5)

    assert result["dump_timestamp_source"] == "file_mtime"
    assert "mtime" in result["dump_timestamp_warning"]
    assert result["dump_elapsed_s"] == pytest.approx(2.3, abs=0.1)
