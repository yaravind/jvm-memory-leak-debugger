#!/usr/bin/env python3
"""
Run pyflakes when available, otherwise compile files as a stdlib-only fallback.
"""

import importlib.util
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path


def _compile(files):
    with tempfile.TemporaryDirectory(prefix="jvm-memleak-pycompile-") as tmp:
        tmp_dir = Path(tmp)
        for index, file_name in enumerate(files):
            cfile = tmp_dir / f"{index}-{Path(file_name).name}.pyc"
            py_compile.compile(file_name, cfile=str(cfile), doraise=True)
    print(f"pyflakes not installed; py_compile fallback passed for {len(files)} files.")
    return 0


def main(argv):
    files = [str(Path(arg)) for arg in argv[1:]]
    if not files:
        print("usage: lint_or_compile.py <python-file> [...]", file=sys.stderr)
        return 2

    if importlib.util.find_spec("pyflakes") is not None:
        return subprocess.call([sys.executable, "-m", "pyflakes", *files])
    return _compile(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
