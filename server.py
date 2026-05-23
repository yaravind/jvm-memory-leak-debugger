"""
server.py
=========
FastAPI bridge for GitHub Copilot Extensions and OpenAI Assistants API.

Usage:
    pip install fastapi uvicorn
    uvicorn server:app --host 0.0.0.0 --port 8080

All four skill tools are exposed as HTTP POST endpoints.
The request body must match the parameter schema defined in skill.json.

See README.md for full Copilot Extension and Codex deployment instructions.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    raise SystemExit(
        "FastAPI not installed. Run: pip install fastapi uvicorn\n"
        "Then: uvicorn server:app --host 0.0.0.0 --port 8080"
    )

from debug_memory_leak import run_full_analysis
from gc_parser import parse_gc_log, gc_summary_to_dict
from mat_runner import analyse_hprof
from correlator import correlate as _correlate

app = FastAPI(
    title="JVM Memory Leak Debugger",
    description="Agent skill: GC log + hprof → root cause + fix recommendations",
    version="1.0.0",
)


def _err(e: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(e), "type": type(e).__name__})


@app.get("/health")
def health():
    return {"status": "ok", "skill": "jvm-memory-leak-debugger", "version": "1.0.0"}


@app.get("/skill.json")
def skill_manifest():
    with open(os.path.join(os.path.dirname(__file__), "skill.json")) as f:
        return json.load(f)


@app.post("/tools/generate_report")
async def generate_report(request: Request):
    """Full pipeline: GC log + hprof → report.json + report.md"""
    try:
        body = await request.json()
        result = run_full_analysis(
            hprof_path=body["hprof_path"],
            gc_log_path=body["gc_log_path"],
            output_dir=body.get("output_dir"),
            skip_mat=body.get("skip_mat", False),
            mat_heap_gb=body.get("mat_heap_gb", 12),
        )
        return result
    except Exception as e:
        return _err(e)


@app.post("/tools/analyze_gc_log")
async def analyze_gc_log(request: Request):
    """Parse a GC log and return structured statistics"""
    try:
        body = await request.json()
        gc_path = body["gc_log_path"]
        if not os.path.exists(gc_path):
            raise HTTPException(status_code=422, detail=f"GC log not found: {gc_path}")
        return gc_summary_to_dict(parse_gc_log(gc_path))
    except HTTPException:
        raise
    except Exception as e:
        return _err(e)


@app.post("/tools/extract_heap_suspects")
async def extract_heap_suspects(request: Request):
    """Run Eclipse MAT headlessly and return leak suspects + histogram"""
    try:
        body = await request.json()
        hprof = body["hprof_path"]
        if not os.path.exists(hprof):
            raise HTTPException(status_code=422, detail=f"hprof not found: {hprof}")
        return analyse_hprof(
            hprof_path=hprof,
            mat_heap_gb=body.get("mat_heap_gb", 12),
            timeout_s=body.get("timeout_s", 7200),
        )
    except HTTPException:
        raise
    except Exception as e:
        return _err(e)


@app.post("/tools/correlate_dump_to_gc")
async def correlate_dump_to_gc(request: Request):
    """Correlate dump mtime with GC timeline → dump_phase, oom_proximity, inferred_trigger"""
    try:
        body = await request.json()
        gc_sum = parse_gc_log(body["gc_log_path"])
        return _correlate(
            gc_summary=gc_sum,
            gc_log_path=body["gc_log_path"],
            hprof_path=body["hprof_path"],
            window_s=body.get("window_s", 60.0),
        )
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

