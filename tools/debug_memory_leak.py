#!/usr/bin/env python3
"""
debug_memory_leak.py
====================
Primary skill entrypoint. Provides both:
  1. A CLI interface:   python3 debug_memory_leak.py --hprof <path> --gc-log <path>
  2. A callable API:    from tools.debug_memory_leak import run_full_analysis

This module is the `generate_report` tool in skill.json.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# Ensure tools/ is importable when called directly
sys.path.insert(0, str(Path(__file__).parent))

from dispatch import dispatch_tool
from mat_runner import DEFAULT_MAT_HOME, runtime_diagnostics
from pipeline import run_full_analysis

__all__ = ["main", "run_full_analysis"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_runtime_diagnostics(status: dict) -> None:
    print("[jvm-memory-leak-debugger] runtime check")
    print(f"  Platform:      {status['platform_key']}")
    print(f"  Supported:     {status['platform_supported']}")
    print(f"  Java 17+:      {status['java_17_plus']}")
    if status.get("java_home"):
        print(f"  Java home:     {status['java_home']}")
    print(f"  MAT version:   {status['mat_version']}")
    print(f"  MAT home:      {status['mat_home']}")
    print(f"  MAT installed: {status['mat_installed']}")
    if status.get("mat_eclipse_dir"):
        print(f"  Eclipse dir:   {status['mat_eclipse_dir']}")
    print(f"  curl:          {status.get('curl_available', False)}")
    print(f"  Auto-install:  {status['can_auto_install_mat']}")
    print(f"  Ready:         {status['ready_for_analysis']}")
    if status.get("errors"):
        print("\n  Issues:")
        for error in status["errors"]:
            print(f"    - {error}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="JVM Memory Leak Debugger - GC log + hprof -> structured report"
    )
    ap.add_argument("--hprof")
    ap.add_argument("--gc-log", dest="gc_log")
    ap.add_argument("--output-dir", default=None, dest="output_dir")
    ap.add_argument(
        "--mat-home",
        default=None,
        dest="mat_home",
        help=f"Optional Eclipse MAT install root (default: {DEFAULT_MAT_HOME}).",
    )
    ap.add_argument("--mat-heap-gb", type=int, default=12, dest="mat_heap_gb")
    ap.add_argument(
        "--timeout-s",
        type=int,
        default=7200,
        dest="timeout_s",
        help="Timeout in seconds for MAT analysis (default: 7200).",
    )
    ap.add_argument(
        "--patterns-file",
        default=None,
        dest="patterns_file",
        help="Optional JSON file with custom recommendation patterns.",
    )
    ap.add_argument("--skip-mat", action="store_true", dest="skip_mat")
    ap.add_argument(
        "--dump-time",
        default=None,
        dest="dump_time",
        help="Optional heap dump timestamp override as ISO-8601, epoch seconds, or epoch milliseconds.",
    )
    ap.add_argument(
        "--check-runtime",
        action="store_true",
        dest="check_runtime",
        help="Check local platform, Java 17+, and MAT installation readiness without reading artifacts.",
    )
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--json", action="store_true", help="Print result JSON to stdout")
    args = ap.parse_args()

    if args.check_runtime:
        status = runtime_diagnostics(
            Path(args.mat_home) if args.mat_home else DEFAULT_MAT_HOME
        )
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            _print_runtime_diagnostics(status)
        return 0 if status["ready_for_analysis"] else 1

    if not args.hprof:
        print("ERROR: --hprof is required unless --check-runtime is used.", file=sys.stderr)
        return 2
    if not args.gc_log:
        print("ERROR: --gc-log is required unless --check-runtime is used.", file=sys.stderr)
        return 2

    if not Path(args.hprof).exists():
        print(f"ERROR: hprof not found: {args.hprof}", file=sys.stderr)
        return 1
    if not Path(args.gc_log).exists():
        print(f"ERROR: GC log not found: {args.gc_log}", file=sys.stderr)
        return 1

    print(f"[jvm-memory-leak-debugger] hprof:  {args.hprof}")
    print(f"[jvm-memory-leak-debugger] gc-log: {args.gc_log}")

    result = dispatch_tool("generate_report", {
        "hprof_path": args.hprof,
        "gc_log_path": args.gc_log,
        "output_dir": args.output_dir,
        "skip_mat": args.skip_mat,
        "mat_home": args.mat_home,
        "mat_heap_gb": args.mat_heap_gb,
        "timeout_s": args.timeout_s,
        "patterns_file": args.patterns_file,
        "dump_time": args.dump_time,
    })

    print(f"\n  Severity:  {result['severity']}")
    print(f"  JSON:      {result['json_report_path']}")
    print(f"  Markdown:  {result['md_report_path']}")

    print("\n  Top Recommendations:")
    for i, rec in enumerate(result["top_recommendations"], 1):
        print(f"    #{i} {rec['title']}")
        if rec.get("code_pointer"):
            print(f"       -> {rec['code_pointer']}")
        for fix in rec.get("fixes", []):
            print(f"       • {fix}")

    if args.json:
        print("\n--- JSON ---")
        print(json.dumps(result, indent=2, default=str))

    if args.open:
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", result["md_report_path"]], check=False)
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
