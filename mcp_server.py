"""
mcp_server.py
=============
Compatibility wrapper for the packageable MCP adapter.

Run source checkouts with:
    python3 mcp_server.py

Run installed environments with:
    jvm-memory-leak-debugger-mcp
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

from mcp_adapter import *  # noqa: F401,F403
from mcp_adapter import main


if __name__ == "__main__":
    main()
