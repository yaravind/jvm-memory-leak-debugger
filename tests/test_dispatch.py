"""
test_dispatch.py - Shared tool registry tests.
"""
import json
from pathlib import Path

import pytest

import dispatch


FIXTURES = Path(__file__).parent / "fixtures"
GC_LOG = FIXTURES / "gc-16615.log"


def test_registry_contains_public_skill_tools():
    assert set(dispatch.TOOLS) == {
        "analyze_gc_log",
        "extract_heap_suspects",
        "correlate_dump_to_gc",
        "generate_report",
    }


def test_dispatch_analyze_gc_log():
    result = dispatch.dispatch_tool("analyze_gc_log", {"gc_log_path": str(GC_LOG)})

    assert result["config"]["collector"] == "G1"
    assert result["full_gc_count"] == 33


def test_dispatch_correlate_dump_to_gc_with_override(tmp_path):
    hprof = tmp_path / "dump.hprof"
    hprof.write_bytes(b"placeholder")

    result = dispatch.dispatch_tool(
        "correlate_dump_to_gc",
        {
            "gc_log_path": str(GC_LOG),
            "hprof_path": str(hprof),
            "dump_time": "2026-05-22T16:18:36-04:00",
        },
    )

    assert result["dump_timestamp_source"] == "override"
    assert result["dump_phase"] == "during_full_gc_storm"


def test_dispatch_generate_report_skip_mat(tmp_path):
    hprof = tmp_path / "dump.hprof"
    hprof.write_bytes(b"placeholder")

    result = dispatch.dispatch_tool(
        "generate_report",
        {
            "gc_log_path": str(GC_LOG),
            "hprof_path": str(hprof),
            "output_dir": str(tmp_path / "report"),
            "skip_mat": True,
            "dump_time": "2026-05-22T16:18:36-04:00",
        },
    )

    report = json.load(open(result["json_report_path"]))
    assert result["severity"] == "CRITICAL"
    assert report["correlation"]["dump_timestamp_source"] == "override"
    assert report["heap_dump_analysis"]["analysis_status"] == "skipped"
    assert "MAT analysis skipped" in report["heap_dump_analysis"]["error"]


def test_dispatch_generate_report_does_not_write_invalid_report(monkeypatch, tmp_path):
    hprof = tmp_path / "dump.hprof"
    hprof.write_bytes(b"placeholder")

    def invalid_report(**kwargs):
        return {"schema_version": "not-valid"}

    monkeypatch.setattr("pipeline.reporter.build_report", invalid_report)

    with pytest.raises(Exception) as exc:
        dispatch.dispatch_tool(
            "generate_report",
            {
                "gc_log_path": str(GC_LOG),
                "hprof_path": str(hprof),
                "output_dir": str(tmp_path / "report"),
                "skip_mat": True,
                "dump_time": "2026-05-22T16:18:36-04:00",
            },
        )

    assert "missing required" in str(exc.value) or "expected one of" in str(exc.value)
    assert not (tmp_path / "report" / "report.json").exists()


def test_dispatch_generate_report_forwards_timeout(monkeypatch, tmp_path):
    hprof = tmp_path / "dump.hprof"
    gc_log = tmp_path / "gc.log"
    mat_home = tmp_path / "mat-home"
    hprof.write_bytes(b"placeholder")
    gc_log.write_text("[0.001s][info][gc] Using G1\n")
    captured = {}

    def fake_run_full_analysis(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(dispatch, "run_full_analysis", fake_run_full_analysis)

    result = dispatch.dispatch_tool(
        "generate_report",
        {
            "gc_log_path": str(gc_log),
            "hprof_path": str(hprof),
            "mat_home": str(mat_home),
            "timeout_s": 123,
        },
    )

    assert result == {"ok": True}
    assert captured["mat_home"] == str(mat_home)
    assert captured["timeout_s"] == 123


def test_dispatch_missing_required_parameter():
    with pytest.raises(dispatch.ToolDispatchError) as exc:
        dispatch.dispatch_tool("analyze_gc_log", {})

    assert exc.value.status_code == 422
    assert "gc_log_path" in str(exc.value)


def test_dispatch_requires_object_parameters():
    with pytest.raises(dispatch.ToolDispatchError) as exc:
        dispatch.dispatch_tool("analyze_gc_log", [])

    assert exc.value.status_code == 422
    assert "JSON object" in str(exc.value)


def test_dispatch_unknown_tool():
    with pytest.raises(dispatch.ToolDispatchError) as exc:
        dispatch.dispatch_tool("missing_tool", {})

    assert exc.value.status_code == 404
