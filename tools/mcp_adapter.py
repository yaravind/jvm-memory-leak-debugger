"""
mcp_adapter.py
==============
Packageable Claude/MCP server for the JVM memory leak debugger skill.
"""

import argparse

try:
    from mcp.server import FastMCP
    _MCP_IMPORT_ERROR = None
except ImportError as e:
    FastMCP = None
    _MCP_IMPORT_ERROR = e

from dispatch import dispatch_tool
from skill_resources import read_text


_FALLBACK_INSTRUCTIONS = (
    "Diagnose JVM memory leaks from .hprof heap dumps and JVM GC logs. "
    "Use the public tools for GC parsing, MAT suspect extraction, dump/GC "
    "correlation, and report generation. Do not fabricate missing evidence."
)

if FastMCP is not None:
    mcp = FastMCP(
        "jvm-memory-leak-debugger",
        instructions=read_text("instructions/system_prompt.md", _FALLBACK_INSTRUCTIONS),
    )

    @mcp.tool()
    def generate_report(
        hprof_path: str,
        gc_log_path: str,
        skip_mat: bool = False,
        mat_home: str = None,
        mat_heap_gb: int = 12,
        timeout_s: int = 7200,
        output_dir: str = None,
        patterns_file: str = None,
        dump_time: str = None,
    ) -> dict:
        """
        Full pipeline: parse GC log, correlate dump timestamp, run Eclipse MAT,
        apply fix-pattern matching, and write report.json + report.md.
        """
        return dispatch_tool("generate_report", {
            "hprof_path": hprof_path,
            "gc_log_path": gc_log_path,
            "output_dir": output_dir,
            "skip_mat": skip_mat,
            "mat_home": mat_home,
            "mat_heap_gb": mat_heap_gb,
            "timeout_s": timeout_s,
            "patterns_file": patterns_file,
            "dump_time": dump_time,
        })

    @mcp.tool()
    def analyze_gc_log(gc_log_path: str) -> dict:
        """Parse a JVM G1 unified GC log and return structured statistics."""
        return dispatch_tool("analyze_gc_log", {"gc_log_path": gc_log_path})

    @mcp.tool()
    def extract_heap_suspects(
        hprof_path: str,
        mat_home: str = None,
        mat_heap_gb: int = 12,
        timeout_s: int = 7200,
    ) -> dict:
        """Run Eclipse Memory Analyzer headlessly on an .hprof file."""
        return dispatch_tool("extract_heap_suspects", {
            "hprof_path": hprof_path,
            "mat_home": mat_home,
            "mat_heap_gb": mat_heap_gb,
            "timeout_s": timeout_s,
        })

    @mcp.tool()
    def correlate_dump_to_gc(
        gc_log_path: str,
        hprof_path: str,
        window_s: float = 60.0,
        dump_time: str = None,
    ) -> dict:
        """Correlate a heap dump timestamp with the GC log wall-clock timeline."""
        return dispatch_tool("correlate_dump_to_gc", {
            "gc_log_path": gc_log_path,
            "hprof_path": hprof_path,
            "window_s": window_s,
            "dump_time": dump_time,
        })
else:
    mcp = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JVM Memory Leak Debugger MCP adapter")
    parser.parse_args()
    if _MCP_IMPORT_ERROR is not None:
        raise SystemExit(
            "MCP SDK not installed. Run: pip install 'jvm-memory-leak-debugger[mcp]'\n"
            "For source checkouts on Python 3.10+: pip install -e '.[mcp]'"
        )
    mcp.run()


if __name__ == "__main__":
    main()
