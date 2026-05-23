"""
test_e2e_real_gc.py
====================
End-to-end tests that run against the REAL GC log and (optionally) the real
heap dump from the data-diff pid 16615 OOM incident.

Marker strategy
---------------
  @pytest.mark.e2e_gc    — uses only gc-16615.log (always available; runs in CI)
  @pytest.mark.e2e_full  — requires java_pid16615.hprof (skipped in CI unless
                           HPROF_PATH is set or the file exists in fixtures/)

Run locally (GC-only):
    PYTHONPATH=tools pytest tests/test_e2e_real_gc.py -v -m e2e_gc

Run locally (full pipeline — needs hprof):
    ln -s $(git rev-parse --show-toplevel)/target/jvm-logs/java_pid16615.hprof \\
          tests/fixtures/java_pid16615.hprof
    PYTHONPATH=tools pytest tests/test_e2e_real_gc.py -v -m e2e_full

    # or via env var:
    HPROF_PATH=/path/to/java_pid16615.hprof \\
      PYTHONPATH=tools pytest tests/test_e2e_real_gc.py -v -m e2e_full
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

import gc_parser
import correlator
import reporter

# ---------------------------------------------------------------------------
# Fixture paths
# ---------------------------------------------------------------------------

_FIXTURES = Path(__file__).parent / "fixtures"
REAL_GC_LOG = _FIXTURES / "gc-16615.log"

# hprof resolution: fixtures dir first, then HPROF_PATH env var
_FIXTURE_HPROF = _FIXTURES / "java_pid16615.hprof"
_ENV_HPROF = os.environ.get("HPROF_PATH", "")
REAL_HPROF = (
    str(_FIXTURE_HPROF) if _FIXTURE_HPROF.exists()
    else (_ENV_HPROF if _ENV_HPROF and Path(_ENV_HPROF).exists() else None)
)

HPROF_AVAILABLE = REAL_HPROF is not None


# ---------------------------------------------------------------------------
# Shared parsed state (computed once per session)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def real_gc_summary():
    assert REAL_GC_LOG.exists(), f"Fixture not found: {REAL_GC_LOG}"
    return gc_parser.parse_gc_log(str(REAL_GC_LOG))


@pytest.fixture(scope="session")
def real_gc_data(real_gc_summary):
    return gc_parser.gc_summary_to_dict(real_gc_summary)


# ---------------------------------------------------------------------------
# GC-log-only E2E tests  (marker: e2e_gc)
# Always run — no hprof needed. These are the CI gate tests.
# ---------------------------------------------------------------------------

@pytest.mark.e2e_gc
def test_real_gc_collector(real_gc_data):
    """G1 collector is detected from the real log."""
    assert real_gc_data["config"]["collector"] == "G1"


@pytest.mark.e2e_gc
def test_real_gc_heap_config(real_gc_data):
    """8 GB max heap and 2 MB region size are parsed correctly."""
    assert real_gc_data["config"]["max_heap_mb"] == 8192
    assert real_gc_data["config"]["region_size_mb"] == 2


@pytest.mark.e2e_gc
def test_real_gc_young_count(real_gc_data):
    """All 471 Young GC events are counted."""
    assert real_gc_data["young_gc"]["count"] == 471


@pytest.mark.e2e_gc
def test_real_gc_full_count(real_gc_data):
    """All 33 Full GC events are counted."""
    assert real_gc_data["full_gc_count"] == 33


@pytest.mark.e2e_gc
def test_real_gc_to_space_exhausted(real_gc_data):
    """31 To-space exhausted events are detected."""
    assert real_gc_data["to_space_exhausted_count"] == 31


@pytest.mark.e2e_gc
def test_real_gc_concurrent_aborts(real_gc_data):
    """16 Concurrent Mark Abort events are counted."""
    assert real_gc_data["concurrent_abort_count"] == 16


@pytest.mark.e2e_gc
def test_real_gc_max_pause(real_gc_data):
    """Max Full GC pause is ~1016 ms (worst STW in the storm)."""
    assert real_gc_data["full_gc"]["max"] == pytest.approx(1016.36, abs=1.0)


@pytest.mark.e2e_gc
def test_real_gc_runtime(real_gc_data):
    """JVM ran for ~435 seconds total."""
    assert real_gc_data["runtime_s"] == pytest.approx(435.66, abs=1.0)


@pytest.mark.e2e_gc
def test_real_gc_timeline_length(real_gc_data):
    """Full GC timeline has exactly 33 entries."""
    assert len(real_gc_data["full_gc_timeline"]) == 33


@pytest.mark.e2e_gc
def test_real_gc_timeline_first_event(real_gc_data):
    """First Full GC at GC#286 with 8192→7580 MB heap change."""
    first = real_gc_data["full_gc_timeline"][0]
    assert first["gc_id"] == 286
    assert first["before_mb"] == pytest.approx(8192, abs=1)
    assert first["after_mb"] == pytest.approx(7580, abs=1)
    assert first["elapsed_s"] == pytest.approx(300.733, abs=0.1)


@pytest.mark.e2e_gc
def test_real_gc_timeline_last_event(real_gc_data):
    """Last Full GC at GC#365 with 8190→22 MB (heap freed by OOM recovery)."""
    last = real_gc_data["full_gc_timeline"][-1]
    assert last["gc_id"] == 365
    assert last["before_mb"] == pytest.approx(8190, abs=1)
    assert last["after_mb"] == pytest.approx(22, abs=1)
    assert last["elapsed_s"] == pytest.approx(374.992, abs=0.1)


@pytest.mark.e2e_gc
def test_real_gc_severity_critical(real_gc_data):
    """33 Full GCs → CRITICAL severity."""
    mock_corr = {"oom_proximity_pct": 100.0}
    badge = reporter.severity_badge(real_gc_data, mock_corr)
    assert "CRITICAL" in badge


@pytest.mark.e2e_gc
def test_real_gc_pattern_to_space_matched(real_gc_data):
    """to_space_exhausted pattern is matched from real GC data."""
    mock_mat = {"suspects": [], "histogram": []}
    report = reporter.build_report(
        gc_data=real_gc_data,
        mat_findings=mock_mat,
        correlation={"dump_phase": "during_full_gc_storm", "oom_proximity_pct": 100.0},
        hprof_path="/dev/null",
        gc_log_path=str(REAL_GC_LOG),
    )
    ids = [r["id"] for r in report["recommendations"]]
    assert "to_space_exhausted" in ids


@pytest.mark.e2e_gc
def test_real_gc_json_report_roundtrip(real_gc_data):
    """JSON report written from real GC data loads correctly with expected fields."""
    mock_mat = {"suspects": [], "histogram": []}
    mock_corr = {
        "dump_phase": "during_full_gc_storm",
        "oom_proximity_pct": 100.0,
        "inferred_trigger": "Real GC log test.",
        "live_set_at_dump_mb": 8190.0,
    }
    report = reporter.build_report(
        gc_data=real_gc_data,
        mat_findings=mock_mat,
        correlation=mock_corr,
        hprof_path="/dev/null",
        gc_log_path=str(REAL_GC_LOG),
    )
    with tempfile.TemporaryDirectory() as td:
        path = reporter.write_json_report(report, f"{td}/report.json")
        loaded = json.load(open(path))

    assert loaded["schema_version"] == "1.0"
    assert loaded["gc_analysis"]["full_gc_count"] == 33
    assert loaded["gc_analysis"]["to_space_exhausted_count"] == 31
    assert len(loaded["gc_analysis"]["full_gc_timeline"]) == 33


@pytest.mark.e2e_gc
def test_real_gc_markdown_report_content(real_gc_data):
    """Markdown report generated from real GC data contains key sections."""
    mock_mat = {"suspects": [], "histogram": []}
    mock_corr = {
        "dump_phase": "during_full_gc_storm",
        "oom_proximity_pct": 100.0,
        "inferred_trigger": "Real GC log test.",
        "live_set_at_dump_mb": 8190.0,
    }
    report = reporter.build_report(
        gc_data=real_gc_data,
        mat_findings=mock_mat,
        correlation=mock_corr,
        hprof_path="/dev/null",
        gc_log_path=str(REAL_GC_LOG),
    )
    with tempfile.TemporaryDirectory() as td:
        path = reporter.write_markdown_report(report, f"{td}/report.md")
        content = open(path).read()

    assert "# JVM Memory Leak Debug Report" in content
    assert "CRITICAL" in content
    assert "Full GC Storm Timeline" in content
    assert "GC#286" in content or "286" in content
    assert "Recommendations" in content


# ---------------------------------------------------------------------------
# Full pipeline E2E tests  (marker: e2e_full)
# Skipped in CI unless hprof is present (HPROF_PATH or fixture symlink).
# ---------------------------------------------------------------------------

_skip_no_hprof = pytest.mark.skipif(
    not HPROF_AVAILABLE,
    reason=(
        "java_pid16615.hprof not available. "
        "Symlink to tests/fixtures/ or set HPROF_PATH. "
        "See tests/fixtures/README.md."
    ),
)


@pytest.mark.e2e_full
@_skip_no_hprof
def test_real_correlate_dump_phase(real_gc_summary):
    """Correlator classifies the real dump as 'during_full_gc_storm'."""
    result = correlator.correlate(
        gc_summary=real_gc_summary,
        gc_log_path=str(REAL_GC_LOG),
        hprof_path=REAL_HPROF,
    )
    assert result.get("dump_phase") == "during_full_gc_storm"


@pytest.mark.e2e_full
@_skip_no_hprof
def test_real_correlate_oom_proximity(real_gc_summary):
    """OOM proximity is ≥ 95% — heap was essentially full at dump time."""
    result = correlator.correlate(
        gc_summary=real_gc_summary,
        gc_log_path=str(REAL_GC_LOG),
        hprof_path=REAL_HPROF,
    )
    assert result.get("oom_proximity_pct", 0) >= 95.0


@pytest.mark.e2e_full
@_skip_no_hprof
def test_real_full_pipeline_skip_mat(real_gc_data, tmp_path):
    """
    Full pipeline run with --skip-mat (no MAT binary needed).
    Validates report.json + report.md are written with correct structure.
    """
    import debug_memory_leak

    result = debug_memory_leak.run_full_analysis(
        hprof_path=REAL_HPROF,
        gc_log_path=str(REAL_GC_LOG),
        output_dir=str(tmp_path),
        skip_mat=True,
    )

    # Check return contract
    assert result["severity"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
    assert Path(result["json_report_path"]).exists()
    assert Path(result["md_report_path"]).exists()

    # Validate JSON report content
    report = json.load(open(result["json_report_path"]))
    assert report["schema_version"] == "1.0"
    assert report["gc_analysis"]["full_gc_count"] == 33
    assert report["gc_analysis"]["to_space_exhausted_count"] == 31
    assert report["correlation"]["dump_phase"] == "during_full_gc_storm"
    assert len(report["recommendations"]) > 0
    assert "to_space_exhausted" in [r["id"] for r in report["recommendations"]]

    # Validate Markdown report
    md_content = open(result["md_report_path"]).read()
    assert "CRITICAL" in md_content
    assert "Full GC Storm Timeline" in md_content

    # Severity should be CRITICAL (33 Full GCs)
    assert result["severity"] == "CRITICAL"
