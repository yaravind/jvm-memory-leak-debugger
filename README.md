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
│   ├── conftest.py
│   ├── test_gc_parser.py
│   └── test_reporter.py
├── schemas/
│   ├── gc_analysis_result.json      # JSON Schema for analyze_gc_log output
│   └── memory_leak_report.json      # JSON Schema for generate_report output
├── examples/
│   └── conversation_examples.md     # Sample user-agent conversations
├── mcp_server.py                    # Claude MCP server
├── server.py                        # FastAPI bridge (Copilot / Codex)
├── Makefile                         # make test | make lint | make run-example
├── pytest.ini
└── .github/workflows/
    └── test-skill.yml               # CI: tests + lint on every push
```

---

## Requirements

| Requirement | Details |
|-------------|---------|
| Python 3.9+ | stdlib only — no pip install needed for core tools |
| Java 17+ | Required by Eclipse MAT 1.16. Set `JAVA17_HOME` or use Microsoft JDK 17 |
| curl | Auto-download Eclipse MAT on first use |
| hdiutil | macOS only — unpack MAT DMG. Linux fallback uses tar |
| Internet (first run) | Downloads MAT ~92 MB from download.eclipse.org |

---

## Build & Test

No build step — Python stdlib only.

```bash
cd skills/jvm-memory-leak-debugger

# Run unit tests (11 tests, ~0.05s)
make test
# or: PYTHONPATH=tools python3 -m pytest tests/ -v

# Validate skill.json + JSON schemas
make validate-manifests

# Smoke test against real session artifacts (skip MAT re-run)
make run-example
```

---

## CLI Usage

```bash
# Full analysis (Eclipse MAT runs — 10-30 min on large dumps):
python3 tools/debug_memory_leak.py \
  --hprof   /path/to/java_pidNNN.hprof \
  --gc-log  /path/to/gc-NNN.log

# MAT already ran (suspects ZIP exists beside hprof):
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --skip-mat

# Open Markdown report after generation (macOS):
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --open

# Print structured JSON to stdout:
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --json

# Tune MAT heap for very large dumps (default 12 GB):
python3 tools/debug_memory_leak.py --hprof ... --gc-log ... --mat-heap-gb 24
```

---

## Deploy to Claude (MCP)

```bash
pip install mcp

# claude_desktop_config.json:
{
  "mcpServers": {
    "jvm-memory-leak-debugger": {
      "command": "python3",
      "args": ["/path/to/skills/jvm-memory-leak-debugger/mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop. Tools appear automatically in Claude's tool palette.

---

## Deploy to GitHub Copilot Extension

1. Create a GitHub App at https://github.com/settings/apps/new
2. Deploy `server.py` to any HTTPS host: `pip install fastapi uvicorn && uvicorn server:app --host 0.0.0.0 --port 8080`
3. Register the app webhook pointing to your host
4. Upload `skill.json` as the skill manifest in the App configuration
5. Install the Copilot Extension in your org

Users then type `@jvm-memory-leak-debugger analyze /path/to/dump.hprof with /path/to/gc.log` in Copilot Chat.

Full step-by-step: see https://docs.github.com/en/copilot/building-copilot-extensions/about-building-copilot-extensions

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

Extend `tools/reporter.py` `_KNOWN_PATTERNS` with new entries:

| Pattern ID | Trigger | Code Pointer |
|-----------|---------|--------------|
| `unbounded_jdbc_read` | `JdbcDatasetReader.readResultSet` on stack | `JdbcDatasetReader.scala:97` |
| `vectorbuilder_leak` | `VectorBuilder` in dominator tree | — |
| `immutable_hashmap_overhead` | `HashMap$HashMap1`/`HashTrieMap` at scale | — |
| `to_space_exhausted` | To-space exhausted events in GC log | — |

Each pattern: `id`, `title`, `description`, `fixes[]`, `code_pointer`.

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
