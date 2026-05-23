#!/usr/bin/env bash
# run_mat.sh
# ----------
# Runs Eclipse Memory Analyzer (MAT) headlessly on an .hprof heap dump.
# Auto-downloads MAT 1.16 if not already installed.
#
# Usage:
#   ./run_mat.sh <hprof_path> [mat_heap_gb]
#
# Environment variables:
#   JAVA17_HOME   — path to a Java 17+ JDK (default: auto-detected)
#   MAT_INSTALL   — path where MAT is/should be installed
#                   (default: ~/tools/eclipse-mat)
#
# Outputs a <hprof_stem>_Leak_Suspects.zip beside the .hprof file.

set -euo pipefail

HPROF="${1:-}"
MAT_HEAP_GB="${2:-12}"

if [[ -z "$HPROF" ]]; then
  echo "Usage: $0 <hprof_path> [mat_heap_gb]" >&2
  exit 1
fi

if [[ ! -f "$HPROF" ]]; then
  echo "ERROR: Heap dump not found: $HPROF" >&2
  exit 1
fi

HPROF="$(cd "$(dirname "$HPROF")" && pwd)/$(basename "$HPROF")"

# ---------------------------------------------------------------------------
# Locate Java 17+
# ---------------------------------------------------------------------------
if [[ -n "${JAVA17_HOME:-}" ]]; then
  JAVA_BIN="$JAVA17_HOME/bin/java"
elif [[ -d "/Library/Java/JavaVirtualMachines/microsoft-17.jdk/Contents/Home" ]]; then
  JAVA_BIN="/Library/Java/JavaVirtualMachines/microsoft-17.jdk/Contents/Home/bin/java"
else
  JAVA_BIN="$(command -v java || true)"
  if [[ -z "$JAVA_BIN" ]]; then
    echo "ERROR: Java 17+ not found. Set JAVA17_HOME or install Microsoft JDK 17." >&2
    exit 1
  fi
fi
echo "Using Java: $JAVA_BIN ($("$JAVA_BIN" -version 2>&1 | head -1))"

# ---------------------------------------------------------------------------
# Install MAT if absent
# ---------------------------------------------------------------------------
MAT_INSTALL="${MAT_INSTALL:-$HOME/tools/eclipse-mat}"
MAT_EXEC="$MAT_INSTALL/ParseHeapDump.sh"

if [[ ! -x "$MAT_EXEC" ]]; then
  echo "Eclipse MAT not found at $MAT_INSTALL — downloading..."
  mkdir -p "$MAT_INSTALL"

  PLATFORM="$(uname -s)"
  if [[ "$PLATFORM" == "Darwin" ]]; then
    MAT_URL="https://download.eclipse.org/mat/1.16.0/rcp/MemoryAnalyzer-1.16.0.20241122-macosx.cocoa.x86_64.dmg"
    DMG="/tmp/mat.dmg"
    curl -L --progress-bar -o "$DMG" "$MAT_URL"
    hdiutil attach "$DMG" -nobrowse -quiet
    cp -R /Volumes/MemoryAnalyzer*/mat/* "$MAT_INSTALL/"
    hdiutil detach /Volumes/MemoryAnalyzer* -quiet
    rm -f "$DMG"
  else
    MAT_URL="https://download.eclipse.org/mat/1.16.0/rcp/MemoryAnalyzer-1.16.0.20241122-linux.gtk.x86_64.tar.gz"
    curl -L --progress-bar -o /tmp/mat.tar.gz "$MAT_URL"
    tar -xzf /tmp/mat.tar.gz -C "$MAT_INSTALL" --strip-components=1
    rm -f /tmp/mat.tar.gz
  fi

  chmod +x "$MAT_EXEC"
  echo "MAT installed at $MAT_INSTALL"
fi

# ---------------------------------------------------------------------------
# Run MAT
# ---------------------------------------------------------------------------
echo "Running Eclipse MAT on: $HPROF"
echo "  MAT heap: ${MAT_HEAP_GB}g"

JAVA17_HOME_DIR="$(dirname "$(dirname "$JAVA_BIN")")"
export JAVA_HOME="$JAVA17_HOME_DIR"

"$MAT_EXEC" \
  "$HPROF" \
  -vmargs "-Xmx${MAT_HEAP_GB}g" \
  org.eclipse.mat.api.leak \
  org.eclipse.mat.api.suspects \
  org.eclipse.mat.api.overview

STEM="${HPROF%.hprof}"
ZIP="${STEM}_Leak_Suspects.zip"

if [[ -f "$ZIP" ]]; then
  echo "OK: Suspects ZIP written to $ZIP"
else
  echo "WARNING: Suspects ZIP not found at expected path: $ZIP" >&2
  echo "         Check MAT output directory for generated files." >&2
  exit 1
fi

