Recommendation Patterns
=======================

The built-in recommendation patterns are intentionally generic JVM, G1 GC, and
MAT heuristics. Project-specific classes, stack frames, and code pointers should
live in a custom JSON pattern file instead of `tools/reporter.py`.

Load a custom file with either:

```bash
python3 tools/debug_memory_leak.py \
  --hprof /path/to/dump.hprof \
  --gc-log /path/to/gc.log \
  --patterns-file /path/to/patterns.json
```

or:

```bash
PATTERNS_FILE=/path/to/patterns.json python3 tools/debug_memory_leak.py ...
```

The file can be either a top-level array of pattern objects or an object with a
`patterns` array. See `schemas/recommendation_patterns.json` and
`examples/custom_patterns.json`.

Pattern fields:

| Field | Required | Description |
| --- | --- | --- |
| `id` | yes | Stable recommendation identifier. |
| `title` | yes | Human-readable recommendation heading. |
| `description` | yes | Explanation of why the pattern matters. |
| `fixes` | yes | Ordered list of suggested fixes. |
| `code_pointer` | no | Optional repository path, URL, or note for project-specific remediation. |
| `match_class` | no | Case-insensitive regex matched against MAT suspect, dominator, and histogram text. |
| `match_stack` | no | Case-insensitive regex matched against MAT stack frames. |
| `match_text` | no | Case-insensitive regex matched against combined MAT suspect text. |
| `gc` | no | Numeric GC thresholds such as `min_to_space_exhausted`, `min_full_gc_count`, and `min_concurrent_abort_count`. |

Validation rules:

- `id` values must be unique across built-in and custom patterns.
- Every custom pattern must define at least one matcher: `match_class`,
  `match_stack`, `match_text`, or `gc`.
- Regex fields are compiled at load time so syntax errors fail before report
  generation starts.
- GC threshold values must be non-negative integers.
- Unknown GC threshold names are rejected.

Each matched recommendation in `report.json` includes `pattern_source`, set to
`builtin` for built-in patterns or the custom pattern file path for user-supplied
patterns.
