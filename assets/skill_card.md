# JVM Memory Leak Debugger

Diagnoses JVM memory leaks from a heap dump and G1 unified GC log.

Inputs:

- `.hprof` heap dump
- JVM GC log from the same process run

Outputs:

- `report.json`: durable machine-readable evidence
- `report.md`: operator-friendly summary

Use it for:

- `OutOfMemoryError: Java heap space`
- repeated G1 Full GC with little reclaimed memory
- To-space exhaustion cascades
- suspected unbounded collections, maps, queues, caches, buffers, or thread
  local retention

Run locally:

```bash
python3 tools/debug_memory_leak.py --hprof /path/to/dump.hprof --gc-log /path/to/gc.log
```

Host surfaces:

- standalone CLI
- Claude MCP server through `mcp_server.py`
- HTTP/FastAPI bridge through `server.py`
- function-tool dispatch through `tools/dispatch.py`
