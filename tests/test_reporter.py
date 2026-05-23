"""
test_reporter.py — Unit tests for the reporter and pattern matching
"""
import sys
import os
import json
import tempfile

import reporter


MOCK_GC_DATA = {
    "config": {"collector": "G1", "max_heap_mb": 8192, "region_size_mb": 2, "compressed_oops": True},
    "runtime_s": 435.6,
    "young_gc": {"count": 471, "min": 0.5, "max": 315.3, "avg": 10.9, "p95": 30.0, "total": 5134.0},
    "full_gc": {"count": 33, "min": 853.0, "max": 1016.4, "avg": 867.7, "p95": 940.0, "total": 28634.0},
    "full_gc_count": 33,
    "to_space_exhausted_count": 31,
    "concurrent_abort_count": 16,
    "live_set_drift_mb": -70.0,
    "full_gc_timeline": [
        {"gc_id": 286, "elapsed_s": 300.733, "before_mb": 8192, "after_mb": 7580, "heap_mb": 8192, "pause_ms": 853.231},
        {"gc_id": 365, "elapsed_s": 374.992, "before_mb": 8190, "after_mb": 22, "heap_mb": 114, "pause_ms": 130.738},
    ],
    "final_metaspace_used_kb": 46517,
    "heap_exit_used_mb": 22.0,
    "heap_exit_total_mb": 114.0,
}

MOCK_MAT_FINDINGS = {
    "suspects": [
        {
            "suspect_number": 1,
            "description": "The thread main keeps local variables with total size 8,565,398,576 (99.78%) bytes.",
            "accumulation_point": "JdbcDatasetReader$.readResultSet",
            "retained_bytes": 8565398576,
            "retained_pct": 99.78,
            "stack_frames": [
                "at com.tccc.dna.diff.engine.local.JdbcDatasetReader$.readResultSet(JdbcDatasetReader.scala:99)",
                "at com.tccc.dna.diff.DataDiffApp$.run(DataDiffApp.scala:55)",
            ],
            "dominator_path": ["scala.collection.immutable.VectorBuilder @ 0x644816c30"],
            "object_graph_classes": [
                "scala.collection.immutable.HashMap$HashMap1  44040192  1409286144",
                "scala.Tuple2  44040192  1056964608",
            ],
        }
    ],
    "histogram": [
        {"class": "scala.collection.immutable.HashMap$HashMap1", "objects": 59758552, "shallow_bytes": 1912273664, "retained_bytes": 7391013656},
        {"class": "java.lang.String", "objects": 58801906, "shallow_bytes": 1411245744, "retained_bytes": 3106854904},
    ],
    "suspects_zip": "/path/to/java_pid16615_Leak_Suspects.zip",
}

MOCK_CORRELATION = {
    "dump_wall_time": "2026-05-22T16:18:36",
    "dump_elapsed_s": 374.9,
    "jvm_start_wall_time": "2026-05-22T16:12:21",
    "dump_phase": "during_full_gc_storm",
    "inferred_trigger": "Heap dump captured during Full GC storm. 31 to-space exhausted events. OOM proximity 100%.",
    "oom_proximity_pct": 100.0,
    "live_set_at_dump_mb": 8190.0,
    "full_gc_density_per_min_near_dump": 16.5,
    "full_gc_count_near_dump": 33,
    "to_space_exhausted_count": 31,
    "surrounding_events": [],
}


def test_build_report_structure():
    report = reporter.build_report(
        gc_data=MOCK_GC_DATA,
        mat_findings=MOCK_MAT_FINDINGS,
        correlation=MOCK_CORRELATION,
        hprof_path="/path/to/dump.hprof",
        gc_log_path="/path/to/gc.log",
    )
    assert report["schema_version"] == "1.0"
    assert "CRITICAL" in report["severity"]
    assert report["gc_analysis"]["full_gc_count"] == 33
    assert report["heap_dump_analysis"]["analysis_status"] == "unknown"
    assert report["heap_dump_analysis"]["error"] is None
    assert len(report["heap_dump_analysis"]["suspects"]) == 1
    assert report["correlation"]["dump_phase"] == "during_full_gc_storm"
    assert len(report["recommendations"]) > 0


def test_to_space_pattern_matched():
    report = reporter.build_report(
        gc_data=MOCK_GC_DATA,
        mat_findings=MOCK_MAT_FINDINGS,
        correlation=MOCK_CORRELATION,
        hprof_path="/p",
        gc_log_path="/p",
    )
    ids = [r["id"] for r in report["recommendations"]]
    assert "to_space_exhausted" in ids


def test_builtin_patterns_are_generic():
    report = reporter.build_report(
        gc_data=MOCK_GC_DATA,
        mat_findings=MOCK_MAT_FINDINGS,
        correlation=MOCK_CORRELATION,
        hprof_path="/p",
        gc_log_path="/p",
    )
    ids = [r["id"] for r in report["recommendations"]]
    assert "large_thread_local_retention" in ids
    assert "collection_builder_retention" in ids
    assert "map_entry_overhead" in ids
    assert "unbounded_jdbc_read" not in ids
    assert all(r.get("code_pointer") is None for r in report["recommendations"])
    assert all(r.get("pattern_source") == "builtin" for r in report["recommendations"])


def test_custom_pattern_file_matched():
    custom = {
        "patterns": [
            {
                "id": "unbounded_jdbc_read",
                "match_class": "JdbcDatasetReader|readResultSet",
                "match_stack": "readResultSet|JdbcDatasetReader",
                "title": "Custom JDBC reader materialises the result set",
                "description": "Project-specific guidance from a custom pattern file.",
                "fixes": ["Add a row cap in the project JDBC reader."],
                "code_pointer": "src/main/scala/example/JdbcDatasetReader.scala:97",
            }
        ]
    }

    with tempfile.TemporaryDirectory() as td:
        patterns_path = f"{td}/patterns.json"
        with open(patterns_path, "w") as f:
            json.dump(custom, f)

        report = reporter.build_report(
            gc_data=MOCK_GC_DATA,
            mat_findings=MOCK_MAT_FINDINGS,
            correlation=MOCK_CORRELATION,
            hprof_path="/p",
            gc_log_path="/p",
            patterns_file=patterns_path,
        )

    rec = next(r for r in report["recommendations"] if r["id"] == "unbounded_jdbc_read")
    assert rec["code_pointer"] == "src/main/scala/example/JdbcDatasetReader.scala:97"
    assert rec["pattern_source"].endswith("patterns.json")


def test_patterns_file_env_var(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        patterns_path = f"{td}/patterns.json"
        with open(patterns_path, "w") as f:
            json.dump(
                [
                    {
                        "id": "custom_gc_pressure",
                        "title": "Custom GC pressure rule",
                        "description": "Matched from PATTERNS_FILE.",
                        "fixes": ["Tune the workload."],
                        "gc": {"min_full_gc_count": 1},
                    }
                ],
                f,
            )
        monkeypatch.setenv("PATTERNS_FILE", patterns_path)

        patterns = reporter.load_patterns()

    assert any(p["id"] == "custom_gc_pressure" for p in patterns)


def test_custom_pattern_file_rejects_invalid_regex():
    custom = {
        "patterns": [
            {
                "id": "broken_regex",
                "match_class": "[unterminated",
                "title": "Broken regex",
                "description": "Should fail at load time.",
                "fixes": ["Fix the regex."],
            }
        ]
    }

    with tempfile.TemporaryDirectory() as td:
        patterns_path = f"{td}/patterns.json"
        with open(patterns_path, "w") as f:
            json.dump(custom, f)

        try:
            reporter.load_patterns(patterns_path)
        except ValueError as e:
            assert "match_class is not a valid regex" in str(e)
        else:
            raise AssertionError("invalid regex was accepted")


def test_custom_pattern_file_rejects_matcherless_pattern():
    custom = {
        "patterns": [
            {
                "id": "matches_everything",
                "title": "Too broad",
                "description": "A matcherless custom pattern would match every report.",
                "fixes": ["Add a matcher."],
            }
        ]
    }

    with tempfile.TemporaryDirectory() as td:
        patterns_path = f"{td}/patterns.json"
        with open(patterns_path, "w") as f:
            json.dump(custom, f)

        try:
            reporter.load_patterns(patterns_path)
        except ValueError as e:
            assert "must define at least one matcher" in str(e)
        else:
            raise AssertionError("matcherless pattern was accepted")


def test_custom_pattern_file_rejects_bad_gc_condition():
    custom = {
        "patterns": [
            {
                "id": "bad_gc",
                "title": "Bad GC",
                "description": "Invalid GC threshold.",
                "fixes": ["Use a non-negative integer."],
                "gc": {"min_full_gc_count": -1},
            }
        ]
    }

    with tempfile.TemporaryDirectory() as td:
        patterns_path = f"{td}/patterns.json"
        with open(patterns_path, "w") as f:
            json.dump(custom, f)

        try:
            reporter.load_patterns(patterns_path)
        except ValueError as e:
            assert "gc.min_full_gc_count must be a non-negative integer" in str(e)
        else:
            raise AssertionError("bad GC condition was accepted")


def test_custom_pattern_file_rejects_duplicate_builtin_id():
    custom = {
        "patterns": [
            {
                "id": "to_space_exhausted",
                "title": "Duplicate built-in",
                "description": "Duplicates should be explicit, not silently ignored.",
                "fixes": ["Use a unique id."],
                "gc": {"min_full_gc_count": 1},
            }
        ]
    }

    with tempfile.TemporaryDirectory() as td:
        patterns_path = f"{td}/patterns.json"
        with open(patterns_path, "w") as f:
            json.dump(custom, f)

        try:
            reporter.load_patterns(patterns_path)
        except ValueError as e:
            assert "duplicate pattern id: to_space_exhausted" in str(e)
        else:
            raise AssertionError("duplicate pattern id was accepted")


def test_severity_critical():
    badge = reporter.severity_badge(MOCK_GC_DATA, MOCK_CORRELATION)
    assert "CRITICAL" in badge


def test_write_json_report():
    report = reporter.build_report(MOCK_GC_DATA, MOCK_MAT_FINDINGS, MOCK_CORRELATION, "/p", "/p")
    with tempfile.TemporaryDirectory() as td:
        path = reporter.write_json_report(report, f"{td}/report.json")
        with open(path) as f:
            loaded = json.load(f)
        assert loaded["schema_version"] == "1.0"
        assert "CRITICAL" in loaded["severity"]
        assert loaded["gc_analysis"]["to_space_exhausted_count"] == 31


def test_write_markdown_report():
    report = reporter.build_report(MOCK_GC_DATA, MOCK_MAT_FINDINGS, MOCK_CORRELATION, "/p", "/p")
    with tempfile.TemporaryDirectory() as td:
        path = reporter.write_markdown_report(report, f"{td}/report.md")
        content = open(path).read()
        assert "# JVM Memory Leak Debug Report" in content
        assert "CRITICAL" in content
        assert "Full GC Storm Timeline" in content
        assert "MAT analysis status" in content
        assert "Recommendations" in content


def test_report_surfaces_heap_analysis_error_in_json_and_markdown():
    findings = {
        "suspects": [],
        "histogram": [],
        "suspects_zip": None,
        "analysis_status": "failed",
        "error": "Java 17+ is required to run Eclipse MAT.",
    }

    report = reporter.build_report(MOCK_GC_DATA, findings, MOCK_CORRELATION, "/p", "/p")

    assert report["heap_dump_analysis"]["analysis_status"] == "failed"
    assert "Java 17" in report["heap_dump_analysis"]["error"]

    with tempfile.TemporaryDirectory() as td:
        path = reporter.write_markdown_report(report, f"{td}/report.md")
        content = open(path).read()

    assert "Heap evidence gap" in content
    assert "Java 17+ is required" in content
