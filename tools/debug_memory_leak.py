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
import os
import subprocess
import sys
from pathlib import Path

# Ensure tools/ is importable when called directly
sys.path.insert(0, str(Path(__file__).parent))

import gc_parser
import correlator
import reporter


# ---------------------------------------------------------------------------
# Public API (callable by agent runtimes)
# ---------------------------------------------------------------------------

def run_full_analysis(
    hprof_path: str,
    gc_log_path: str,
    output_dir: str = None,
    skip_mat: bool = False,
    mat_heap_gb: int = 12,
    timeout_s: int = 7200,
) -> dict:
    """
    Full pipeline: parse GC log → correlate → MAT analysis → build reports.

    Returns:
        {
            "json_report_path": str,
            "md_report_path": str,
            "severity": str,            # CRITICAL / HIGH / MEDIUM / LOW
            "top_recommendations": list,
            "gc_summary": dict,
            "correlation": dict,
            "suspects": list,
        }
    """
    hprof = str(Path(hprof_path).resolve())
    gc_log = str(Path(gc_log_path).resolve())

    out_dir = Path(output_dir) if output_dir else Path(gc_log).parent / "memleak-report"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: GC log
    gc_sum = gc_parser.parse_gc_log(gc_log)
    gc_data = gc_parser.gc_summary_to_dict(gc_sum)

    # Step 2: Correlation
    try:
        corr = correlator.correlate(gc_sum, gc_log, hprof)
    except Exception as e:
        corr = {"error": str(e), "dump_phase": "unknown"}

    # Step 3: MAT
    mat_findings: dict = {"suspects": [], "histogram": [], "suspects_zip": None}
    if not skip_mat:
        try:
            from mat_runner import analyse_hprof
            mat_findings = analyse_hprof(
                hprof_path=hprof,
                mat_heap_gb=mat_heap_gb,
                timeout_s=timeout_s,
            )
        except Exception as e:
            mat_findings = {"suspects": [], "histogram": [], "error": str(e)}
    else:
        # Try to reuse existing suspects zip
        from mat_runner import _parse_leak_suspects
        zip_path = Path(hprof).parent / (Path(hprof).stem + "_Leak_Suspects.zip")
        if zip_path.exists():
            try:
                mat_findings = _parse_leak_suspects(zip_path)
                mat_findings["suspects_zip"] = str(zip_path)
            except Exception:
                pass

    # Step 4: Build report
    full_report = reporter.build_report(
        gc_data=gc_data,
        mat_findings=mat_findings,
        correlation=corr,
        hprof_path=hprof,
        gc_log_path=gc_log,
    )

    json_path = reporter.write_json_report(full_report, str(out_dir / "report.json"))
    md_path = reporter.write_markdown_report(full_report, str(out_dir / "report.md"))

    # Severity for caller
    from reporter import _severity_badge
    severity = _severity_badge(gc_data, corr).split(" ", 1)[-1].strip()

    return {
        "json_report_path": json_path,
        "md_report_path": md_path,
        "severity": severity,
        "top_recommendations": [
            {"title": r["title"], "code_pointer": r.get("code_pointer"), "fixes": r.get("fixes", [])[:2]}
            for r in full_report.get("recommendations", [])[:3]
        ],
        "gc_summary": gc_data,
        "correlation": corr,
        "suspects": mat_findings.get("suspects", []),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="JVM Memory Leak Debugger — GC log + hprof → structured report"
    )
    ap.add_argument("--hprof", required=True)
    ap.add_argument("--gc-log", required=True, dest="gc_log")
    ap.add_argument("--output-dir", default=None, dest="output_dir")
    ap.add_argument("--mat-heap-gb", type=int, default=12, dest="mat_heap_gb")
    ap.add_argument("--skip-mat", action="store_true", dest="skip_mat")
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--json", action="store_true", help="Print result JSON to stdout")
    args = ap.parse_args()

    if not Path(args.hprof).exists():
        print(f"ERROR: hprof not found: {args.hprof}", file=sys.stderr)
        return 1
    if not Path(args.gc_log).exists():
        print(f"ERROR: GC log not found: {args.gc_log}", file=sys.stderr)
        return 1

    print(f"[jvm-memory-leak-debugger] hprof:  {args.hprof}")
    print(f"[jvm-memory-leak-debugger] gc-log: {args.gc_log}")

    result = run_full_analysis(
        hprof_path=args.hprof,
        gc_log_path=args.gc_log,
        output_dir=args.output_dir,
        skip_mat=args.skip_mat,
        mat_heap_gb=args.mat_heap_gb,
    )

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

