"""
test_mcp_adapter.py - MCP adapter smoke tests.

These tests require the optional mcp extra and are skipped in core-only
environments.
"""
from pathlib import Path

import pytest

pytest.importorskip("mcp")

import mcp_server
import mcp_adapter


FIXTURES = Path(__file__).parent / "fixtures"
GC_LOG = FIXTURES / "gc-16615.log"


def test_mcp_analyze_gc_log_wrapper_dispatches():
    result = mcp_server.analyze_gc_log(str(GC_LOG))
    adapter_result = mcp_adapter.analyze_gc_log(str(GC_LOG))

    assert result["config"]["collector"] == "G1"
    assert result["full_gc_count"] == 33
    assert adapter_result["full_gc_count"] == 33


def test_mcp_correlate_wrapper_accepts_dump_time(tmp_path):
    hprof = tmp_path / "dump.hprof"
    hprof.write_bytes(b"placeholder")

    result = mcp_server.correlate_dump_to_gc(
        gc_log_path=str(GC_LOG),
        hprof_path=str(hprof),
        dump_time="2026-05-22T16:18:36-04:00",
    )

    assert result["dump_timestamp_source"] == "override"
    assert result["dump_phase"] == "during_full_gc_storm"
