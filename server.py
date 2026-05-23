"""
server.py
=========
Compatibility wrapper for the packageable FastAPI adapter.

Run source checkouts with:
    python3 server.py

Run installed environments with:
    jvm-memory-leak-debugger-api
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

import server_adapter as _adapter

TOOLS = _adapter.TOOLS
app = _adapter.app
health = _adapter.health
main = _adapter.main
skill_manifest = _adapter.skill_manifest
tool_catalog = _adapter.tool_catalog

__all__ = ["TOOLS", "app", "health", "main", "skill_manifest", "tool_catalog"]


if __name__ == "__main__":
    main()
