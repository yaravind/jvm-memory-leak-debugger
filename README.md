# jvm-memory-leak-debugger

> **Agent skill** — Diagnoses JVM out-of-memory failures from a `.hprof` heap dump and G1 GC log.
> Identifies the dominant object graph, classifies the GC failure phase, and produces ranked fix recommendations.
> Deployable to GitHub Copilot Extensions, OpenAI Codex agents, Claude MCP servers, and as a standalone CLI.

---

## What It Does

Given a JVM heap dump and GC log the skill:

1. Parses the GC log — Full GC timeline, pause stats, To-space exhaustion count, live-set drift
2. Correlates the dump timestamp — dump phase classification (during storm / post-OOM / normal)
3. Runs Eclipse MAT headlessly — leak suspects, dominator tree, class histogram
4. Matches known patterns — code-pointer-linked fix recommendations
5. Writes `report.json` (machine-readable) + `report.md` (human-readable)

---

## Skill Structure

```
jvm-memory-leak-debugger/
├── skill.json                       # Skill manifest (4 tool definitions + metadata)
├── instructions/
│   └── system_prompt.md             # Agent system prompt
├── tools/
│   ├── debug_memory_leak.py         # Entry point / generate_report tool
│   ├── gc_parser.py                 # analyze_gc_log tool
│   ├── mat_runner.py                # extract_heap_suspects tool (Eclipse MAT)
│   ├── correlator.py                # correlate_dump_to_gc tool
│   └── reporter.py                  # Report builder + fix-pattern library
├── tests/
│   ├── test_gc_parser.py
│   └── test_reporter.py
├── schemas/
│   ├── gc_analysis_result.json      # JSON Schema for analyze_gc_log output
│   └── memory_leak_report.json      # JSON Schema for generate_report output
├── examples/
│   └── conversation_examples.md     # Sample user-agent conversations
├── mcp_server.py                    # Claude MCP server
├── server.py                        # FastAPI bridge (Copilot / Codex)
├── scripts/
│   ├── lint_or_compile.py            # pyflakes when available; py_compile fallback
│   └── validate_artifacts.sh         # optional local artifact sanity check
├── Makefile                         # make test | make lint | make run-example
├── pytest.ini
└── .github/workflows/
    ├── test-skill.yml               # CI: fast tests, package smoke, adapters
    └── mat-runtime-smoke.yml        # Manual release smoke for MAT downloads
```

---

## Requirements

| Requirement | Details |
|-------------|---------|
| Python 3.9+ | stdlib only — no pip install needed for core tools |
| Java 17+ | Required by Eclipse MAT 1.16. Set `JAVA17_HOME`/`JAVA_HOME` or put Java 17+ on `PATH` |
| curl | Auto-download Eclipse MAT on first use |
| Internet (first run) | Downloads the pinned Eclipse MAT ZIP for Linux, macOS, or Windows from download.eclipse.org |

---

## Build & Test

No build step — Python stdlib only.

```bash
cd /path/to/jvm-memory-leak-debugger

# Run unit tests
make test
# or: PYTHONPATH=tools python3 -m pytest tests/ -v

# Validate skill.json + JSON schemas
make validate-manifests

# Validate real/generated JSON outputs against checked-in schemas
make validate-contracts

# Optional lint check; falls back to stdlib py_compile when pyflakes is absent
make lint

# Check local platform/Java/MAT readiness without downloading MAT
make check-runtime

# Smoke test against local artifacts (skip MAT re-run)
make run-example HPROF_PATH=/path/to/java_pidNNN.hprof GC_LOG_PATH=/path/to/gc.log

# Optional live MAT runtime smoke; downloads and verifies the pinned MAT ZIP
make test-mat-runtime

# Optional adapter smoke tests
pip install -e ".[server,mcp]" pytest httpx
make test-adapters
```

For host/operator setup checks, use `references/preflight_checklist.md`.

CI runs the full fast suite on Linux and a cross-platform smoke matrix on
Linux, macOS, and Windows. The smoke matrix verifies the manifest contract,
dispatcher, GC parser, editable install, and installed console command without
requiring a heap dump or MAT download. CI also runs an optional adapter smoke
job for the HTTP/FastAPI bridge and Claude MCP wrappers, plus a non-editable
package smoke that verifies installed skill bundle data outside a source
checkout.

A manual `MAT Runtime Smoke` GitHub Actions workflow is available for
release-readiness evidence. It runs on Linux, macOS, and Windows with Java 17,
then downloads, verifies, unpacks, and validates the pinned MAT distribution
without requiring a heap dump.

For the current release proof matrix and the remaining external evidence
required before claiming full maturity, see
`docs/architecture/RELEASE_EVIDENCE.md`.

After the maturity branch is committed and pushed, use the GitHub Actions
runbook in `docs/architecture/RELEASE_READINESS_CHECKLIST.md` to capture the
required cross-platform and MAT runtime run URLs. The MAT runtime workflow can
be started with:

```bash
gh workflow run "MAT Runtime Smoke" \
  --repo yaravind/jvm-memory-leak-debugger \
  --ref codex/maturity-roadmap
```

---

## Install

Core CLI install, no hosted-adapter dependencies:

```bash
python3 -m pip install --upgrade pip
pip install -e .
jvm-memory-leak-debugger --hprof /path/to/java_pidNNN.hprof --gc-log /path/to/gc.log
```

Optional adapter installs:

```bash
pip install -e ".[mcp]"      # Claude/MCP hosting
pip install -e ".[server]"   # FastAPI/HTTP bridge hosting
pip install -e ".[all]"      # every optional adapter
```

The core CLI supports Python 3.9+. The current MCP SDK requires Python 3.10+,
so `.[mcp]` and the MCP portion of `.[all]` only install on Python 3.10 or
newer.

The `requirements*.txt` files mirror these extras for harnesses that prefer
requirements-file installation.

---

## CLI Usage

```bash
# Check platform, Java, and MAT readiness without reading heap/GC artifacts:
python3 tools/debug_memory_leak.py --check-runtime
# or after install:
jvm-memory-leak-debugger --check-runtime --json

# Full analysis (Eclipse MAT runs — 10-30 min on large dumps):
python3 tools/debug_memory_leak.py \
  --hprof   /path/to/java_pidNNN.hprof \
  --gc-log  /path/to/gc-NNN.log

# After pip install -e .:
jvm-memory-leak-debugger --hprof /path/to/java_pidNNN.hprof --gc-log /path/to/gc-NNN.log

# MAT already ran (suspects ZIP exists beside hprof):
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --skip-mat

# Override dump timestamp when the hprof header is unavailable or intentionally ignored:
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... \
  --dump-time 2026-05-22T16:18:36-04:00

# Open Markdown report after generation (macOS):
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --open

# Print structured JSON to stdout:
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --json

# Tune MAT heap for very large dumps (default 12 GB):
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --mat-heap-gb 24

# Use an existing MAT installation instead of the default temp install root:
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --mat-home /opt/eclipse-mat

# Extend the MAT timeout for very large dumps (default 7200 seconds):
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --timeout-s 14400

# Add project-specific recommendations:
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... \
  --patterns-file examples/custom_patterns.json
```

MAT is installed automatically under the system temp directory on first use,
unless you pass an existing installation through the callable API. The Python
runner supports the pinned
Eclipse MAT 1.16.1 ZIP distributions for Linux x86_64/AArch64, macOS
x86_64/AArch64, and Windows x86_64.

Dump-to-GC correlation prefers the embedded HPROF header timestamp, then falls
back to file mtime with a warning in `report.json`. Use `--dump-time` to provide
an explicit timestamp when analysing transferred or synthetic artifacts.

---

## Deploy to Claude (MCP)

```bash
pip install mcp

# claude_desktop_config.json:
{
  "mcpServers": {
    "jvm-memory-leak-debugger": {
      "command": "jvm-memory-leak-debugger-mcp"
    }
  }
}
```

Restart Claude Desktop. Tools appear automatically in Claude's tool palette.

---

## Deploy to GitHub Copilot Extension

1. Create a GitHub App at https://github.com/settings/apps/new
2. Deploy the HTTP adapter to any HTTPS host: `pip install "jvm-memory-leak-debugger[server]" && jvm-memory-leak-debugger-api`
3. Register the app webhook pointing to your host
4. Upload `skill.json` as the skill manifest in the App configuration
5. Install the Copilot Extension in your org

Users then type `@jvm-memory-leak-debugger analyze /path/to/dump.hprof with /path/to/gc.log` in Copilot Chat.

Full step-by-step: see https://docs.github.com/en/copilot/building-copilot-extensions/about-building-copilot-extensions

Portable configuration examples for Claude MCP, direct function dispatch, and
HTTP bridge hosts are under `harnesses/`. The same directory includes
Codex-style local skill and GitHub Copilot Extension-style HTTP examples.
Use `harnesses/installed_commands.example.json` when a harness can launch the
installed console commands directly.

Installed adapter commands:

```bash
jvm-memory-leak-debugger-api --host 0.0.0.0 --port 8080
jvm-memory-leak-debugger-mcp
```

---

## Deploy to OpenAI Codex / GPT-4 Agents

```python
from openai import OpenAI
import json, sys, os

sys.path.insert(0, "tools")
from debug_memory_leak import run_full_analysis

client = OpenAI()
skill  = json.load(open("skill.json"))

tools = [
    {"type": "function", "function": {
        "name": t["name"],
        "description": t["description"],
        "parameters": t["parameters"],
    }}
    for t in skill["tools"]
]

assistant = client.beta.assistants.create(
    name="JVM Memory Leak Debugger",
    instructions=open("instructions/system_prompt.md").read(),
    tools=tools,
    model="gpt-4o",
)

def handle_tool_call(name, args):
    if name == "generate_report":
        return json.dumps(run_full_analysis(**args), default=str)
    # ... handle other tools
```

---

## Enabling JVM Artifacts

```
-Xlog:gc*:file=/path/jvm-logs/gc-%p.log:time,uptime,level,tags
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/path/jvm-logs/
```

Maven Surefire example:

```xml
<argLine>
  -Xmx8g
  -Xlog:gc*:file=${project.build.directory}/jvm-logs/gc-%p.log:time,uptime,level,tags
  -XX:+HeapDumpOnOutOfMemoryError
  -XX:HeapDumpPath=${project.build.directory}/jvm-logs/
</argLine>
```

---

## Pattern Library

Built-in recommendations are generic JVM/G1/MAT heuristics. Project-specific
classes, stack frames, and code pointers belong in a custom JSON pattern file,
loaded with `--patterns-file` or the `PATTERNS_FILE` environment variable.

Pattern files can be either a JSON array or an object with a `patterns` array.
Each pattern supports:

| Field | Purpose |
|-------|---------|
| `id`, `title`, `description`, `fixes[]` | Public recommendation content |
| `code_pointer` | Optional project path or URL for custom patterns |
| `match_class`, `match_stack`, `match_text` | Case-insensitive regex matchers over MAT findings |
| `gc` | Thresholds such as `min_to_space_exhausted` and `min_full_gc_count` |

See `examples/custom_patterns.json`, `references/fix_patterns.md`, and
`schemas/recommendation_patterns.json`.

---

## Session Findings — data-diff pid 16615

This skill was built from a real incident:

| Finding | Detail |
|---------|--------|
| Root cause | `JdbcDatasetReader.readResultSet()` buffered ~44M rows with no row cap |
| Accumulation | `VectorBuilder` retained **8,565 MB (99.78%)** on the `main` thread |
| Object graph | `java.lang.Object[32]` tree at 6.3 GB; two balanced halves ~3.1 GB each |
| Per-row overhead | ~6 objects/cell: `HashMap1 + HashTrieMap + Tuple2 + Some + String + byte[]` |
| GC signature | 33 Full GCs / 74s; 31 To-space exhausted; 850-1016 ms STW; 0.02% freed/GC |
| Dump captured | Elapsed 374.9s — inside Full GC storm; OOM proximity 100% |

---

## License

MIT
