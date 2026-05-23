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

from server_adapter import *  # noqa: F401,F403
from server_adapter import main


if __name__ == "__main__":
    main()
