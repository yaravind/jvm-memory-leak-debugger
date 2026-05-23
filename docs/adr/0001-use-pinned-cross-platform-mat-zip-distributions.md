# 0001: Use Pinned Cross-Platform MAT ZIP Distributions

## Status

Accepted

## Context

The initial MAT runner used a macOS-only `.dmg` download, `hdiutil`, a
developer-machine install path, and a specific local Java 17 path. That made the
heap suspect extraction tool unusable on Linux CI runners, most servers,
Windows, and non-identical macOS machines.

Eclipse publishes standalone Memory Analyzer 1.16.1 ZIP distributions for
Linux, macOS, and Windows. Those archives contain the Eclipse runtime layout
needed by the headless `org.eclipse.mat.api.parse` application.

## Decision

Use pinned Eclipse MAT 1.16.1 ZIP distributions for the Python MAT installer
across supported operating systems:

- Linux x86_64 and AArch64
- macOS x86_64 and AArch64
- Windows x86_64

The installer selects a platform package from `platform.system()` and
`platform.machine()`, verifies the archive SHA-256 before extraction, and
discovers the Eclipse plugin directory from either the Linux/Windows `mat/`
layout or the macOS `MemoryAnalyzer.app/Contents/Eclipse` layout.

Java discovery is explicit-env-first: `JAVA17_HOME`, then `JAVA_HOME`, then
platform/PATH discovery. Configured environment variables must point to Java
17+; older configured homes fail clearly rather than silently falling through to
another Java installation.

## Consequences

The Python runner no longer depends on macOS `hdiutil`, `.dmg` mounting, or a
developer-machine Java path. Normal tests can verify platform selection and
install layout handling without downloading MAT.

The project now owns pinned SHA-256 values for each supported MAT archive.
Future MAT upgrades must update package names, hashes, and tests together.

Windows ARM64 is not supported by the pinned Eclipse MAT 1.16.1 standalone
package set. Users on that platform should use Windows x86_64 emulation if
viable, WSL with the Linux package, or provide a custom MAT installation.
