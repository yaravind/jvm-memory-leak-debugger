#!/usr/bin/env bash
# validate_artifacts.sh
# ---------------------
# Checks that a .hprof heap dump and JVM GC log are present and non-empty.
# Usage: ./validate_artifacts.sh <hprof_path> <gc_log_path>
# Exit 0 = both files OK; Exit 1 = one or more problems found.

set -euo pipefail

HPROF="${1:-}"
GC_LOG="${2:-}"
ERRORS=0

check_file() {
  local label="$1"
  local path="$2"
  if [[ -z "$path" ]]; then
    echo "ERROR: $label path not provided." >&2
    ((ERRORS++))
    return
  fi
  if [[ ! -f "$path" ]]; then
    echo "ERROR: $label not found: $path" >&2
    ((ERRORS++))
    return
  fi
  local size
  size=$(wc -c < "$path" | tr -d ' ')
  if [[ "$size" -eq 0 ]]; then
    echo "ERROR: $label is empty (0 bytes): $path" >&2
    ((ERRORS++))
    return
  fi
  echo "OK: $label — $path ($(du -sh "$path" | cut -f1))"
}

check_file "Heap dump (.hprof)" "$HPROF"
check_file "GC log"             "$GC_LOG"

# Quick sanity: GC log should contain at least one GC event line
if [[ -n "$GC_LOG" && -f "$GC_LOG" ]]; then
  if ! grep -qE '\[gc[ *\]]|\[gc,|GC\(' "$GC_LOG" 2>/dev/null; then
    echo "WARNING: GC log does not appear to contain JVM unified GC events." >&2
    echo "         Expected format: -Xlog:gc*:file=<path>:time,uptime,level,tags" >&2
  fi
fi

if [[ "$ERRORS" -gt 0 ]]; then
  echo ""
  echo "Fix: add the following JVM flags to produce the required artifacts:"
  echo "  -Xlog:gc*:file=/path/to/jvm-logs/gc-%p.log:time,uptime,level,tags"
  echo "  -XX:+HeapDumpOnOutOfMemoryError"
  echo "  -XX:HeapDumpPath=/path/to/jvm-logs/"
  exit 1
fi

echo ""
echo "All artifacts validated. Proceed with analysis."
exit 0

