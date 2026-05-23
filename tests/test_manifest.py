"""
test_manifest.py - Public skill and harness contract checks.
"""
import importlib
import json
from pathlib import Path

import dispatch
import skill_resources


ROOT = Path(__file__).resolve().parents[1]


def _skill_manifest():
    return json.load(open(ROOT / "skill.json"))


def _pyproject_text():
    return (ROOT / "pyproject.toml").read_text()


def test_skill_manifest_tools_match_dispatch_registry():
    manifest_tools = {tool["name"] for tool in _skill_manifest()["tools"]}
    assert manifest_tools == set(dispatch.TOOLS)


def test_skill_manifest_declared_functions_are_importable():
    for tool in _skill_manifest()["tools"]:
        module_path = Path(tool["module"])
        assert (ROOT / module_path).exists()

        module = importlib.import_module(module_path.stem)
        handler = getattr(module, tool["function"])
        assert callable(handler)


def test_generate_report_manifest_exposes_mat_timeout():
    tool = next(t for t in _skill_manifest()["tools"] if t["name"] == "generate_report")
    props = tool["parameters"]["properties"]

    assert props["timeout_s"]["default"] == 7200


def test_manifest_exposes_shared_runtime_parameters():
    tools = {tool["name"]: tool for tool in _skill_manifest()["tools"]}

    extract_props = tools["extract_heap_suspects"]["parameters"]["properties"]
    assert extract_props["mat_home"]["default"] is None
    assert extract_props["mat_heap_gb"]["default"] == 12
    assert extract_props["timeout_s"]["default"] == 7200

    correlate_props = tools["correlate_dump_to_gc"]["parameters"]["properties"]
    assert correlate_props["dump_time"]["default"] is None

    report_props = tools["generate_report"]["parameters"]["properties"]
    assert report_props["mat_home"]["default"] is None
    assert report_props["mat_heap_gb"]["default"] == 12
    assert report_props["timeout_s"]["default"] == 7200
    assert report_props["patterns_file"]["default"] is None
    assert report_props["dump_time"]["default"] is None


def test_cli_and_mcp_wrappers_expose_shared_runtime_parameters():
    cli_text = (ROOT / "tools" / "debug_memory_leak.py").read_text()
    mcp_text = (ROOT / "tools" / "mcp_adapter.py").read_text()

    assert "--check-runtime" in cli_text
    assert "curl_available" in cli_text
    assert "--mat-home" in cli_text
    assert "mat_home: str = None" in mcp_text


def test_harness_examples_reference_public_tools():
    manifest_tools = {tool["name"] for tool in _skill_manifest()["tools"]}
    direct = json.load(open(ROOT / "harnesses" / "direct_function_dispatch.example.json"))
    installed = json.load(open(ROOT / "harnesses" / "installed_commands.example.json"))
    codex = json.load(open(ROOT / "harnesses" / "codex_skill.example.json"))
    copilot = json.load(open(ROOT / "harnesses" / "copilot_extension.example.json"))

    assert set(direct["tools"]) == manifest_tools
    assert direct["dispatcher"] == {"module": "dispatch", "function": "dispatch_tool"}
    assert codex["host"] == "openai-codex"
    assert codex["transport"] == "direct_function_dispatch"
    assert set(codex["tools"]) == manifest_tools
    assert codex["dispatcher"] == {"module": "dispatch", "function": "dispatch_tool"}
    assert copilot["host"] == "github-copilot-extension"
    assert copilot["transport"] == "http"
    assert set(copilot["tools"]) == manifest_tools
    assert copilot["tool_catalog_url"].endswith("/tools")
    assert installed["commands"]["cli"] == "jvm-memory-leak-debugger"
    assert installed["commands"]["http"] == "jvm-memory-leak-debugger-api"
    assert installed["commands"]["mcp"] == "jvm-memory-leak-debugger-mcp"
    assert installed["http"]["tool_catalog_url"].endswith("/tools")


def test_manual_mat_runtime_workflow_stays_release_smoke_only():
    workflow = (ROOT / ".github" / "workflows" / "mat-runtime-smoke.yml").read_text()

    assert "workflow_dispatch:" in workflow
    assert "ubuntu-latest" in workflow
    assert "macos-latest" in workflow
    assert "windows-latest" in workflow
    assert "actions/setup-java@v4" in workflow
    assert 'java-version: "17"' in workflow
    assert "mat_runner.runtime_diagnostics()" in workflow
    assert "mat_runner.ensure_mat()" in workflow
    assert "curl_available" in workflow
    assert "--no-deps" in workflow
    assert "HPROF_PATH" not in workflow
    assert "test-e2e-full" not in workflow


def test_pyproject_exposes_console_script_and_optional_adapters():
    text = _pyproject_text()

    assert 'jvm-memory-leak-debugger = "debug_memory_leak:main"' in text
    assert 'jvm-memory-leak-debugger-api = "server_adapter:main"' in text
    assert 'jvm-memory-leak-debugger-mcp = "mcp_adapter:main"' in text
    assert 'mcp = ["mcp>=1.0.0; python_version >= \'3.10\'"]' in text
    assert 'server = ["fastapi>=0.111.0", "uvicorn[standard]>=0.29.0"]' in text
    for module_name in dispatch.TOOLS:
        if module_name == "extract_heap_suspects":
            assert '"mat_runner"' in text
        elif module_name == "generate_report":
            assert '"debug_memory_leak"' in text and '"pipeline"' in text
        elif module_name == "correlate_dump_to_gc":
            assert '"correlator"' in text
        elif module_name == "analyze_gc_log":
            assert '"gc_parser"' in text
    assert '"server_adapter"' in text
    assert '"mcp_adapter"' in text
    assert '"skill_resources"' in text
    assert '"share/jvm-memory-leak-debugger" = [' in text
    assert '"share/jvm-memory-leak-debugger/docs/architecture" = [' in text
    for bundle_file in (
        "skill.json",
        "instructions/system_prompt.md",
        "references/preflight_checklist.md",
        "schemas/memory_leak_report.json",
        "harnesses/direct_function_dispatch.example.json",
        "harnesses/installed_commands.example.json",
        "harnesses/codex_skill.example.json",
        "harnesses/copilot_extension.example.json",
        "docs/architecture/RELEASE_EVIDENCE.md",
        "docs/architecture/RELEASE_READINESS_CHECKLIST.md",
        "docs/architecture/MATURITY_COMPLETION_AUDIT.md",
        "docs/architecture/ISSUE_RESOLUTION_MATRIX.md",
        "docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md",
    ):
        assert bundle_file in text


def test_make_lint_has_dependency_free_fallback():
    makefile = (ROOT / "Makefile").read_text()
    script = (ROOT / "scripts" / "lint_or_compile.py").read_text()
    readme = (ROOT / "README.md").read_text()

    assert "scripts/lint_or_compile.py" in makefile
    assert "release-check: lint test validate-manifests validate-contracts test-e2e-gc package-smoke" in makefile
    assert "py_compile fallback" in script
    assert "make lint" in readme
    assert "py_compile" in readme


def test_readme_points_to_actions_evidence_runbook():
    readme = (ROOT / "README.md").read_text()

    assert "docs/architecture/RELEASE_EVIDENCE.md" in readme
    assert "docs/architecture/RELEASE_READINESS_CHECKLIST.md" in readme
    assert 'gh workflow run "MAT Runtime Smoke"' in readme
    assert "gh workflow run mat-runtime-smoke.yml" not in readme
    assert "--ref codex/maturity-roadmap" in readme


def test_release_readiness_checklist_tracks_required_evidence():
    readme = (ROOT / "README.md").read_text()
    text = (ROOT / "docs" / "architecture" / "RELEASE_READINESS_CHECKLIST.md").read_text()
    evidence = (ROOT / "docs" / "architecture" / "RELEASE_EVIDENCE.md").read_text()
    audit = (ROOT / "docs" / "architecture" / "MATURITY_COMPLETION_AUDIT.md").read_text()
    issue_matrix = (ROOT / "docs" / "architecture" / "ISSUE_RESOLUTION_MATRIX.md").read_text()

    for required in (
        "make validate-contracts",
        "make test-e2e-gc",
        "make package-smoke",
        "make release-check",
        "make lint",
        "py_compile",
        "make test-adapters",
        "make test-mat-runtime",
        "Test JVM Memory Leak Debugger Skill",
        "MAT Runtime Smoke",
        "PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters",
        "passed 8 tests",
        "gh workflow run \"MAT Runtime Smoke\"",
        "gh run watch <run-id>",
        "gh run view <run-id> --log-failed",
        "--json databaseId,status,conclusion,url",
        "gh run view <run-id> --repo yaravind/jvm-memory-leak-debugger --json url",
        "Do not claim Windows MAT readiness from source-only tests",
        "still capture CI adapter-smoke via the main workflow",
        "MATURITY_COMPLETION_AUDIT.md",
    ):
        assert required in text

    for required in (
        "make release-check",
        "make lint",
        "py_compile fallback",
        "Test JVM Memory Leak Debugger Skill",
        "MAT Runtime Smoke",
        "PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters",
        "2 MCP wrapper tests",
        "gh workflow run \"MAT Runtime Smoke\"",
        "gh run watch",
        "gh run view --log-failed",
        "gh run view <run-id> --json url",
        "Do not claim Windows MAT readiness from source-only tests",
        "Do not claim hosted MCP runtime readiness until the Python 3.11",
        "ADR 0004 for full heap replay evidence policy",
        "Full heap replay policy",
        "MATURITY_COMPLETION_AUDIT.md",
        "ISSUE_RESOLUTION_MATRIX.md",
    ):
        assert required in evidence

    for required in (
        "Requirement Matrix",
        "Work with MCP hosts such as Claude",
        "Work without MCP",
        "Configure with Codex, Claude, GitHub Copilot, and other harnesses",
        "Requires live GitHub Actions run URLs",
        "Successful `Test JVM Memory Leak Debugger Skill` GitHub Actions run URL",
        "Successful `MAT Runtime Smoke` GitHub Actions run URL",
        "Local\n`make release-check` is necessary but not sufficient",
    ):
        assert required in audit

    for required in (
        "Issue Resolution Matrix",
        "#1 `mat_runner.py` is macOS-only",
        "#2 Add requirements/dependency manifest",
        "#3 Hardcoded project-specific recommendation patterns",
        "#8 Tool wiring duplicated across deployment surfaces",
        "#14 Hardcoded Makefile paths",
        "Hosted Python 3.11 `adapter-smoke` job URL",
        "Test JVM Memory Leak Debugger Skill",
        "MAT Runtime Smoke",
    ):
        assert required in issue_matrix

    assert "docs/architecture/RELEASE_EVIDENCE.md" in readme


def test_full_heap_replay_policy_is_external_release_evidence():
    prd = (ROOT / "docs" / "architecture" / "JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md").read_text()
    checklist = (ROOT / "docs" / "architecture" / "RELEASE_READINESS_CHECKLIST.md").read_text()
    adr = (ROOT / "docs" / "adr" / "0004-keep-full-heap-replay-as-external-release-evidence.md").read_text()
    pyproject = _pyproject_text()
    setup_py = (ROOT / "setup.py").read_text()
    package_smoke = (ROOT / "scripts" / "package_smoke.py").read_text()

    assert "Full heap replay |" not in (ROOT / "docs" / "architecture" / "RELEASE_EVIDENCE.md").read_text()
    assert "Status\n\nAccepted" in adr
    assert "Do not require a committed or default-CI `.hprof` artifact" in adr
    assert "HPROF_PATH=/path/to/java_pidNNN.hprof make test-e2e-full" in adr
    assert "ADR 0004 keeps this as external release evidence" in checklist
    assert "0004-keep-full-heap-replay-as-external-release-evidence.md" in prd
    assert "not require a committed or default-CI `.hprof` artifact" in prd
    assert "0004-keep-full-heap-replay-as-external-release-evidence.md" in pyproject
    assert "0004-keep-full-heap-replay-as-external-release-evidence.md" in setup_py
    assert "0004-keep-full-heap-replay-as-external-release-evidence.md" in package_smoke


def test_prd_records_resolved_windows_mat_decision():
    text = (ROOT / "docs" / "architecture" / "JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md").read_text()

    assert "Whether Windows MAT support should run native MAT" not in text
    assert "Resolved Decisions" in text
    assert "0001-use-pinned-cross-platform-mat-zip-distributions.md" in text
    assert "native Windows x86_64 Eclipse MAT ZIP" in text


def test_prd_records_resolved_recommendation_pattern_language():
    text = (ROOT / "docs" / "architecture" / "JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md").read_text()
    adr = (ROOT / "docs" / "adr" / "0003-use-schema-backed-custom-recommendation-patterns.md").read_text()
    pyproject = _pyproject_text()
    setup_py = (ROOT / "setup.py").read_text()

    assert "Whether custom recommendation patterns should support regex-only matching" not in text
    assert "None currently recorded" in text
    assert "0003-use-schema-backed-custom-recommendation-patterns.md" in text
    assert "regex evidence matchers plus structured GC threshold matchers" in text
    assert "schemas/recommendation_patterns.json" in adr
    assert "match_class" in adr
    assert "min_full_gc_count" in adr
    assert "0003-use-schema-backed-custom-recommendation-patterns.md" in pyproject
    assert "0003-use-schema-backed-custom-recommendation-patterns.md" in setup_py


def test_prd_marks_locally_completed_maturity_slices_without_overclaiming_ci():
    text = (ROOT / "docs" / "architecture" / "JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md").read_text()

    assert "### M6: Contributor Cleanup\n\nRemove local-machine assumptions" in text
    assert "Status: implemented locally on `codex/maturity-roadmap`. Severity is public" in text
    assert "Manifest regression guards keep those cleanup decisions in" in text
    assert "Status: implemented locally on `codex/maturity-roadmap` for non-empty" in text
    assert "HTTP `/tools`\ncatalog discovery" in text
    assert "Status: implemented locally on `codex/maturity-roadmap` with\n`pyproject.toml`" in text
    assert "package smoke evidence from a non-editable install outside the source\ncheckout" in text
    assert "M9: Cross-Platform CI Evidence" in text
    assert "Status: partially implemented on `codex/maturity-roadmap` with a GitHub Actions\ncross-platform smoke matrix" in text
    assert "M10: Optional Adapter Runtime Evidence" in text
    assert "Status: implemented locally on `codex/maturity-roadmap` with optional FastAPI\nand MCP smoke tests" in text
    assert "PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters" in text
    assert "passed all 8 adapter tests" in text
    assert "Hosted MCP runtime proof still needs the Python 3.11 `adapter-smoke`\njob URL" in text


def test_contributor_cleanup_regression_guards():
    makefile = (ROOT / "Makefile").read_text()
    debug_cli = (ROOT / "tools" / "debug_memory_leak.py").read_text()
    gc_parser = (ROOT / "tools" / "gc_parser.py").read_text()
    reporter = (ROOT / "tools" / "reporter.py").read_text()
    pytest_ini = (ROOT / "pytest.ini").read_text()
    public_docs = "\n".join(
        path.read_text()
        for path in [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "instructions" / "system_prompt.md",
            *sorted((ROOT / "references").glob("*.md")),
            *sorted((ROOT / "examples").glob("*.md")),
            *sorted((ROOT / "assets").glob("*.md")),
        ]
    )

    assert "../../target" not in makefile
    assert "HPROF_PATH ?=" in makefile
    assert "GC_LOG_PATH ?=" in makefile
    assert "OUTPUT_DIR ?=" in makefile
    assert not (ROOT / "conftest.py").exists()
    assert not (ROOT / "tests" / "conftest.py").exists()
    assert "pythonpath = tools" in pytest_ini
    assert "→" not in debug_cli
    assert "_RE_PAUSE_FULL_SUMMARY" not in gc_parser
    assert reporter.count('encoding="utf-8"') >= 2
    for deleted_entry_point in (
        "scripts/run_mat.sh",
        "scripts/parse_gc_log.py",
        "scripts/generate_report.py",
    ):
        assert deleted_entry_point not in public_docs


def test_setup_py_keeps_legacy_editable_installs_working():
    text = (ROOT / "setup.py").read_text()

    assert "from setuptools import setup" in text
    assert 'name="jvm-memory-leak-debugger"' in text
    assert '"console_scripts"' in text
    assert '"share/jvm-memory-leak-debugger/docs/architecture"' in text


def test_package_smoke_checks_installed_commands_and_bundle():
    text = (ROOT / "scripts" / "package_smoke.py").read_text()
    workflow = (ROOT / ".github" / "workflows" / "test-skill.yml").read_text()

    for expected in (
        "jvm-memory-leak-debugger",
        "jvm-memory-leak-debugger-api",
        "jvm-memory-leak-debugger-mcp",
        "references/fix_patterns.md",
        "references/preflight_checklist.md",
        "examples/custom_patterns.json",
        "schemas/recommendation_patterns.json",
        "harnesses/installed_commands.example.json",
        "harnesses/codex_skill.example.json",
        "harnesses/copilot_extension.example.json",
        "docs/adr/0003-use-schema-backed-custom-recommendation-patterns.md",
        "docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md",
        "docs/architecture/ISSUE_RESOLUTION_MATRIX.md",
        "docs/architecture/MATURITY_COMPLETION_AUDIT.md",
        "docs/architecture/RELEASE_EVIDENCE.md",
        "docs/architecture/RELEASE_READINESS_CHECKLIST.md",
    ):
        assert expected in text
        assert expected in workflow


def test_skill_resources_can_find_source_bundle_files():
    manifest = skill_resources.find_repo_file("skill.json")
    instructions = skill_resources.find_repo_file("instructions/system_prompt.md")

    assert manifest is not None
    assert instructions is not None
    assert skill_resources.load_json("skill.json", {})["id"] == "jvm-memory-leak-debugger"
