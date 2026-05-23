# 0002: Use Pyproject For Portable CLI And Optional Adapter Extras

## Status

Accepted

## Context

The project must work as both an agent skill and a standalone JVM memory leak
debugging tool. Core analysis currently uses only the Python standard library,
while MCP and HTTP/FastAPI hosting require optional dependencies. A widely
adoptable skill needs a normal Python installation path, a stable console
command, and clear optional extras without making local CLI users install server
packages they do not need.

## Decision

Add `pyproject.toml` using setuptools. Package the core modules from `tools/` as
top-level Python modules and expose `jvm-memory-leak-debugger` as a console
script that calls `debug_memory_leak:main`.

Expose packageable adapter launchers as console scripts:

- `jvm-memory-leak-debugger-api` for the FastAPI/HTTP bridge
- `jvm-memory-leak-debugger-mcp` for Claude/MCP hosting

Install skill bundle files under `share/jvm-memory-leak-debugger` so installed
adapters can serve `skill.json` and read instructions without requiring the
current working directory to be a source checkout.

Keep a minimal `setup.py` shim so editable installs work on older pip versions
that do not support PEP 660 editable installs from `pyproject.toml` alone.

Keep the core package dependency-free. Declare adapter dependencies as optional
extras:

- `mcp` for Claude/MCP hosting on Python 3.10+
- `server` for FastAPI/HTTP hosting
- `all` for local environments that want every adapter

Keep `requirements*.txt` files as compatibility helpers for users and harnesses
that prefer requirements files.

## Consequences

Users can install the CLI with `pip install -e .` during development or install
from a packaged distribution later. Hosted adapter users can install only the
extra they need, for example `.[mcp]` or `.[server]`, and launch adapters
without relying on source-checkout paths. Adapter resource lookup now checks
source roots, the current working directory, and the installed shared-data
directory.

The MCP extra is version-marked because current MCP SDK releases require Python
3.10+, while the core CLI remains Python 3.9 compatible. The packaging remains
intentionally lightweight, but the project still has top-level modules rather
than a namespaced Python package. A future package namespace would be a breaking
import-path change and should be handled in a separate ADR if needed.
