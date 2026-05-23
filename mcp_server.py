"""
mcp_server.py
=============
Claude MCP server for the jvm-memory-leak-debugger skill.

Install:       pip install mcp
Register:      add to ~/Library/Application Support/Claude/claude_desktop_config.json
Run directly:  python3 mcp_server.py

See README.md for full deployment instructions.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

try:
    from mcp.server import FastMCP
except ImportError:
    raise SystemExit(
        "MCP SDK not installed. Run: pip install mcp\n"
        "See https://github.com/modelcontextprotocol/python-sdk"
    )

from debug_memory_leak import run_full_analysis
from gc_parser import parse_gc_log, gc_summary_to_dict
from mat_runner import analyse_hprof
from correlator import correlate as _correlate

mcp = FastMCP(
    "jvm-memory-leak-debugger",
    instructions=open(
        os.path.join(os.path.dirname(__file__), "instructions", "system_prompt.md")
    ).read(),
)


@mcp.tool()
def generate_report(
    hprof_path: str,
    gc_log_path: str,
    skip_mat: bool = False,
    mat_heap_gb: int = 12,
    output_dir: str = None,
) -> dict:
    """
    Full pipeline: parse GC log, correlate dump timestamp, run Eclipse MAT,
    apply fix-pattern matching, and write report.json + report.md.

    Returns severity, top_recommendations, json_report_path, md_report_path.
    """
    return run_full_analysis(
        hprof_path=hprof_path,
        gc_log_path=gc_log_path,
        output_dir=output_dir,
        skip_mat=skip_mat,
        mat_heap_gb=mat_heap_gb,
    )


@mcp.tool()
def analyze_gc_log(gc_log_path: str) -> dict:
    """
    Parse a JVM G1 unified GC log and return structured statistics:
    pause counts, Full GC timeline, To-space exhaustion events, live-set drift,
    concurrent cycle aborts, and heap config.
    """
    return gc_summary_to_dict(parse_gc_log(gc_log_path))


@mcp.tool()
def extract_heap_suspects(
    hprof_path: str,
    mat_heap_gb: int = 12,
    timeout_s: int = 7200,
) -> dict:
    """
    Run Eclipse Memory Analyzer (MAT) headlessly on an .hprof file.
    Auto-downloads MAT (~92 MB) on first use.
    Returns leak suspects with stack frames, dominator paths, and class histogram.
    """
    return analyse_hprof(
        hprof_path=hprof_path,
        mat_heap_gb=mat_heap_gb,
        timeout_s=timeout_s,
    )


@mcp.tool()
def correlate_dump_to_gc(
    gc_log_path: str,
    hprof_path: str,
    window_s: float = 60.0,
) -> dict:
    """
    Correlate the heap dump file timestamp with the GC log wall-clock timeline.
    Returns dump_phase (during_full_gc_storm / post_oom_recovery / normal_operation),
    oom_proximity_pct, live_set_at_dump_mb, inferred_trigger, and surrounding GC events.
    """
    from gc_parser import parse_gc_log as _parse
    gc_sum = _parse(gc_log_path)
    return _correlate(gc_sum, gc_log_path, hprof_path, window_s=window_s)


if __name__ == "__main__":
    mcp.run()

