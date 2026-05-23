#!/usr/bin/env python3
"""
generate_report.py
------------------
Standalone CLI wrapper around run_full_analysis (the generate_report tool).
Provides a simple entry point without requiring the agent runtime.

Usage:
    python3 scripts/generate_report.py \
        --hprof  /path/to/java_pidNNN.hprof \
        --gc-log /path/to/gc-NNN.log

    # Skip MAT if suspects ZIP already exists:
    python3 scripts/generate_report.py --hprof ... --gc-log ... --skip-mat

    # Print full JSON result to stdout:
    python3 scripts/generate_report.py --hprof ... --gc-log ... --json

    # Open the Markdown report after generation (macOS):
    python3 scripts/generate_report.py --hprof ... --gc-log ... --open
"""
import sys
from pathlib import Path

# Allow running from repo root or scripts/ directory
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent / "tools"))

from debug_memory_leak import main

if __name__ == "__main__":
    sys.exit(main())

