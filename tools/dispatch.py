"""
dispatch.py
===========
Shared tool registry for all hosting surfaces.

Adapters should call `dispatch_tool(name, params)` so callable names, defaults,
and validation stay consistent across CLI-adjacent code, HTTP, MCP, and direct
agent runtimes.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping

from correlator import correlate
from gc_parser import parse_and_summarize, parse_gc_log
from mat_runner import DEFAULT_MAT_HOME, analyse_hprof
from pipeline import run_full_analysis


class ToolDispatchError(Exception):
    """Raised when a registered tool cannot be dispatched."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[[Mapping[str, Any]], Dict[str, Any]]


def _missing(params: Mapping[str, Any], required: Iterable[str]) -> list:
    return [key for key in required if key not in params or params[key] in (None, "")]


def _require(params: Mapping[str, Any], *required: str) -> None:
    missing = _missing(params, required)
    if missing:
        raise ToolDispatchError(f"Missing required parameter(s): {', '.join(missing)}", status_code=422)


def _require_file(path: str, label: str) -> None:
    if not Path(path).exists():
        raise ToolDispatchError(f"{label} not found: {path}", status_code=422)


def _analyze_gc_log(params: Mapping[str, Any]) -> Dict[str, Any]:
    _require(params, "gc_log_path")
    _require_file(str(params["gc_log_path"]), "GC log")
    return parse_and_summarize(str(params["gc_log_path"]))


def _extract_heap_suspects(params: Mapping[str, Any]) -> Dict[str, Any]:
    _require(params, "hprof_path")
    _require_file(str(params["hprof_path"]), "hprof")
    return analyse_hprof(
        hprof_path=str(params["hprof_path"]),
        mat_home=(
            Path(str(params["mat_home"]))
            if params.get("mat_home")
            else DEFAULT_MAT_HOME
        ),
        mat_heap_gb=int(params.get("mat_heap_gb", 12)),
        timeout_s=int(params.get("timeout_s", 7200)),
    )


def _correlate_dump_to_gc(params: Mapping[str, Any]) -> Dict[str, Any]:
    _require(params, "gc_log_path", "hprof_path")
    _require_file(str(params["gc_log_path"]), "GC log")
    _require_file(str(params["hprof_path"]), "hprof")
    gc_sum = parse_gc_log(str(params["gc_log_path"]))
    return correlate(
        gc_summary=gc_sum,
        gc_log_path=str(params["gc_log_path"]),
        hprof_path=str(params["hprof_path"]),
        window_s=float(params.get("window_s", 60.0)),
        dump_time=params.get("dump_time"),
    )


def _generate_report(params: Mapping[str, Any]) -> Dict[str, Any]:
    _require(params, "hprof_path", "gc_log_path")
    _require_file(str(params["hprof_path"]), "hprof")
    _require_file(str(params["gc_log_path"]), "GC log")
    return run_full_analysis(
        hprof_path=str(params["hprof_path"]),
        gc_log_path=str(params["gc_log_path"]),
        output_dir=params.get("output_dir"),
        skip_mat=bool(params.get("skip_mat", False)),
        mat_home=params.get("mat_home"),
        mat_heap_gb=int(params.get("mat_heap_gb", 12)),
        timeout_s=int(params.get("timeout_s", 7200)),
        patterns_file=params.get("patterns_file"),
        dump_time=params.get("dump_time"),
    )


TOOLS: Dict[str, ToolSpec] = {
    "analyze_gc_log": ToolSpec(
        name="analyze_gc_log",
        description="Parse a JVM G1 unified GC log and return structured statistics.",
        handler=_analyze_gc_log,
    ),
    "extract_heap_suspects": ToolSpec(
        name="extract_heap_suspects",
        description="Run Eclipse MAT headlessly and return leak suspects plus histogram data.",
        handler=_extract_heap_suspects,
    ),
    "correlate_dump_to_gc": ToolSpec(
        name="correlate_dump_to_gc",
        description="Correlate a heap dump timestamp with the GC log timeline.",
        handler=_correlate_dump_to_gc,
    ),
    "generate_report": ToolSpec(
        name="generate_report",
        description="Run the full GC, heap, correlation, recommendation, and report pipeline.",
        handler=_generate_report,
    ),
}


def dispatch_tool(name: str, params: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        spec = TOOLS[name]
    except KeyError:
        raise ToolDispatchError(f"Unknown tool: {name}", status_code=404)
    if not isinstance(params, Mapping):
        raise ToolDispatchError("Tool parameters must be a JSON object.", status_code=422)
    return spec.handler(params)
