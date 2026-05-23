"""
pipeline.py
===========
Shared end-to-end memory leak analysis pipeline used by the CLI, dispatch
registry, MCP server, and HTTP bridge.
"""

from pathlib import Path
from typing import Optional

import gc_parser
import correlator
import reporter
import schema_validator
import skill_resources


def validate_memory_report(report: dict) -> None:
    """Validate a full report dict against the installed/source JSON schema."""
    schema_path = skill_resources.find_repo_file("schemas/memory_leak_report.json")
    if schema_path is None:
        raise FileNotFoundError("schemas/memory_leak_report.json not found")
    schema_validator.validate(
        report,
        schema_validator.load_schema(str(schema_path)),
        schema_base=schema_path.parent,
    )


def run_full_analysis(
    hprof_path: str,
    gc_log_path: str,
    output_dir: Optional[str] = None,
    skip_mat: bool = False,
    mat_home: Optional[str] = None,
    mat_heap_gb: int = 12,
    timeout_s: int = 7200,
    patterns_file: Optional[str] = None,
    dump_time: Optional[str] = None,
) -> dict:
    """
    Full pipeline: parse GC log -> correlate -> MAT analysis -> build reports.

    Returns:
        {
            "json_report_path": str,
            "md_report_path": str,
            "severity": str,
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

    gc_sum = gc_parser.parse_gc_log(gc_log)
    gc_data = gc_parser.gc_summary_to_dict(gc_sum)

    try:
        corr = correlator.correlate(gc_sum, gc_log, hprof, dump_time=dump_time)
    except Exception as e:
        corr = {"error": str(e), "dump_phase": "unknown"}

    mat_findings: dict = {
        "suspects": [],
        "histogram": [],
        "suspects_zip": None,
        "analysis_status": "not_run",
        "error": None,
    }
    if not skip_mat:
        try:
            from mat_runner import DEFAULT_MAT_HOME, analyse_hprof

            mat_findings = analyse_hprof(
                hprof_path=hprof,
                mat_home=Path(mat_home) if mat_home else DEFAULT_MAT_HOME,
                mat_heap_gb=mat_heap_gb,
                timeout_s=timeout_s,
            )
            mat_findings["analysis_status"] = "completed"
            mat_findings.setdefault("error", None)
        except Exception as e:
            mat_findings = {
                "suspects": [],
                "histogram": [],
                "suspects_zip": None,
                "analysis_status": "failed",
                "error": str(e),
            }
    else:
        from mat_runner import _parse_leak_suspects

        zip_path = Path(hprof).parent / (Path(hprof).stem + "_Leak_Suspects.zip")
        if zip_path.exists():
            try:
                mat_findings = _parse_leak_suspects(zip_path)
                mat_findings["suspects_zip"] = str(zip_path)
                mat_findings["analysis_status"] = "parsed_existing"
                mat_findings.setdefault("error", None)
            except Exception as e:
                mat_findings = {
                    "suspects": [],
                    "histogram": [],
                    "suspects_zip": str(zip_path),
                    "analysis_status": "failed",
                    "error": str(e),
                }
        else:
            mat_findings["analysis_status"] = "skipped"
            mat_findings["error"] = (
                "MAT analysis skipped and no existing *_Leak_Suspects.zip "
                f"was found beside {hprof}."
            )

    full_report = reporter.build_report(
        gc_data=gc_data,
        mat_findings=mat_findings,
        correlation=corr,
        hprof_path=hprof,
        gc_log_path=gc_log,
        patterns_file=patterns_file,
    )

    validate_memory_report(full_report)
    json_path = reporter.write_json_report(full_report, str(out_dir / "report.json"))
    md_path = reporter.write_markdown_report(full_report, str(out_dir / "report.md"))

    severity = full_report["severity"].split(" ", 1)[-1].strip()

    return {
        "json_report_path": json_path,
        "md_report_path": md_path,
        "severity": severity,
        "top_recommendations": [
            {
                "title": r["title"],
                "code_pointer": r.get("code_pointer"),
                "fixes": r.get("fixes", [])[:2],
            }
            for r in full_report.get("recommendations", [])[:3]
        ],
        "gc_summary": gc_data,
        "correlation": corr,
        "suspects": mat_findings.get("suspects", []),
    }
