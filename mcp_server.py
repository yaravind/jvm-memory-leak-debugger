"""
mcp_server.py
=============
Compatibility wrapper for the packageable MCP adapter.

Run source checkouts with:
    python3 mcp_server.py

Run installed environments with:
    jvm-memory-leak-debugger-mcp
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

import mcp_adapter as _adapter

mcp = _adapter.mcp
main = _adapter.main

if mcp is not None:
    generate_report = _adapter.generate_report
    analyze_gc_log = _adapter.analyze_gc_log
    extract_heap_suspects = _adapter.extract_heap_suspects
    correlate_dump_to_gc = _adapter.correlate_dump_to_gc

__all__ = [
    "mcp",
    "main",
    "generate_report",
    "analyze_gc_log",
    "extract_heap_suspects",
    "correlate_dump_to_gc",
]


if __name__ == "__main__":
    main()
