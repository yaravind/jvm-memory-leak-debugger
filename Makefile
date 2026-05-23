# jvm-memory-leak-debugger skill – convenience targets

PYTHON   ?= python3
TOOLS_DIR = tools
TEST_DIR  = tests
FIXTURES  = tests/fixtures

.PHONY: test test-e2e-gc test-e2e-full lint validate-manifests run-example clean help

## Run all unit tests (fast, no hprof required)
test:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -m pytest $(TEST_DIR) -v -m "not e2e_full"

## Run E2E GC-log tests against the real gc-16615.log fixture (no hprof needed)
test-e2e-gc:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -m pytest $(TEST_DIR)/test_e2e_real_gc.py -v -m e2e_gc

## Run full E2E pipeline including correlator + skip-mat (requires hprof)
## Symlink first: ln -s $$PWD/../../target/jvm-logs/java_pid16615.hprof $(FIXTURES)/java_pid16615.hprof
## Or set HPROF_PATH=/path/to/java_pid16615.hprof
test-e2e-full:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) -m pytest $(TEST_DIR)/test_e2e_real_gc.py -v -m e2e_full

## Symlink the hprof from target/jvm-logs into fixtures/ for local E2E (does not copy the 13 GB file)
link-hprof:
	@HPROF="../../target/jvm-logs/java_pid16615.hprof"; \
	if [ -f "$$HPROF" ]; then \
	  ln -sf "$$HPROF" $(FIXTURES)/java_pid16615.hprof && echo "Linked $$HPROF → $(FIXTURES)/java_pid16615.hprof"; \
	else \
	  echo "ERROR: $$HPROF not found. Run the DataDiff app first to generate the heap dump."; exit 1; \
	fi

## Pyflakes lint check
lint:
	$(PYTHON) -m pyflakes $(TOOLS_DIR)/gc_parser.py \
	                      $(TOOLS_DIR)/mat_runner.py \
	                      $(TOOLS_DIR)/correlator.py \
	                      $(TOOLS_DIR)/reporter.py \
	                      $(TOOLS_DIR)/debug_memory_leak.py

## Validate JSON manifests and schemas
validate-manifests:
	$(PYTHON) -c "import json; d=json.load(open('skill.json')); assert d['schema_version']=='1.0'; assert len(d['tools'])==4; print('skill.json OK')"
	$(PYTHON) -c "import json; json.load(open('schemas/gc_analysis_result.json')); print('gc_analysis_result.json OK')"
	$(PYTHON) -c "import json; json.load(open('schemas/memory_leak_report.json')); print('memory_leak_report.json OK')"

## Quick smoke test using the real session artifacts (skips MAT re-run)
run-example:
	PYTHONPATH=$(TOOLS_DIR) $(PYTHON) $(TOOLS_DIR)/debug_memory_leak.py \
	  --hprof   ../../target/jvm-logs/java_pid16615.hprof \
	  --gc-log  ../../target/jvm-logs/gc-16615.log \
	  --skip-mat \
	  --output-dir /tmp/memleak-skill-test

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

