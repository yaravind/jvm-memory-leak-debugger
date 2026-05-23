"""
skill_resources.py
==================
Small helpers for locating skill bundle files from source checkouts and
editable/package installs.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def _candidate_roots() -> list:
    here = Path(__file__).resolve()
    return [
        here.parent.parent,
        Path.cwd(),
        Path(sys.prefix) / "share" / "jvm-memory-leak-debugger",
    ]


def find_repo_file(relative_path: str) -> Optional[Path]:
    """Return the first matching skill file from known source/install roots."""
    for root in _candidate_roots():
        candidate = root / relative_path
        if candidate.exists():
            return candidate
    return None


def read_text(relative_path: str, fallback: str = "") -> str:
    path = find_repo_file(relative_path)
    if path is None:
        return fallback
    return path.read_text()


def load_json(relative_path: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    path = find_repo_file(relative_path)
    if path is None:
        return fallback
    with open(path) as f:
        return json.load(f)
