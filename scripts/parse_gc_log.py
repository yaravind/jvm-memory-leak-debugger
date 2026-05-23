#!/usr/bin/env python3
"""
parse_gc_log.py
---------------
Standalone CLI wrapper around gc_parser.parse_gc_log / gc_summary_to_dict.
Prints a JSON summary of a JVM G1 GC log to stdout.

Usage:
    python3 scripts/parse_gc_log.py <gc_log_path>
    python3 scripts/parse_gc_log.py <gc_log_path> --pretty
"""
import argparse
import json
import sys
from pathlib import Path

# Allow running from the repo root or scripts/ directory
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent / "tools"))

import gc_parser


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Parse a JVM G1 GC log and emit a JSON summary."
    )
    ap.add_argument("gc_log", help="Path to the JVM GC log file")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = ap.parse_args()

    log_path = Path(args.gc_log)
    if not log_path.exists():
        print(f"ERROR: GC log not found: {log_path}", file=sys.stderr)
        return 1

    try:
        gc_sum = gc_parser.parse_gc_log(str(log_path))
        data = gc_parser.gc_summary_to_dict(gc_sum)
    except Exception as exc:
        print(f"ERROR: Failed to parse GC log: {exc}", file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps(data, indent=indent, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

