"""
test_schema_validator.py - Contract validation tests for public JSON outputs.
"""
from pathlib import Path

import pytest

import gc_parser
import reporter
import schema_validator
import pipeline


ROOT = Path(__file__).resolve().parents[1]
GC_LOG = ROOT / "tests" / "fixtures" / "gc-16615.log"


def test_real_gc_summary_matches_schema():
    data = gc_parser.parse_and_summarize(str(GC_LOG))

    schema_validator.validate(
        data,
        schema_validator.load_schema(str(ROOT / "schemas" / "gc_analysis_result.json")),
        schema_base=ROOT / "schemas",
    )


def test_generated_report_matches_schema(tmp_path):
    gc_data = gc_parser.parse_and_summarize(str(GC_LOG))
    report = reporter.build_report(
        gc_data=gc_data,
        mat_findings={"suspects": [], "histogram": [], "suspects_zip": None},
        correlation={
            "dump_phase": "during_full_gc_storm",
            "dump_elapsed_s": 300.0,
            "dump_timestamp_source": "override",
            "dump_timestamp_warning": None,
            "oom_proximity_pct": 100.0,
            "inferred_trigger": "schema test",
            "live_set_at_dump_mb": 8190.0,
            "surrounding_events": [],
        },
        hprof_path="/tmp/dump.hprof",
        gc_log_path=str(GC_LOG),
    )
    report_path = reporter.write_json_report(report, str(tmp_path / "report.json"))

    schema_validator.validate_file(
        report_path,
        str(ROOT / "schemas" / "memory_leak_report.json"),
    )


def test_pipeline_validates_memory_report_dict():
    gc_data = gc_parser.parse_and_summarize(str(GC_LOG))
    report = reporter.build_report(
        gc_data=gc_data,
        mat_findings={"suspects": [], "histogram": [], "suspects_zip": None},
        correlation={
            "dump_phase": "during_full_gc_storm",
            "dump_elapsed_s": 300.0,
            "dump_timestamp_source": "override",
            "dump_timestamp_warning": None,
            "oom_proximity_pct": 100.0,
            "inferred_trigger": "schema test",
            "live_set_at_dump_mb": 8190.0,
            "surrounding_events": [],
        },
        hprof_path="/tmp/dump.hprof",
        gc_log_path=str(GC_LOG),
    )

    pipeline.validate_memory_report(report)


def test_report_schema_requires_dump_timestamp_provenance():
    gc_data = gc_parser.parse_and_summarize(str(GC_LOG))
    report = reporter.build_report(
        gc_data=gc_data,
        mat_findings={"suspects": [], "histogram": [], "suspects_zip": None},
        correlation={
            "dump_phase": "during_full_gc_storm",
            "dump_elapsed_s": 300.0,
            "oom_proximity_pct": 100.0,
            "inferred_trigger": "schema test",
            "surrounding_events": [],
        },
        hprof_path="/tmp/dump.hprof",
        gc_log_path=str(GC_LOG),
    )

    with pytest.raises(schema_validator.SchemaValidationError, match="dump_timestamp_source"):
        pipeline.validate_memory_report(report)


def test_report_schema_rejects_raw_mat_page_text():
    gc_data = gc_parser.parse_and_summarize(str(GC_LOG))
    report = reporter.build_report(
        gc_data=gc_data,
        mat_findings={
            "suspects": [],
            "histogram": [],
            "suspects_zip": None,
            "raw_text_by_page": {"suspect.html": "very large html text"},
        },
        correlation={
            "dump_phase": "during_full_gc_storm",
            "dump_elapsed_s": 300.0,
            "dump_timestamp_source": "override",
            "dump_timestamp_warning": None,
            "oom_proximity_pct": 100.0,
            "inferred_trigger": "schema test",
            "surrounding_events": [],
        },
        hprof_path="/tmp/dump.hprof",
        gc_log_path=str(GC_LOG),
    )
    report["heap_dump_analysis"]["raw_text_by_page"] = {"suspect.html": "very large html text"}

    with pytest.raises(schema_validator.SchemaValidationError, match="raw_text_by_page"):
        pipeline.validate_memory_report(report)


def test_custom_recommendation_example_matches_schema():
    schema_validator.validate_file(
        str(ROOT / "examples" / "custom_patterns.json"),
        str(ROOT / "schemas" / "recommendation_patterns.json"),
    )


def test_recommendation_pattern_schema_rejects_unknown_fields():
    data = {
        "patterns": [
            {
                "id": "unknown_field",
                "title": "Unknown field",
                "description": "Should fail schema validation.",
                "fixes": ["Remove the field."],
                "gc": {"min_full_gc_count": 1, "not_supported": 2},
            }
        ]
    }

    with pytest.raises(schema_validator.SchemaValidationError, match="unexpected properties"):
        schema_validator.validate(
            data,
            schema_validator.load_schema(str(ROOT / "schemas" / "recommendation_patterns.json")),
            schema_base=ROOT / "schemas",
        )


def test_recommendation_pattern_schema_rejects_negative_threshold():
    data = {
        "patterns": [
            {
                "id": "negative_threshold",
                "title": "Negative threshold",
                "description": "Should fail schema validation.",
                "fixes": ["Use a non-negative integer."],
                "gc": {"min_full_gc_count": -1},
            }
        ]
    }

    with pytest.raises(schema_validator.SchemaValidationError, match="minimum"):
        schema_validator.validate(
            data,
            schema_validator.load_schema(str(ROOT / "schemas" / "recommendation_patterns.json")),
            schema_base=ROOT / "schemas",
        )


def test_schema_validator_reports_missing_required_field():
    schema = {
        "type": "object",
        "required": ["answer"],
        "properties": {"answer": {"type": "integer"}},
    }

    with pytest.raises(schema_validator.SchemaValidationError, match="missing required"):
        schema_validator.validate({}, schema)
