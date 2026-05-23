# jvm-memory-leak-debugger skill – convenience targets

PYTHON   ?= python3
TOOLS_DIR = tools
TEST_DIR  = tests
FIXTURES  = tests/fixtures
HPROF_PATH ?=
GC_LOG_PATH ?= $(FIXTURES)/gc-16615.log
OUTPUT_DIR ?= /tmp/memleak-skill-test

.PHONY: test test-adapters test-e2e-gc test-e2e-full lint validate-manifests validate-contracts check-runtime test-mat-runtime package-smoke release-check run-example clean help

## Run all unit tests (fast, no hprof required)
test:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -m pytest $(TEST_DIR) -v -m "not e2e_full"

## Run optional HTTP/MCP adapter smoke tests (requires .[server,mcp])
test-adapters:
	PYTHONPATH=$(TOOLS_DIR):. $(PYTHON) -m pytest $(TEST_DIR)/test_server_adapter.py $(TEST_DIR)/test_mcp_adapter.py -v

## Run E2E GC-log tests against the real gc-16615.log fixture (no hprof needed)
test-e2e-gc:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -m pytest $(TEST_DIR)/test_e2e_real_gc.py -v -m e2e_gc

## Run full E2E pipeline including correlator + skip-mat (requires hprof)
## Set HPROF_PATH=/path/to/java_pid16615.hprof
test-e2e-full:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -m pytest $(TEST_DIR)/test_e2e_real_gc.py -v -m e2e_full

## Symlink HPROF_PATH into fixtures/ for local E2E (does not copy large dumps)
link-hprof:
	@if [ -z "$(HPROF_PATH)" ]; then \
	  echo "ERROR: set HPROF_PATH=/path/to/java_pidNNN.hprof"; exit 1; \
	elif [ -f "$(HPROF_PATH)" ]; then \
	  ln -sf "$(HPROF_PATH)" $(FIXTURES)/java_pid16615.hprof && echo "Linked $(HPROF_PATH) -> $(FIXTURES)/java_pid16615.hprof"; \
	else \
	  echo "ERROR: HPROF_PATH not found: $(HPROF_PATH)"; exit 1; \
	fi

## Pyflakes lint check, with stdlib py_compile fallback when pyflakes is absent
lint:
	$(PYTHON) scripts/lint_or_compile.py $(TOOLS_DIR)/gc_parser.py \
	                                    $(TOOLS_DIR)/mat_runner.py \
	                                    $(TOOLS_DIR)/correlator.py \
	                                    $(TOOLS_DIR)/reporter.py \
	                                    $(TOOLS_DIR)/schema_validator.py \
	                                    $(TOOLS_DIR)/pipeline.py \
	                                    $(TOOLS_DIR)/dispatch.py \
	                                    $(TOOLS_DIR)/debug_memory_leak.py \
	                                    $(TOOLS_DIR)/server_adapter.py \
	                                    $(TOOLS_DIR)/mcp_adapter.py \
	                                    $(TOOLS_DIR)/skill_resources.py \
	                                    server.py \
	                                    mcp_server.py

## Validate JSON manifests and schemas
validate-manifests:
	$(PYTHON) -c "import json; d=json.load(open('skill.json')); assert d['schema_version']=='1.0'; assert len(d['tools'])==4; print('skill.json OK')"
	$(PYTHON) -c "import json; json.load(open('schemas/gc_analysis_result.json')); print('gc_analysis_result.json OK')"
	$(PYTHON) -c "import json; json.load(open('schemas/memory_leak_report.json')); print('memory_leak_report.json OK')"
	$(PYTHON) -c "import json; json.load(open('schemas/recommendation_patterns.json')); print('recommendation_patterns.json OK')"
	$(PYTHON) -c "from pathlib import Path; t=Path('pyproject.toml').read_text(); assert 'jvm-memory-leak-debugger = \"debug_memory_leak:main\"' in t; assert 'jvm-memory-leak-debugger-api = \"server_adapter:main\"' in t; assert 'jvm-memory-leak-debugger-mcp = \"mcp_adapter:main\"' in t; assert 'mcp>=1.0.0; python_version >= \\'3.10\\'' in t; assert 'server = [\"fastapi>=0.111.0\", \"uvicorn[standard]>=0.29.0\"]' in t; assert 'share/jvm-memory-leak-debugger' in t and 'instructions/system_prompt.md' in t and 'schemas/memory_leak_report.json' in t; print('pyproject.toml OK')"
	$(PYTHON) -c "from pathlib import Path; t=Path('setup.py').read_text(); assert 'name=\"jvm-memory-leak-debugger\"' in t; assert 'console_scripts' in t; assert 'share/jvm-memory-leak-debugger/docs/architecture' in t; print('setup.py legacy-install shim OK')"
	$(PYTHON) -c "from pathlib import Path; files=['instructions/system_prompt.md','references/g1gc_phases.md','references/jvm_flags.md','references/mat_installation.md','references/harness_configuration.md','references/preflight_checklist.md','examples/conversation_examples.md','assets/report_template.md','assets/skill_card.md']; missing=[f for f in files if not Path(f).read_text().strip()]; assert not missing, missing; print('skill package docs OK')"
	$(PYTHON) -c "import json, pathlib; [json.load(open(p)) for p in pathlib.Path('harnesses').glob('*.json')]; print('harness examples OK')"
	@! grep -R "scripts/run_mat.sh\|scripts/parse_gc_log.py\|scripts/generate_report.py" SKILL.md README.md instructions references examples assets

## Validate real/generated JSON outputs against checked-in schemas
validate-contracts:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -m pytest $(TEST_DIR)/test_schema_validator.py -v

## Check local Java/MAT/platform readiness without downloading MAT
check-runtime:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) $(TOOLS_DIR)/debug_memory_leak.py --check-runtime --json

## Download, verify, and unpack pinned MAT for this host; no hprof required
test-mat-runtime:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -c "import mat_runner; s=mat_runner.runtime_diagnostics(); assert s['ready_for_analysis'], s; eclipse=mat_runner.ensure_mat(); s=mat_runner.runtime_diagnostics(); assert s['mat_installed'], s; assert s['equinox_launcher_found'], s; print(eclipse)"

## Verify a non-editable install can run commands and find bundled skill data
package-smoke:
	$(PYTHON) scripts/package_smoke.py

## Run local release-readiness gates that do not require MAT download or hprof
release-check: lint test validate-manifests validate-contracts test-e2e-gc package-smoke

## Quick smoke test using caller-provided artifacts (skips MAT re-run)
run-example:
	@test -n "$(HPROF_PATH)" || (echo "ERROR: set HPROF_PATH=/path/to/java_pidNNN.hprof"; exit 1)
	@test -f "$(HPROF_PATH)" || (echo "ERROR: HPROF_PATH not found: $(HPROF_PATH)"; exit 1)
	@test -n "$(GC_LOG_PATH)" || (echo "ERROR: set GC_LOG_PATH=/path/to/gc.log"; exit 1)
	@test -f "$(GC_LOG_PATH)" || (echo "ERROR: GC_LOG_PATH not found: $(GC_LOG_PATH)"; exit 1)
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) $(TOOLS_DIR)/debug_memory_leak.py \
	  --hprof   "$(HPROF_PATH)" \
	  --gc-log  "$(GC_LOG_PATH)" \
	  --skip-mat \
	  --output-dir "$(OUTPUT_DIR)"

## Start the Claude MCP server
mcp-server:
	$(PYTHON) mcp_server.py

## Start the FastAPI bridge for Copilot/Codex
api-server:
	$(PYTHON) -m uvicorn server:app --host 0.0.0.0 --port 8080

## Remove pytest/pyc artefacts
clean:
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	rm -rf .pytest_cache; \
	echo "clean"

help:
	@grep -E '^## ' Makefile | sed 's/## /  /'
