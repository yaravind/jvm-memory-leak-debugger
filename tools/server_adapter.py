"""
server_adapter.py
=================
Packageable FastAPI bridge for GitHub Copilot Extensions, Codex, and other
HTTP/function-tool hosts.
"""

import argparse
from typing import Callable

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    import uvicorn
    _SERVER_IMPORT_ERROR = None
except ImportError as e:
    FastAPI = None
    Request = object
    JSONResponse = dict
    uvicorn = None
    _SERVER_IMPORT_ERROR = e

from dispatch import TOOLS, ToolDispatchError, dispatch_tool
from skill_resources import load_json


if FastAPI is not None:
    app = FastAPI(
        title="JVM Memory Leak Debugger",
        description="Agent skill: GC log + hprof -> root cause + fix recommendations",
        version="1.0.0",
    )
else:
    app = None


def _err(e: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(e), "type": type(e).__name__})


def _dispatch_err(e: ToolDispatchError) -> JSONResponse:
    return JSONResponse(
        status_code=e.status_code,
        content={"error": str(e), "type": type(e).__name__},
    )


def health():
    return {"status": "ok", "skill": "jvm-memory-leak-debugger", "version": "1.0.0"}


def skill_manifest():
    fallback = {
        "schema_version": "1.0",
        "id": "jvm-memory-leak-debugger",
        "name": "JVM Memory Leak Debugger",
        "version": "1.0.0",
        "tools": [{"name": name, "description": spec.description} for name, spec in TOOLS.items()],
    }
    return load_json("skill.json", fallback)


def tool_catalog():
    manifest = skill_manifest()
    manifest_tools = {
        tool.get("name"): tool
        for tool in manifest.get("tools", [])
        if tool.get("name")
    }
    return {
        "tools": [
            {
                "name": name,
                "description": spec.description,
                "route": f"/tools/{name}",
                "method": "POST",
                "parameters": manifest_tools.get(name, {}).get("parameters", {}),
            }
            for name, spec in TOOLS.items()
        ]
    }


def _make_tool_route(tool_name: str) -> Callable[[Request], dict]:
    async def route(request: Request):
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON request body.", "type": "InvalidRequestBody"},
            )

        try:
            return dispatch_tool(tool_name, body)
        except ToolDispatchError as e:
            return _dispatch_err(e)
        except Exception as e:
            return _err(e)

    route.__name__ = tool_name
    route.__doc__ = TOOLS[tool_name].description
    return route


if app is not None:
    app.get("/health")(health)
    app.get("/skill.json")(skill_manifest)
    app.get("/tools")(tool_catalog)
    for _tool_name in TOOLS:
        app.post(f"/tools/{_tool_name}")(_make_tool_route(_tool_name))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JVM Memory Leak Debugger HTTP adapter")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if _SERVER_IMPORT_ERROR is not None:
        raise SystemExit(
            "FastAPI not installed. Run: pip install 'jvm-memory-leak-debugger[server]'\n"
            "For source checkouts: pip install -e '.[server]'"
        )
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
