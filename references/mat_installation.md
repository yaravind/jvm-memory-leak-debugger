# Eclipse MAT Runtime Guide

`extract_heap_suspects` uses Eclipse Memory Analyzer (MAT) headlessly. The
runner does not parse `.hprof` files directly.

Requirements:

- Java 17 or newer
- `curl` for first-run download
- enough disk space for the heap dump, MAT indexes, and generated reports
- enough RAM for MAT; start with `mat_heap_gb=12` and increase for large dumps

Java discovery order:

1. `JAVA17_HOME`
2. `JAVA_HOME`
3. macOS `/usr/libexec/java_home -v 17`
4. `java` on `PATH`

MAT installation:

- The runner downloads pinned MAT 1.16.1 ZIP distributions from Eclipse.
- Supported packages are Linux x86_64/AArch64, macOS x86_64/AArch64, and
  Windows x86_64.
- Archives are SHA-256 verified before unpacking.
- The default install root is the host temp directory under
  `eclipse-mat/<version>`.
- Use `python3 tools/debug_memory_leak.py --check-runtime` or installed
  `jvm-memory-leak-debugger --check-runtime --json` to verify platform, Java,
  curl availability for first-run downloads, configured MAT archive, and any
  existing MAT installation without reading a heap dump or downloading MAT.
- Managed MAT installs are considered ready only when the Eclipse plugin
  directory and Equinox launcher jar are present. If the launcher is missing,
  fix the MAT install or allow the runner to download the pinned archive.
- Use `make test-mat-runtime` when you intentionally want to download, verify,
  unpack, and validate the pinned MAT archive for the current host without
  running heap analysis.
- Pass `--mat-home /path/to/eclipse-mat` to the CLI, or `mat_home` through
  `extract_heap_suspects` / `generate_report`, when a host manages MAT outside
  the default temp install root.

Operational notes:

- MAT can take 10-30 minutes on large production dumps.
- Existing `*_Leak_Suspects.zip` and `.index` files beside the heap dump are
  reused.
- Temporary MAT workspaces are removed after success, failure, or timeout.
- If MAT cannot run, use `analyze_gc_log` and `correlate_dump_to_gc` anyway so
  the report still captures GC pressure and timestamp evidence.

Common fixes:

- `Java 17+ is required`: install a JDK 17+ and set `JAVA17_HOME`.
- `curl is required`: install curl for first-run MAT download, or pass
  `mat_home` pointing at an existing MAT installation.
- `Equinox launcher jar not found`: the MAT install is incomplete or points at
  the wrong directory. Use the root produced by the pinned MAT ZIP, or rerun
  `make test-mat-runtime` on a host that can download MAT.
- `No Eclipse MAT distribution configured`: run on one of the supported OS and
  CPU combinations, or add a pinned distribution entry in `tools/mat_runner.py`.
- Timeout: increase `timeout_s` and `mat_heap_gb`, or run on a larger machine.
