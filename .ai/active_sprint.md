# Active Sprint: JVM Memory Leak Debugger Maturity

Updated: 2026-05-23

## Branch

- `codex/maturity-roadmap`

## Goal

Mature this repo into a portable JVM memory leak debugging skill/CLI usable from
Codex, Claude, GitHub Copilot, MCP hosts, HTTP adapters, and shell workflows.

## GitHub State

- `gh auth status` reports the default `yaravind` token is invalid.
- Despite that warning, `gh issue list` and `gh issue view` worked for
  `yaravind/jvm-memory-leak-debugger`.
- `gh issue comment` initially hit a network restriction, then succeeded after
  explicit approval for the `gh issue comment` command prefix.
- Existing issues reviewed before local planning:
  - P1: #1, #2, #3
  - P2: #4, #5, #6, #7
  - P3/P4 summary reviewed from issue list: #8 through #14
- Existing issue updates added:
  - #1: M2 MAT portability planning note
  - #2: dependency manifest implementation note
  - #3: M3 pluggable recommendations planning note
  - #4: raw MAT text removal implementation note
  - #5: M4 HPROF timestamp planning note
  - #6: MAT temp workspace cleanup implementation note
  - #7: manifest callable implementation note
  - #8: M5 shared registry planning note
- Re-checked `gh auth status` during packaging work; it still reports the
  default `yaravind` token is invalid, but `gh issue comment` continued to work.
- Added #2 packaging implementation note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4525985043
- Re-checked `gh auth status` during cross-platform CI work; it still reports
  the default `yaravind` token is invalid, but `gh issue comment` continued to
  work.
- Added #1 cross-platform CI implementation note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526008552
- Re-checked `gh auth status` during optional adapter smoke work; it still
  reports the default `yaravind` token is invalid, but `gh issue comment`
  continued to work.
- Added #8 optional adapter smoke implementation note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526014744
- Re-checked `gh auth status` during adapter packaging work; it still reports
  the default `yaravind` token is invalid, but `gh issue comment` continued to
  work.
- Added #8 adapter packaging follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526050053
- Re-checked `gh auth status` during package-data work; it still reports the
  default `yaravind` token is invalid, but `gh issue comment` continued to work.
- Added #2 package-data follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526096837
- Re-checked `gh auth status` during package-smoke CI work; it still reports
  the default `yaravind` token is invalid, but `gh issue comment` continued to
  work.
- Added #2 package-smoke CI follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526101098
- Re-checked `gh auth status` during output-contract validation work; it still
  reports the default `yaravind` token is invalid. The first `gh issue comment`
  attempt hit a network error, then succeeded after explicit network approval.
- Added #10 output-contract validation implementation note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/10#issuecomment-4526108014
- Re-checked `gh auth status` during pipeline report-contract enforcement work;
  it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #10 pipeline enforcement follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/10#issuecomment-4526141278
- Re-checked `gh auth status` during MAT runtime diagnostic work; it still
  reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #1 MAT runtime diagnostic follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526150165
- Re-checked `gh auth status` during cross-platform diagnostic CI guardrail
  work; it still reports the default `yaravind` token is invalid. Initial
  `gh issue comment` attempts hit network errors, then succeeded after
  explicit network approval.
- Added #1 cross-platform diagnostic CI follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526155380
- Added #8 shared runtime-parameter guardrail follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526164326
- Re-checked `gh auth status` during manual MAT runtime smoke workflow work;
  it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #1 manual MAT runtime smoke follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526208154
- Re-checked `gh auth status` during manual MAT workflow guardrail work; it
  still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #1 MAT runtime workflow guardrail follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526244889
- Re-checked `gh auth status` during HTTP `/tools` catalog work; it still
  reports the default `yaravind` token is invalid. The first `gh issue comment`
  attempt hit a network error, then succeeded after explicit network approval.
- Added #8 HTTP tool catalog follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526254141
- Re-checked `gh auth status` during installed-command harness/preflight work;
  it still reports the default `yaravind` token is invalid. Initial
  `gh issue comment` attempts hit network errors, then succeeded after
  explicit network approval.
- Added #2 installed-command/preflight package follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526318572
- Added #8 installed-command harness follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526321538
- Re-checked `gh auth status` during heap evidence gap report-contract work; it
  still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #10 heap evidence gap report-contract follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/10#issuecomment-4526329036
- Re-checked `gh auth status` during release-readiness/package-smoke hardening;
  it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #2 release-readiness/package-smoke hardening follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526344122
- Re-checked `gh auth status` during reusable package-smoke and no-deps adapter
  discovery work; it still reports the default `yaravind` token is invalid.
  The first `gh issue comment` attempt hit a network error, then succeeded
  after explicit network approval.
- Added #2 reusable package-smoke/no-deps adapter-help follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526361524
- Re-checked `gh auth status` during custom recommendation pattern validation
  hardening; it still reports the default `yaravind` token is invalid. The
  first `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #3 custom recommendation pattern validation follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/3#issuecomment-4526365378
- Re-checked `gh auth status` during recommendation-pattern schema contract
  validation; it still reports the default `yaravind` token is invalid. The
  first `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #3 recommendation-pattern schema validation follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/3#issuecomment-4526368104
- Re-checked `gh auth status` during MAT first-run curl readiness work; it
  still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #1 MAT first-run curl readiness follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526376228
- Re-checked `gh auth status` during human runtime diagnostic output
  hardening; it still reports the default `yaravind` token is invalid. The
  first `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #1 human runtime diagnostic output follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526380445
- Re-checked `gh auth status` during managed MAT install readiness hardening;
  it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #1 managed MAT install readiness follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526390381
- Re-checked `gh auth status` during dump timestamp provenance schema
  hardening; it still reports the default `yaravind` token is invalid. The
  first `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #5 dump timestamp provenance contract follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/5#issuecomment-4526393765
- Re-checked `gh auth status` during shared dispatch/client error contract
  hardening; it still reports the default `yaravind` token is invalid. The
  first `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #8 shared dispatch/client error contract follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526401212
- Re-checked `gh auth status` during raw MAT page text report-contract guard
  work; it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #4 raw MAT page text report-contract guard follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/4#issuecomment-4526406215
- Re-checked `gh auth status` during MAT timeout process cleanup hardening; it
  still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after
  explicit network approval.
- Added #6 MAT timeout process cleanup follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/6#issuecomment-4526411630
- Refreshed the open GitHub issue list after the #6 update; `gh issue list`
  succeeded with network approval despite the stale `yaravind` auth warning.
- Viewed #7 before adding more work. The existing implementation already added
  `gc_parser.parse_and_summarize`; this pass added a manifest regression guard
  that imports every declared `skill.json` module/function pair.
- Added #7 manifest callable regression coverage follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/7#issuecomment-4526413744
- Re-checked `gh auth status` while selecting the next backlog item; it still
  reports the default `yaravind` token is invalid. `gh issue view` succeeded
  for existing issues #11, #12, and #14 with network approval.
- Added #12 structured MAT suspect parsing follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/12#issuecomment-4526424138
- Added contributor-cleanup regression coverage for #9, #11, and #14 in
  `tests/test_manifest.py`.
- Added #9 wrapper-script cleanup regression coverage follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/9#issuecomment-4526431387
- Added #11 GC pause regex regression coverage follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/11#issuecomment-4526431419
- Added #14 Makefile path portability regression coverage follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/14#issuecomment-4526431215
- Re-checked `gh auth status` during conftest cleanup regression work; it
  still reports the default `yaravind` token is invalid. `gh issue view`
  succeeded for existing issue #13 with network approval.
- Added #13 conftest cleanup regression coverage follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/13#issuecomment-4526535571
- Ran `make release-check` after the latest cleanup/parser guard work. It
  passed. Package smoke first hit the expected isolated-build network failure
  while trying to fetch `setuptools>=68`, then retried with
  `--no-build-isolation` and successfully installed
  `jvm-memory-leak-debugger-1.0.0`, verified installed CLI/API/MCP `--help`,
  and found bundled skill data from the temporary venv.
- Added #2 release-check/package-smoke evidence follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526548339
- Re-checked `gh auth status` during optional adapter evidence refresh; it
  still reports the default `yaravind` token is invalid.
- Refreshed optional adapter smoke evidence from the current worktree:
  `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`
  passed 6 HTTP adapter tests and skipped the MCP module because the local
  optional-dependency venv is Python 3.9 while the MCP extra is constrained to
  Python 3.10+.
- Added #8 optional adapter evidence refresh follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526550989
- Reconciled the PRD open decisions with ADR 0001: Windows MAT strategy is no
  longer listed as open. The PRD now records native Windows x86_64 Eclipse MAT
  ZIP support as the primary path, with WSL/custom MAT as fallback guidance.
- Added #1 Windows MAT strategy documentation follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526552975
- Re-checked `gh auth status` during release evidence snapshot work; it still
  reports the default `yaravind` token is invalid.
- Added #2 release evidence snapshot/package-data follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526557005
- Re-checked `gh auth status` during README release-evidence discoverability
  work; it still reports the default `yaravind` token is invalid.
- Added #2 README release-evidence discoverability follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526559006
- Re-checked `gh auth status` during dependency-free lint fallback work; it
  still reports the default `yaravind` token is invalid.
- Added #2 dependency-free contributor lint follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526572532
- Updated `docs/architecture/RELEASE_EVIDENCE.md` with the current
  dependency-free lint evidence: `make lint` passed from this worktree using the
  `py_compile` fallback across 13 Python files because `pyflakes` was not
  installed. Added a manifest guard so the release evidence keeps recording
  `make lint` and the `py_compile fallback`.
- Verification after the release-evidence lint update:
  - First focused manifest run failed because the evidence page used backticks
    around `py_compile`; adjusted wording so the drift guard can match the
    plain phrase.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 15
    tests.
  - `make validate-manifests` passed.
  - `make lint` passed with the `py_compile` fallback across 13 Python files.
  - `make test` passed: 93 selected tests, 2 optional adapter skips, and 3 full
    E2E tests deselected.
- Re-checked `gh auth status` during release-evidence lint issue work; it still
  reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 release-evidence lint follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526580061
- Added `lint` to `make release-check` so the one-command local release gate now
  runs lint before tests, manifest validation, contract validation, real-GC
  fixture tests, and package smoke. Updated
  `docs/architecture/RELEASE_READINESS_CHECKLIST.md`,
  `docs/architecture/RELEASE_EVIDENCE.md`, and the manifest regression guards
  to keep that gate documented.
- Verification after expanding `make release-check`:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 15
    tests.
  - `make validate-manifests` passed.
  - `make release-check` passed. It ran `make lint`, `make test`,
    `make validate-manifests`, `make validate-contracts`, `make test-e2e-gc`,
    and `make package-smoke`.
  - The lint step used the `py_compile` fallback across 13 Python files because
    `pyflakes` was not installed.
  - `make test` passed inside release-check: 93 selected tests, 2 optional
    adapter skips, and 3 full E2E tests deselected.
  - `make validate-contracts` passed inside release-check: 9 tests.
  - `make test-e2e-gc` passed inside release-check: 15 selected tests and 3
    full E2E tests deselected.
  - `make package-smoke` passed inside release-check. The first isolated PEP
    517 install hit the expected network restriction fetching build
    dependencies, then retried with `--no-build-isolation` and verified the
    installed CLI/API/MCP help commands plus bundled skill data.
- Re-checked `gh auth status` during release-gate hardening issue work; it
  still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 release-gate hardening follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526583916
- Refreshed the open GitHub issue list; all review issues #1 through #14 are
  still open, with #2 most recently updated by the release-gate evidence.
- Audited #10 and #3 state before the next local hardening step. #10 already
  has `severity_badge()` public and `build_report()` carries severity through
  `report.json`; #3 has a schema-backed custom recommendation pattern file
  format, examples, validation, and tests. The PRD still carried the pattern
  language as an open decision, so this pass resolved that stale handoff gap.
- Added ADR 0003,
  `docs/adr/0003-use-schema-backed-custom-recommendation-patterns.md`, to
  record the accepted custom pattern language: generic built-ins plus JSON
  extension files with regex evidence matchers and structured GC threshold
  matchers.
- Updated the maturity PRD resolved decisions and removed the stale custom
  recommendation-pattern open decision.
- Added ADR 0003 to `pyproject.toml`, `setup.py`, and
  `scripts/package_smoke.py` package-data checks so non-editable installs prove
  the pattern contract decision is bundled.
- Verification after ADR 0003:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py tests/test_reporter.py tests/test_schema_validator.py -v`
    passed, 38 tests.
  - `make validate-manifests` passed.
  - `make package-smoke` passed, verifying installed CLI/API/MCP help commands
    and bundled skill data including
    `docs/adr/0003-use-schema-backed-custom-recommendation-patterns.md`.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 16
    tests after the release evidence snapshot update.
- Re-checked `gh auth status` during recommendation-pattern ADR issue work; it
  still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #3 recommendation-pattern ADR follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/3#issuecomment-4526587642
- Re-audited the maturity PRD against current implementation evidence. M6
  contributor cleanup, M7 skill package completeness, and M8 packaging are now
  marked `implemented locally` with precise evidence, while M9 cross-platform
  CI and M10 optional adapter runtime evidence remain `partially implemented`
  because they still require live GitHub Actions / Python 3.10+ MCP proof.
- Added a manifest regression guard that keeps those PRD statuses from
  overclaiming CI readiness while preserving the local completion evidence for
  M6, M7, and M8.
- Verification after the PRD status refresh:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 17
    tests.
  - `make validate-manifests` passed.
  - `make release-check` passed. It ran lint, 95 selected fast tests with 2
    optional adapter skips and 3 full E2E tests deselected, manifest
    validation, 9 contract tests, 15 real-GC fixture tests, and package smoke.
  - Package smoke hit the expected isolated-build network restriction, retried
    with `--no-build-isolation`, and verified installed CLI/API/MCP help plus
    bundled skill data including ADR 0003.
- Re-checked `gh auth status` during PRD release-status issue work; it still
  reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 PRD release-status refresh follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526590960
- Added an explicit GitHub Actions evidence-capture runbook to
  `docs/architecture/RELEASE_READINESS_CHECKLIST.md` and linked it from
  `docs/architecture/RELEASE_EVIDENCE.md`. The runbook names the exact
  `gh run list`, `gh workflow run "MAT Runtime Smoke"`, `gh run watch`, and
  `gh run view --log-failed` commands to use after the branch is committed and
  pushed, and reminds maintainers to record successful `html_url` values.
- Added manifest regression coverage so the release checklist/evidence snapshot
  keep the GitHub Actions runbook commands and URL-capture requirement visible.
- Verification after the GitHub Actions evidence-capture runbook update:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 17
    tests.
  - `make validate-manifests` passed.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py tests/test_schema_validator.py -v`
    passed, 26 tests.
  - `make lint` passed with the `py_compile` fallback across 13 Python files.
- Re-checked `gh auth status` during GitHub Actions evidence-capture issue work;
  it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 GitHub Actions evidence-capture runbook follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526594606
- Tightened the GitHub Actions evidence-capture runbook after checking local
  `gh run list --help` and `gh run view --help`: the release checklist now
  uses `--json databaseId,status,conclusion,url` and captures final evidence
  with `gh run view <run-id> --json url`, matching the actual `gh` JSON field
  names.
- Updated the release evidence snapshot and manifest regression guard to use
  `url` rather than the stale `html_url` wording.
- Verification after the runbook URL-field correction:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 17
    tests.
  - `make validate-manifests` passed.
  - Basic stdlib workflow shape check passed for
    `.github/workflows/mat-runtime-smoke.yml` and
    `.github/workflows/test-skill.yml`.
- Re-checked `gh auth status` during GitHub Actions runbook correction issue
  work; it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 GitHub Actions runbook correction follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526598644
- Aligned README release evidence guidance with the checklist runbook: README
  now points maintainers to `docs/architecture/RELEASE_READINESS_CHECKLIST.md`
  and uses `gh workflow run "MAT Runtime Smoke"` with the repository and
  `codex/maturity-roadmap` ref instead of the older filename/placeholder
  command.
- Strengthened the `package-smoke` CI job's installed-bundle assertion to check
  `docs/architecture/RELEASE_EVIDENCE.md` and ADR 0003 in addition to the
  existing skill manifest, instructions, schema, preflight, harness examples,
  and release checklist.
- Added manifest regression coverage for README runbook discoverability and for
  CI/package-smoke checking the same installed release docs and ADR bundle files
  as `scripts/package_smoke.py`.
- Verification after README/CI package-check alignment:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 18
    tests.
  - `make validate-manifests` passed.
  - `make package-smoke` passed. The isolated PEP 517 install succeeded this
    time without needing the no-build-isolation fallback and verified installed
    CLI/API/MCP help plus bundled release docs and ADR 0003.
- Re-checked `gh auth status` during README/CI package-proof issue work; it
  still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 README and CI package-proof alignment follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526602776
- Found a local Python 3.12.13 runtime in the Codex workspace dependency
  bundle at
  `/Users/ayarram/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
- Created an isolated optional-adapter venv at
  `/private/tmp/jvm-memleak-py312-adapters` from that Python 3.12 runtime. The
  first dependency install attempt hit the expected sandboxed DNS/network
  failure while fetching build dependencies; the retry with network approval
  succeeded.
- Installed `-e '.[server,mcp]' pytest httpx` in the Python 3.12 venv and ran
  `PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters`.
  It passed all 8 adapter tests: 6 HTTP adapter tests and 2 MCP wrapper tests.
  This replaces the older local Python 3.9 evidence where MCP skipped.
- Updated `docs/architecture/RELEASE_READINESS_CHECKLIST.md`,
  `docs/architecture/RELEASE_EVIDENCE.md`, and the maturity PRD so optional
  HTTP/MCP adapters are marked ready locally from the Python 3.12 smoke, while
  hosted MCP proof still requires the Python 3.11 `adapter-smoke` job URL from
  `Test JVM Memory Leak Debugger Skill`.
- Verification after Python 3.12 optional-adapter evidence:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 18
    tests.
  - `PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters`
    passed, 8 tests with no MCP skip.
  - `make validate-manifests` passed.
- Re-checked `gh auth status` during Python 3.12 optional-adapter issue work;
  it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #8 Python 3.12 optional-adapter runtime evidence follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526608805
- Ran a fresh combined local validation snapshot after the Python 3.12 MCP
  evidence updates:
  - `make release-check` passed. It ran lint, 96 selected fast tests with 2
    optional adapter skips and 3 full E2E tests deselected, manifest
    validation, 9 contract tests, 15 real-GC fixture tests, and package smoke.
  - During package smoke, the first isolated PEP 517 install hit the expected
    network restriction while fetching build dependencies, then retried with
    `--no-build-isolation` and verified installed CLI/API/MCP help commands
    plus bundled release docs and ADR 0003.
  - `PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters`
    passed again, 8 tests with no MCP skip.
- Re-checked `gh auth status` during the fresh combined local validation issue
  work; it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 fresh combined local validation snapshot follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526611933
- Strengthened installed custom-recommendation-pattern bundle proof:
  `scripts/package_smoke.py` and the `package-smoke` GitHub Actions job now
  both verify `references/fix_patterns.md`, `examples/custom_patterns.json`,
  and `schemas/recommendation_patterns.json` are present in non-editable
  installs.
- Updated manifest regression coverage so local package smoke and CI
  package-smoke continue checking those custom-pattern assets.
- Verification after custom-pattern bundle smoke hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py tests/test_schema_validator.py -v`
    passed, 27 tests.
  - `make validate-manifests` passed.
  - `make package-smoke` passed. The isolated PEP 517 install succeeded and
    verified installed CLI/API/MCP help plus bundled custom-pattern schema,
    example, reference docs, release docs, and ADR 0003.
- Re-checked `gh auth status` during installed custom-pattern bundle proof issue
  work; it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #3 installed custom-pattern bundle proof follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/3#issuecomment-4526617551
- Improved `scripts/package_smoke.py` diagnostics for build-isolation/fallback
  troubleshooting. The smoke helper now prints the smoke venv Python and
  setuptools versions before install attempts and explicitly names the
  `--no-build-isolation` fallback when it is used.
- Verification after package-smoke diagnostic hardening:
  - Initial `make package-smoke` failed because the diagnostic snippet used
    `try:` after a semicolon in `python -c`; fixed the snippet to be proper
    multi-line Python.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile scripts/package_smoke.py`
    passed.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v` passed, 18
    tests.
  - `make package-smoke` passed. The diagnostic reported smoke Python 3.9.6
    and setuptools 58.0.4, the isolated PEP 517 install succeeded, and
    installed CLI/API/MCP help plus bundled release/custom-pattern assets were
    verified.
- Re-checked `gh auth status` during package-smoke diagnostic hardening issue
  work; it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 package-smoke diagnostic hardening follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526621957
- Ran `make release-check` after the package-smoke diagnostic hardening. It
  passed. It ran lint, 96 selected fast tests with 2 optional adapter skips and
  3 full E2E tests deselected, manifest validation, 9 contract tests, 15
  real-GC fixture tests, and package smoke.
- During package smoke inside release-check, the diagnostic printed smoke Python
  3.9.6 and setuptools 58.0.4. The isolated PEP 517 install hit the expected
  network restriction fetching build dependencies, then the smoke helper printed
  the explicit `--no-build-isolation` fallback message and verified installed
  CLI/API/MCP help plus bundled release/custom-pattern assets.
- `PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters`
  passed again after the package-smoke diagnostic hardening: 8 tests, including
  6 HTTP adapter tests and 2 MCP wrapper tests, with no MCP skip.
- Re-checked `gh auth status` during post-diagnostic release-check issue work;
  it still reports the default `yaravind` token is invalid. The first
  `gh issue comment` attempt hit a network error, then succeeded after network
  approval.
- Added #2 post-diagnostic release-check evidence follow-up note:
  https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526625449

## Current Implementation Pass

Completed scope:

- Maturity PRD under `docs/architecture`.
- Dependency manifests for optional hosted adapters.
- Small issue-backed fixes for #4, #6, and #7.
- Cross-platform MAT ZIP distribution selection for #1.
- Java 17 discovery without machine-specific fallback paths.
- Added artifact-free MAT runtime diagnostics for #1 through
  `--check-runtime`, plus `mat_home` forwarding for harnesses that manage an
  existing Eclipse MAT installation, including the MCP wrapper signatures.
- Added cross-platform CI smoke coverage for `mat_runner.runtime_diagnostics()`
  so Linux, macOS, and Windows jobs prove the host maps to a pinned MAT archive
  without downloading MAT.
- Runtime diagnostics now include `curl_available` and only claim first-run MAT
  readiness when MAT is already installed or curl can download the pinned MAT
  archive.
- The human `--check-runtime` output now also prints curl availability so
  operators do not need JSON mode to understand first-run MAT download
  readiness.
- Managed MAT installs now count as ready only when the Equinox launcher jar is
  present; a directory with `plugins/` but no launcher is reported as broken
  instead of ready.
- The memory leak report schema now requires dump timestamp provenance fields
  in `correlation`, so harnesses can rely on `dump_timestamp_source` and
  `dump_timestamp_warning`.
- Shared dispatch now rejects non-object tool parameters with a stable 422
  `ToolDispatchError`, and the HTTP adapter rejects malformed JSON bodies with
  a stable 400 `InvalidRequestBody` response.
- The memory leak report schema now rejects raw MAT page text fields in
  `heap_dump_analysis`, preventing oversized `raw_text_by_page` payloads from
  becoming durable report output.
- MAT timeout handling now attempts a bounded graceful stop and escalates to
  process kill before raising, while preserving the temp workspace cleanup and
  including the last captured MAT log lines in the timeout error.
- Manifest validation now proves each `skill.json` tool declaration points to
  an existing importable callable, preventing the original #7 function-name
  mismatch from returning.
- MAT report parsing now prefers structurally marked `problem-suspect`
  article/div/section regions when MAT HTML exposes them through class or id
  metadata, while keeping the flattened-text fallback for older or simpler
  reports.
- Manifest tests now guard against reintroducing deleted wrapper-script
  references in public docs, the duplicate `_RE_PAUSE_FULL_SUMMARY` regex, and
  hardcoded `../../target` Makefile artifact paths.
- The same contributor-cleanup guard now also verifies root/test `conftest.py`
  path shims stay deleted and `pytest.ini` remains the owner of
  `pythonpath = tools`.
- The release-readiness checklist and M10 PRD status now distinguish fresh
  local HTTP adapter evidence from MCP runtime evidence, which must come from
  a Python 3.10+ environment such as the Python 3.11 `adapter-smoke` CI job.
- The maturity PRD now records the Windows MAT strategy as a resolved decision
  backed by ADR 0001 instead of leaving it as an open question.
- Added `docs/architecture/RELEASE_EVIDENCE.md` as a durable evidence snapshot
  for the latest local proof, partial proof, and remaining external release
  blockers. It is linked from the release checklist and included in both
  `pyproject.toml` and `setup.py` package data.
- The README now points maintainers and harness operators to
  `docs/architecture/RELEASE_EVIDENCE.md` from the build/test release evidence
  section.
- Added `scripts/lint_or_compile.py` and updated `make lint` so pyflakes is
  used when available, but core contributors without optional lint
  dependencies still get a stdlib `py_compile` fallback. The fallback writes
  compiled files to a temporary directory to avoid macOS user-cache permission
  issues.
- Added a manual `MAT Runtime Smoke` GitHub Actions workflow for release
  readiness. It runs on Linux, macOS, and Windows with Java 17, then downloads,
  SHA-256 verifies, unpacks, and validates the pinned MAT distribution without
  needing a heap dump.
- Added `make check-runtime` for local no-download diagnostics and
  `make test-mat-runtime` for intentional local MAT download/unpack validation.
- Added a manifest/workflow guard test to keep the manual MAT runtime workflow
  manual-only, Java 17-backed, OS-matrixed, and free of heap dump requirements.
- ADR for pinned cross-platform MAT ZIP distributions.
- Pluggable generic/custom recommendation patterns for #3.
- HPROF header timestamp parsing, mtime fallback warnings, and explicit
  `--dump-time` override for #5.
- Shared tool registry and reusable full-report pipeline for #8.
- Severity is now part of `report.json` and `reporter.severity_badge()` is the
  public helper for #10.
- Removed redundant pytest conftest path shims and enabled `pythonpath = tools`
  in `pytest.ini` for #13.
- Parameterized Makefile artifact paths with `HPROF_PATH`, `GC_LOG_PATH`, and
  `OUTPUT_DIR` for #14.
- Removed redundant script entry points for #9: `scripts/generate_report.py`,
  `scripts/parse_gc_log.py`, and stale `scripts/run_mat.sh`. Kept
  `scripts/validate_artifacts.sh` because it is still a distinct local artifact
  sanity checker.
- Consolidated overlapping Full GC pause summary regex handling for #11.
- Made MAT suspect parsing fail explicitly when a page mentions `Problem
  Suspect` but no structured suspect can be extracted, and fixed parser section
  state handling for #12.
- Filled the skill-facing package content that was previously placeholder-only:
  `instructions/system_prompt.md`, `references/g1gc_phases.md`,
  `references/jvm_flags.md`, `references/mat_installation.md`,
  `examples/conversation_examples.md`, `assets/report_template.md`, and
  `assets/skill_card.md`.
- Updated `SKILL.md` to remove references to deleted script entry points and
  point MAT failures at the MAT runtime guide.
- Updated `.github/workflows/test-skill.yml` to run from this repo root instead
  of assuming a nested `skills/jvm-memory-leak-debugger` checkout, and to use
  the same Makefile verification gates contributors run locally.
- Added M7 Skill Package Completeness status and acceptance criteria to
  `docs/architecture/JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md`.
- Added concrete harness examples for Claude MCP, direct non-MCP function
  dispatch, and HTTP bridge hosting under `harnesses/`.
- Added an installed-command harness example for hosts that should launch
  `jvm-memory-leak-debugger`, `jvm-memory-leak-debugger-api`, and
  `jvm-memory-leak-debugger-mcp` instead of source-checkout paths.
- Added `references/harness_configuration.md` and linked it from `SKILL.md`.
- Added `references/preflight_checklist.md` with repeatable core, HTTP, MCP,
  runtime, and artifact-handling checks for new operators and harnesses.
- Aligned MAT analysis timeout configuration across `skill.json`, the CLI, MCP
  `generate_report`, and shared dispatch. `tests/test_dispatch.py` now verifies
  `timeout_s` reaches the shared pipeline.
- Added `tests/test_manifest.py` to keep the public skill manifest, dispatch
  registry, and direct harness tool list in sync.
- Extended manifest tests to guard shared runtime parameters across
  `skill.json`, CLI affordances, and MCP wrappers, including `mat_home`,
  `timeout_s`, `patterns_file`, and `dump_time`.
- Added Python packaging through `pyproject.toml`, exposing the
  `jvm-memory-leak-debugger` console script while keeping core dependencies
  empty and adapter dependencies in optional `mcp`, `server`, and `all` extras.
- Added a minimal `setup.py` shim for older editable-install flows and ADR 0002
  documenting the packaging decision.
- Added a GitHub Actions cross-platform smoke matrix for Linux, macOS, and
  Windows on Python 3.9 and 3.12. The smoke job verifies the manifest/dispatch
  contract, GC parser, editable install, installed console command, and packaged
  module imports without requiring a real heap dump or MAT download.
- Added M9 Cross-Platform CI Evidence to
  `docs/architecture/JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md`.
- Added optional FastAPI HTTP and MCP adapter smoke tests:
  `tests/test_server_adapter.py` and `tests/test_mcp_adapter.py`.
- Added an HTTP `GET /tools` catalog route backed by the shared dispatch
  registry so remote non-MCP hosts can discover POST routes and parameter
  schemas without importing Python modules.
- Added `make test-adapters` and a GitHub Actions `adapter-smoke` job that
  installs `.[server,mcp]` plus `pytest`/`httpx` on Python 3.11.
- Marked the `mcp` optional extra and `requirements-mcp.txt` with
  `python_version >= "3.10"` because current MCP SDK releases do not support
  Python 3.9. Core CLI support remains Python 3.9+.
- Added M10 Optional Adapter Runtime Evidence to
  `docs/architecture/JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md`.
- Split adapter implementations into packageable modules:
  `tools/server_adapter.py`, `tools/mcp_adapter.py`, and
  `tools/skill_resources.py`.
- Kept root `server.py` and `mcp_server.py` as source-checkout compatibility
  wrappers.
- Added installed adapter console scripts:
  `jvm-memory-leak-debugger-api` and `jvm-memory-leak-debugger-mcp`.
- Added safe `--help` handling for adapter launch commands and verified the
  installed HTTP adapter command locally.
- Added package data installation for the skill bundle under
  `share/jvm-memory-leak-debugger` so non-editable installs carry `skill.json`,
  instructions, references, schemas, examples, harness examples, assets, and
  ADRs.
- Updated `tools/skill_resources.py` to search source roots, current working
  directory, and the installed shared-data directory.
- Added `.gitignore` for generated Python caches, pytest caches, build/dist,
  egg-info, local virtualenvs, and local report outputs.
- Added a GitHub Actions `package-smoke` job that verifies a non-editable
  package install, CLI help, and installed skill bundle lookup from `/tmp`.
- Added dependency-free output contract validation through
  `tools/schema_validator.py`, `tests/test_schema_validator.py`, and
  `make validate-contracts`.
- Wired `make validate-contracts` into CI and added M11 Output Contract
  Validation to the maturity PRD.
- Wired full-report generation through the report contract before writing
  `report.json`; invalid generated reports now fail the pipeline before a
  machine-readable artifact is emitted.
- Added heap evidence visibility to the durable report contract. `report.json`
  now records MAT `analysis_status` and `error`, and `report.md` surfaces
  skipped or failed heap analysis instead of only showing an empty suspects
  list.
- Added `docs/architecture/RELEASE_READINESS_CHECKLIST.md` to keep release
  sign-off evidence tied to the goal, including the local gates, package smoke,
  adapter smoke, cross-platform workflow evidence, and manual MAT runtime smoke
  evidence that must be recorded before claiming completion.
- Added `make release-check` as the local no-MAT/no-heap release gate bundle.
- Added architecture checklist files to installed package data and tightened the
  package-smoke workflow assertion so non-editable installs prove the preflight,
  installed-command harness, and release checklist are bundled.
- Added `scripts/package_smoke.py` and `make package-smoke` to verify a fresh
  non-editable install can run the installed CLI, HTTP adapter command, MCP
  adapter command, and locate bundled skill resources from outside the source
  checkout.
- Included `make package-smoke` in `make release-check`.
- Hardened custom recommendation pattern loading so project-specific pattern
  files fail before report generation when they contain invalid regexes,
  duplicate ids, matcherless rules, unknown GC threshold names, or invalid GC
  threshold values.
- Extended the dependency-free schema validator for the recommendation pattern
  contract features used by `schemas/recommendation_patterns.json`: internal
  `#/definitions` refs, `oneOf`, `additionalProperties`, and `minimum`.

Still out of scope for this pass:

- Full live adapter smoke tests requiring optional `fastapi` or `mcp`
  dependencies.
- Actually running the live MAT runtime smoke on GitHub-hosted Linux/macOS/
  Windows or on this host; the current local `JAVA_HOME` points to Java 11.

## Current Verification Artifacts

- `/private/tmp/jvm-memleak-pattern-smoke/` contains the current CLI smoke test
  output generated from this worktree with `--patterns-file
  examples/custom_patterns.json`.
  - `report/report.json` verified that a matched recommendation records
    `pattern_source: builtin`.
  - `report/report.json` verified matcher internals such as `match_class` are
    not emitted in public recommendations.
- `/private/tmp/jvm-memleak-dumptime-smoke/` contains the current CLI smoke test
  output generated from this worktree with `--dump-time
  2026-05-22T16:18:36-04:00`.
  - `report/report.json` verified `dump_timestamp_source: override`.
  - `report/report.json` verified `dump_timestamp_warning: null`.
  - `report/report.json` verified `dump_phase: during_full_gc_storm`.
- `/private/tmp/jvm-memleak-make-example/` contains the current `make
  run-example` smoke output generated with caller-provided `HPROF_PATH`,
  `GC_LOG_PATH`, and `OUTPUT_DIR`.
- `/private/tmp/jvm-memleak-packaging-venv/` contains the packaging smoke-test
  virtualenv used to verify editable install and the installed
  `jvm-memory-leak-debugger` console command.
  - Initial `pip install -e . --no-deps` failed before pip upgrade because pip
    21.2.4 did not support the modern editable path cleanly and build
    dependency download was initially blocked by the network sandbox.
  - After approved network access and `python -m pip install --upgrade pip`,
    `pip install -e . --no-deps` passed.
  - The same venv was later used to verify `.[server]` plus `httpx`/`pytest`
    adapter tests on Python 3.9: HTTP tests passed and MCP tests skipped because
    MCP requires Python 3.10+.
- `/private/tmp/jvm-memleak-wheel-venv/` contains the non-editable install
  smoke-test virtualenv used to verify packaged skill bundle data outside the
  source checkout.
  - `python -m pip install . --no-deps` passed after upgrading pip.
  - A later `--no-build-isolation` package smoke initially built
    `UNKNOWN-0.0.0` from the old empty `setup.py` shim. `setup.py` now carries
    the legacy install metadata and the rerun built
    `jvm-memory-leak-debugger-1.0.0`.
  - From `/private/tmp`, `skill_resources.find_repo_file("skill.json")` resolved
    to the venv's `share/jvm-memory-leak-debugger/skill.json`.
  - Installed shared data check verified `skill.json`,
    `instructions/system_prompt.md`, `references/preflight_checklist.md`,
    `schemas/memory_leak_report.json`,
    `harnesses/installed_commands.example.json`, and
    `docs/architecture/RELEASE_READINESS_CHECKLIST.md`.

## Verification

- `make test`: passed, 29 selected tests and 3 full E2E tests deselected.
- `make validate-manifests`: passed.
- `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
  deselected.
- Later verification after MAT portability work:
  - `PYTHONPATH=tools python3 -m pytest tests/test_mat_runner.py -v`: passed,
    13 tests.
  - `make test`: passed, 40 selected tests and 3 full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `make lint`: not run successfully because `pyflakes` is not installed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed.
- Later verification after recommendation-pattern work:
  - `PYTHONPATH=tools python3 -m pytest tests/test_reporter.py -v`: passed,
    8 tests.
  - `make test`: passed, 42 selected tests and 3 full E2E tests deselected.
  - `make validate-manifests`: passed, including
    `schemas/recommendation_patterns.json`.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py` and `mcp_server.py`.
- Later verification after MAT parser explicit-failure work:
  - `PYTHONPATH=tools python3 -m pytest tests/test_mat_runner.py -v`: passed,
    15 tests.
  - `make test`: passed, 54 selected tests and 3 full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py` and `mcp_server.py`.
- Later verification after skill package content and CI root-path work:
  - `make validate-manifests`: passed, including non-empty skill package docs
    and stale deleted-script reference checks.
  - `make test`: passed, 54 selected tests and 3 full E2E tests deselected.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py` and `mcp_server.py`.
- Later verification after harness-contract work:
  - `make validate-manifests`: passed, including harness example JSON parsing.
  - `python3 -m pytest tests/test_manifest.py tests/test_dispatch.py -v`:
    passed, 10 tests.
  - `python3 tools/debug_memory_leak.py --help`: passed and showed
    `--timeout-s`.
  - `make test`: passed, 58 selected tests and 3 full E2E tests deselected.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py` and `mcp_server.py`.
- Later verification after packaging/installability work:
  - `make validate-manifests`: passed, including `pyproject.toml` and
    `setup.py` checks.
  - `python3 -m pytest tests/test_manifest.py -v`: passed, 5 tests.
  - `/private/tmp/jvm-memleak-packaging-venv/bin/python -m pip install -e . --no-deps`:
    passed after upgrading pip in the venv.
  - `/private/tmp/jvm-memleak-packaging-venv/bin/jvm-memory-leak-debugger --help`:
    passed and showed the installed console command options.
  - `/private/tmp/jvm-memleak-packaging-venv/bin/python -c "import dispatch, debug_memory_leak, gc_parser, mat_runner, pipeline; ..."`:
    passed and showed all public dispatch tools.
  - `make test`: passed, 60 selected tests and 3 full E2E tests deselected.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
  - Follow-up after aligning the MCP wrapper with `mat_home`:
    `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py tests/test_dispatch.py -v`
    passed, 14 tests; `make test` and `make validate-manifests` also passed
    again.
- Later verification after cross-platform runtime diagnostic CI guardrails:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed, 8
    tests.
  - `PYTHONPATH=tools python3 -c "import mat_runner; s=mat_runner.runtime_diagnostics(); assert s['platform_supported'], s; assert s['can_auto_install_mat'], s; print(s['platform_key'], s['ready_for_analysis'])"`:
    passed and printed `macos-aarch64 False` on the current host.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `make test`: passed, 69 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make validate-contracts`: passed, 4 tests.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after adding the manual MAT runtime smoke workflow:
  - `ruby -e 'require "yaml"; %w[test-skill.yml mat-runtime-smoke.yml].each { |f| YAML.load_file(".github/workflows/#{f}"); puts "#{f} OK" }'`:
    passed.
  - `make help`: passed and listed `check-runtime` plus `test-mat-runtime`.
  - `make check-runtime`: exercised the local diagnostic and exited nonzero
    because this host's `JAVA_HOME` points to Java 11. Output still reported
    supported `macos-aarch64`, the pinned MAT archive URL/SHA, and
    `can_auto_install_mat: true`.
  - `make test`: passed, 69 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make validate-contracts`: passed, 4 tests.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after adding the manual MAT workflow guard test:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed, 9
    tests.
  - `ruby -e 'require "yaml"; %w[test-skill.yml mat-runtime-smoke.yml].each { |f| YAML.load_file(".github/workflows/#{f}"); puts "#{f} OK" }'`:
    passed.
  - `make test`: passed, 70 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make validate-contracts`: passed, 4 tests.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after adding the HTTP `/tools` catalog:
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 4 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/server_adapter.py server.py`:
    passed.
  - `make test`: passed, 70 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make validate-contracts`: passed, 4 tests.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after adding installed-command harness and preflight docs:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed, 9
    tests.
  - `make validate-manifests`: passed, including the new preflight reference
    and installed-command harness JSON.
  - `python3 -m json.tool harnesses/installed_commands.example.json`: passed.
  - `make test`: passed, 70 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-contracts`: passed, 4 tests.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 4 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after heap-analysis status/error report contract work:
  - `PYTHONPATH=tools python3 -m pytest tests/test_reporter.py tests/test_dispatch.py tests/test_schema_validator.py -v`:
    passed, 21 tests.
  - `make validate-contracts`: passed, 4 tests.
  - CLI smoke generated `/private/tmp/jvm-memleak-evidence-gap-smoke/report`
    from the current worktree with `--skip-mat` and verified:
    `report.json` has `heap_dump_analysis.analysis_status: skipped`,
    `report.json` includes a MAT skipped error, and `report.md` includes
    `MAT analysis status` plus `Heap evidence gap`.
  - `make test`: passed, 71 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 4 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after cross-platform CI matrix work:
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py tests/test_dispatch.py tests/test_gc_parser.py -v`:
    passed, 18 tests.
  - `make validate-manifests`: passed.
  - `/private/tmp/jvm-memleak-packaging-venv/bin/jvm-memory-leak-debugger --help`:
    passed.
  - `make test`: passed, 60 selected tests and 3 full E2E tests deselected.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after optional adapter smoke work:
  - `make test`: passed, 60 selected tests, 2 optional adapter tests skipped in
    the core-only Python 3.9 environment, and 3 full E2E tests deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP adapter module skipped because local
    venv is Python 3.9.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after adapter packaging work:
  - `make validate-manifests`: passed.
  - `PYTHONPATH=tools:. python3 -m pytest tests/test_manifest.py tests/test_server_adapter.py tests/test_mcp_adapter.py -v`:
    passed, 5 manifest tests and 2 optional adapter modules skipped in the
    core-only Python 3.9 environment.
  - `/private/tmp/jvm-memleak-packaging-venv/bin/jvm-memory-leak-debugger-api --help`:
    passed.
  - `/private/tmp/jvm-memleak-packaging-venv/bin/python -c "import server_adapter, skill_resources; ..."`:
    passed.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `make test`: passed, 60 selected tests, 2 optional adapter skips, and 3 full
    E2E tests deselected.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after package-data work:
  - `make validate-manifests`: passed.
  - `PYTHONPATH=tools:. python3 -m pytest tests/test_manifest.py -v`: passed,
    6 tests.
  - `/private/tmp/jvm-memleak-wheel-venv/bin/python -m pip install . --no-deps`:
    passed for a non-editable wheel install.
  - From `/private/tmp`,
    `/private/tmp/jvm-memleak-wheel-venv/bin/python -c "import skill_resources; ..."`:
    passed and found installed `skill.json` and `instructions/system_prompt.md`
    under `share/jvm-memory-leak-debugger`.
  - Installed shared data existence check for `skill.json`,
    `schemas/memory_leak_report.json`, and
    `harnesses/direct_function_dispatch.example.json`: passed.
  - `make test`: passed, 61 selected tests, 2 optional adapter skips, and 3 full
    E2E tests deselected.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after package-smoke CI work:
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `make validate-manifests`: passed.
  - `make test`: passed, 61 selected tests, 2 optional adapter skips, and 3 full
    E2E tests deselected.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - From `/private/tmp`,
    `/private/tmp/jvm-memleak-wheel-venv/bin/python -c "import skill_resources; ..."`:
    passed and resolved installed `share/jvm-memory-leak-debugger/skill.json`.
  - Installed shared data existence check for `skill.json`,
    `instructions/system_prompt.md`, `schemas/memory_leak_report.json`, and
    `harnesses/direct_function_dispatch.example.json`: passed.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after output-contract validation work:
  - `make validate-contracts`: passed, 3 tests.
  - `PYTHONPATH=tools python3 -m pytest tests/test_schema_validator.py -v`:
    passed, 3 tests.
  - `make test`: passed, 64 selected tests, 2 optional adapter skips, and 3 full
    E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after pipeline report-contract enforcement:
  - `PYTHONPATH=tools python3 -m pytest tests/test_schema_validator.py tests/test_dispatch.py -v`:
    passed, 12 tests, including the invalid-report path that confirms
    `report.json` is not written when contract validation fails.
  - `make validate-contracts`: passed, 4 tests.
  - `make test`: passed, 66 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after MAT runtime diagnostics and `mat_home` wiring:
  - `PYTHONPATH=tools python3 -m pytest tests/test_mat_runner.py tests/test_dispatch.py tests/test_manifest.py -v`:
    passed, 30 tests.
  - `python3 tools/debug_memory_leak.py --help`: passed and showed
    `--check-runtime` plus `--mat-home`.
  - `/private/tmp/jvm-memleak-packaging-venv/bin/jvm-memory-leak-debugger --help`:
    passed and showed `--check-runtime` plus `--mat-home`.
  - `python3 tools/debug_memory_leak.py --check-runtime --json`: exercised the
    diagnostic path on this macOS ARM64 host and exited 1 because local
    `JAVA_HOME` points to Java 11; output still reported supported
    `macos-aarch64`, the pinned MAT archive, and `can_auto_install_mat: true`.
  - `make test`: passed, 67 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 3 HTTP adapter tests and 1 MCP module skipped because local venv is
    Python 3.9.
  - `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/test-skill.yml"); puts "workflow yaml OK"'`:
    passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py`, `mcp_server.py`, and `setup.py`.
- Later verification after script/parser cleanup:
  - `rg "scripts/(generate_report|parse_gc_log|run_mat)|generate_report.py|parse_gc_log.py|run_mat.sh|_RE_PAUSE_FULL_SUMMARY" ...`:
    no matches.
  - `PYTHONPATH=tools python3 -m pytest tests/test_gc_parser.py tests/test_e2e_real_gc.py -v -m "not e2e_full"`:
    passed, 21 selected tests and 3 full E2E tests deselected.
  - `find scripts -maxdepth 2 -type f -print`: only
    `scripts/validate_artifacts.sh` remains.
  - `make test`: passed, 52 selected tests and 3 full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py` and `mcp_server.py`.
- Later verification after contributor cleanup work:
  - `python3 -m pytest tests/test_reporter.py tests/test_dispatch.py -v`:
    passed, 14 tests, proving pytest imports work through `pytest.ini`.
  - `make run-example`: failed fast as expected without `HPROF_PATH`.
  - `make run-example HPROF_PATH=/private/tmp/jvm-memleak-make-example/dump.hprof GC_LOG_PATH=tests/fixtures/gc-16615.log OUTPUT_DIR=/private/tmp/jvm-memleak-make-example/report`:
    passed.
  - `python3 -m pytest tests/test_gc_parser.py -v`: passed, 6 tests, without
    relying on deleted conftest files.
  - Final rerun `make test`: passed, 52 selected tests and 3 full E2E tests
    deselected.
  - `make validate-manifests`: passed.
  - Final rerun `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py` and `mcp_server.py`.
  - CLI smoke with `--patterns-file examples/custom_patterns.json`: passed and
    wrote `/private/tmp/jvm-memleak-pattern-smoke/report/report.json`.
- Later verification after dump timestamp correlation work:
  - `PYTHONPATH=tools python3 -m pytest tests/test_correlator.py -v`: passed,
    4 tests.
  - `make test`: passed, 46 selected tests and 3 full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - CLI smoke with `--dump-time 2026-05-22T16:18:36-04:00`: passed and wrote
    `/private/tmp/jvm-memleak-dumptime-smoke/report/report.json`.
- Later verification after shared dispatch registry work:
  - `PYTHONPATH=tools python3 -m pytest tests/test_dispatch.py -v`: passed,
    6 tests.
  - `make test`: passed, 52 selected tests and 3 full E2E tests deselected.
  - `make validate-manifests`: passed.
  - `make test-e2e-gc`: passed, 15 selected tests and 3 full E2E tests
    deselected.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile ...`:
    passed for tools plus `server.py` and `mcp_server.py`.
- Later verification after release-readiness and package-smoke hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    10 tests.
  - `make validate-manifests`: passed.
  - `make validate-contracts`: passed, 4 tests.
  - `/private/tmp/jvm-memleak-wheel-venv/bin/python -m pip install . --no-deps --no-build-isolation`:
    passed after installing `wheel`; built
    `jvm-memory-leak-debugger-1.0.0`.
  - From `/private/tmp`,
    `/private/tmp/jvm-memleak-wheel-venv/bin/jvm-memory-leak-debugger --help`:
    passed.
  - From `/private/tmp`, installed package data checks passed for the preflight
    checklist, installed-command harness, and release readiness checklist.
  - `make release-check`: passed; it ran `make test`,
    `make validate-manifests`, `make validate-contracts`, and
    `make test-e2e-gc`.
- Later verification after reusable package-smoke target and adapter no-deps
  help hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py tests/test_server_adapter.py tests/test_mcp_adapter.py -v`:
    passed, 11 manifest tests and 2 optional adapter modules skipped in the
    local core-only Python 3.9 environment.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile scripts/package_smoke.py tools/server_adapter.py tools/mcp_adapter.py`:
    passed.
  - `make package-smoke`: passed. It built and installed
    `jvm-memory-leak-debugger-1.0.0` in a temporary venv, then verified
    `jvm-memory-leak-debugger --help`, `jvm-memory-leak-debugger-api --help`,
    `jvm-memory-leak-debugger-mcp --help`, and installed bundled skill data
    from outside the source checkout.
  - `make release-check`: passed. Local package smoke first hit the expected
    network restriction while installing isolated build dependencies, then the
    new fallback retried with local build backend packages and passed.
- Later verification after custom recommendation pattern validation hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_reporter.py -v`: passed,
    13 tests, including invalid regex, matcherless pattern, invalid GC
    threshold, and duplicate built-in id rejection.
  - `make validate-manifests`: passed, including
    `schemas/recommendation_patterns.json`.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/reporter.py`:
    passed.
  - `make test`: passed, 77 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after recommendation-pattern schema contract validation:
  - `PYTHONPATH=tools python3 -m pytest tests/test_schema_validator.py -v`:
    passed, 7 tests, including checked-in custom pattern example validation,
    unknown GC field rejection, and negative threshold rejection.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/schema_validator.py`:
    passed.
  - `make validate-manifests`: passed.
  - `make test`: passed, 80 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after MAT first-run curl readiness diagnostics:
  - `PYTHONPATH=tools python3 -m pytest tests/test_mat_runner.py tests/test_manifest.py -v`:
    passed, 29 tests.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/mat_runner.py`:
    passed.
  - `make validate-manifests`: passed.
  - `PYTHONPATH=tools python3 tools/debug_memory_leak.py --check-runtime --json`:
    exercised the user-facing diagnostic on this macOS ARM64 host. It reported
    `curl_available: true`, `can_auto_install_mat: true`, supported
    `macos-aarch64`, and `ready_for_analysis: false` because local `JAVA_HOME`
    points to Java 11.
- Later verification after human runtime diagnostic output hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_cli.py tests/test_manifest.py -v`:
    passed, 12 tests.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/debug_memory_leak.py`:
    passed.
  - `PYTHONPATH=tools python3 tools/debug_memory_leak.py --check-runtime`:
    exercised human output on this macOS ARM64 host. It printed `curl: True`,
    `Auto-install: True`, and `Ready: False` with the Java 11 `JAVA_HOME`
    issue.
  - `make test`: passed, 83 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after managed MAT install readiness hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_mat_runner.py -v`: passed,
    19 tests, including the broken existing MAT install case with no Equinox
    launcher.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/mat_runner.py`:
    passed.
  - `PYTHONPATH=tools python3 tools/debug_memory_leak.py --check-runtime --json`:
    exercised the user-facing diagnostic on this macOS ARM64 host. It still
    reports supported `macos-aarch64`, `curl_available: true`,
    `can_auto_install_mat: true`, and `ready_for_analysis: false` because
    local `JAVA_HOME` points to Java 11.
  - `make test`: passed, 84 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after dump timestamp provenance schema hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_schema_validator.py -v`:
    passed, 8 tests, including the negative contract check that report
    validation fails when `dump_timestamp_source` is missing.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/schema_validator.py`:
    passed.
  - `make validate-manifests`: passed.
  - `make test`: passed, 85 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after shared dispatch/client error contract hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_dispatch.py -v`: passed,
    9 tests, including non-object parameter rejection.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/dispatch.py tools/server_adapter.py`:
    passed.
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed, 6 HTTP adapter tests and 1 MCP module skipped because the local
    adapter venv is Python 3.9.
  - `make test`: passed, 86 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after raw MAT page text report-contract guard:
  - `PYTHONPATH=tools python3 -m pytest tests/test_schema_validator.py -v`:
    passed, 9 tests, including rejection of
    `heap_dump_analysis.raw_text_by_page`.
  - `make validate-manifests`: passed.
  - `make test`: passed, 87 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after MAT timeout process cleanup hardening:
  - `PYTHONPATH=tools python3 -m pytest tests/test_mat_runner.py -v`: passed,
    20 tests, including the timeout path that terminates, escalates to kill,
    includes captured MAT log output, and cleans the workspace.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/mat_runner.py`:
    passed.
  - `make test`: passed, 88 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
- Later verification after manifest callable regression guard:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    12 tests, including importability of every declared `skill.json`
    module/function pair.
  - `make validate-manifests`: passed.
  - `make test`: passed, 89 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after structured MAT problem-suspect extraction:
  - `PYTHONPATH=tools python3 -m pytest tests/test_mat_runner.py -v`: passed,
    21 tests, including a structural `problem-suspect` region case where page
    navigation/outside text is ignored for suspect stack extraction.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile tools/mat_runner.py`:
    passed.
  - `make test`: passed, 90 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make validate-manifests`: passed.
- Later verification after contributor-cleanup regression guards:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    13 tests, including guards for no stale deleted wrapper references in
    public docs, no duplicate Full-GC pause regex, and no hardcoded
    `../../target` paths in `Makefile`.
  - `make validate-manifests`: passed.
  - `make test`: passed, 91 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after conftest cleanup regression guard:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    13 tests, including checks that root `conftest.py` and
    `tests/conftest.py` remain absent while `pytest.ini` owns
    `pythonpath = tools`.
  - `make validate-manifests`: passed.
  - `make test`: passed, 91 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later release gate bundle after the latest hardening work:
  - `make release-check`: passed. It ran `make test`,
    `make validate-manifests`, `make validate-contracts`,
    `make test-e2e-gc`, and `make package-smoke`.
  - During `make package-smoke`, the first isolated PEP 517 install attempted
    to download build dependencies and failed under network restrictions. The
    smoke script's fallback retried with local build backend packages and
    passed, building/installing `jvm-memory-leak-debugger-1.0.0`, verifying
    installed CLI/API/MCP help commands, and resolving installed bundle data.
- Later optional adapter evidence refresh:
  - `PYTHON=/private/tmp/jvm-memleak-packaging-venv/bin/python make test-adapters`:
    passed 6 HTTP adapter tests and skipped 1 MCP adapter module because the
    local optional-dependency venv is Python 3.9.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    13 tests, including the release-checklist caveat that MCP requires
    Python 3.10+ evidence.
  - `make validate-manifests`: passed.
  - `make test`: passed, 91 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after PRD Windows MAT decision reconciliation:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    14 tests, including the guard that the Windows MAT strategy is recorded as
    resolved through ADR 0001.
  - `make validate-manifests`: passed.
  - `make test`: passed, 92 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after release evidence snapshot packaging:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    14 tests, including checks that `RELEASE_EVIDENCE.md` is packaged and
    records the remaining cross-platform/MAT/MCP proof requirements.
  - `make validate-manifests`: passed.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile scripts/package_smoke.py`:
    passed.
  - `make test`: passed, 92 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make package-smoke`: passed, building and installing
    `jvm-memory-leak-debugger-1.0.0`, verifying installed CLI/API/MCP help
    commands, and confirming bundled `docs/architecture/RELEASE_EVIDENCE.md`
    exists in the temporary venv.
- Later verification after README release-evidence discoverability:
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    14 tests, including the guard that README links to
    `docs/architecture/RELEASE_EVIDENCE.md`.
  - `make validate-manifests`: passed.
  - `make test`: passed, 92 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
- Later verification after dependency-free lint fallback:
  - Initial `make lint` failed because `pyflakes` was not installed.
  - After adding `scripts/lint_or_compile.py`, `make lint` passed with the
    stdlib `py_compile` fallback across 13 Python files.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    15 tests, including the lint fallback guard.
  - `PYTHONPYCACHEPREFIX=/private/tmp/jvm-memory-leak-debugger-pycache python3 -m py_compile scripts/lint_or_compile.py`:
    passed.
  - `make validate-manifests`: passed.
  - `make test`: passed, 93 selected tests, 2 optional adapter skips, and 3
    full E2E tests deselected.
  - `make package-smoke`: passed.
- Later Python 3.12 optional adapter refresh after the post-diagnostic
  release-check snapshot, 2026-05-23 17:56 EDT:
  - `PYTHON=/private/tmp/jvm-memleak-py312-adapters/bin/python make test-adapters`:
    passed 8 tests on Python 3.12.13, including 6 HTTP adapter tests and 2 MCP
    wrapper tests with optional MCP dependencies installed.
- GitHub external evidence check, 2026-05-23 17:58 EDT:
  - `gh auth status` still reports the default `yaravind` token is invalid.
  - `gh issue list --repo yaravind/jvm-memory-leak-debugger --state open
    --limit 50 --json number,title,labels,updatedAt,url` succeeded and showed
    issues #1 through #14 remain open with priority labels.
  - `gh run list --repo yaravind/jvm-memory-leak-debugger --workflow "Test JVM
    Memory Leak Debugger Skill" --branch codex/maturity-roadmap --limit 3
    --json databaseId,status,conclusion,url,headBranch,createdAt` succeeded
    with `[]`, so there is no live run evidence for this branch yet.
  - `gh run list --repo yaravind/jvm-memory-leak-debugger --workflow "MAT
    Runtime Smoke" --branch codex/maturity-roadmap --limit 3 --json
    databaseId,status,conclusion,url,headBranch,createdAt` returned
    `could not find any workflows named MAT Runtime Smoke`, which matches the
    current uncommitted/unpushed workflow file.
  - `git branch -vv` shows `codex/maturity-roadmap` has no upstream while
    `main` tracks `origin/main`; external CI proof therefore requires explicit
    commit/push authorization first.
  - Updated `docs/architecture/RELEASE_EVIDENCE.md` to record the no-run and
    missing-remote-workflow checks so the current absence of external evidence
    is explicit.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    18 tests.
- Later harness portability hardening, 2026-05-23 17:59 EDT:
  - Added `harnesses/codex_skill.example.json` for Codex-style local direct
    dispatcher configuration.
  - Added `harnesses/copilot_extension.example.json` for GitHub Copilot
    Extension-style HTTPS tool routing through `/skill.json`, `/health`,
    `/tools`, and `/tools/{tool_name}`.
  - Updated `references/harness_configuration.md`, `README.md`, `SKILL.md`,
    `pyproject.toml`, `setup.py`, package smoke, CI package-data smoke, and
    manifest tests so the new harness examples are documented, validated, and
    shipped in installed bundles.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    18 tests.
  - `make validate-manifests`: passed.
  - `make package-smoke`: passed. The non-editable install verified CLI/API/MCP
    help and confirmed installed bundle files include
    `harnesses/codex_skill.example.json` and
    `harnesses/copilot_extension.example.json`.
  - Re-checked `gh auth status`; it still reports the default `yaravind` token
    is invalid. The first issue comment attempt hit a network error, then
    succeeded after network approval.
  - Added #8 Codex/Copilot harness portability follow-up note:
    https://github.com/yaravind/jvm-memory-leak-debugger/issues/8#issuecomment-4526635446
- Later full local release gate after Codex/Copilot harness packaging,
  2026-05-23 18:01 EDT:
  - `make release-check`: passed from the current worktree.
  - It ran `make lint`, `make test`, `make validate-manifests`,
    `make validate-contracts`, `make test-e2e-gc`, and `make package-smoke`.
  - `make lint` used the dependency-free `py_compile` fallback across 13
    Python files because `pyflakes` was not installed.
  - `make test`: passed 96 selected tests, skipped 2 optional adapter modules,
    and deselected 3 full E2E tests.
  - `make validate-contracts`: passed 9 schema/contract tests.
  - `make test-e2e-gc`: passed 15 real-GC fixture tests and deselected 3 full
    E2E tests.
  - `make package-smoke`: first hit the expected isolated PEP 517 network
    restriction while fetching build dependencies, then retried with
    `--no-build-isolation` and passed. The smoke verified CLI/API/MCP `--help`
    commands and installed bundle data including
    `harnesses/codex_skill.example.json` and
    `harnesses/copilot_extension.example.json`.
  - Updated `docs/architecture/RELEASE_EVIDENCE.md` with the fresh
    release-check result and reran `PYTHONPATH=tools python3 -m pytest
    tests/test_manifest.py -v`: passed, 18 tests.
- Later full heap replay release-policy decision, 2026-05-23 18:03 EDT:
  - Added
    `docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md`,
    which records that full `.hprof` replay remains supported through
    `make test-e2e-full` and conditional CI, but is external release evidence
    rather than a required default release gate unless a maintained trusted heap
    artifact is available.
  - Updated `docs/architecture/RELEASE_EVIDENCE.md` to move full heap replay
    out of the partially proven missing-evidence table and into local policy
    evidence.
  - Updated `docs/architecture/RELEASE_READINESS_CHECKLIST.md` and
    `docs/architecture/JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md` to reference
    ADR 0004.
  - Wired ADR 0004 into `pyproject.toml`, `setup.py`, CI package-data smoke,
    package smoke, and manifest tests so installed bundles carry the policy.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    19 tests.
  - `make validate-manifests`: passed.
  - `make package-smoke`: passed and confirmed installed bundle data includes
    `docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md`.
  - Re-checked `gh auth status`; it still reports the default `yaravind` token
    is invalid. The first issue comment attempt hit a network error, then
    succeeded after network approval.
  - Added #1 full heap replay release-policy follow-up note:
    https://github.com/yaravind/jvm-memory-leak-debugger/issues/1#issuecomment-4526641180
- Later full local release gate after ADR 0004, 2026-05-23 18:04 EDT:
  - `make release-check`: passed from the current worktree.
  - It ran `make lint`, `make test`, `make validate-manifests`,
    `make validate-contracts`, `make test-e2e-gc`, and `make package-smoke`.
  - `make lint` used the dependency-free `py_compile` fallback across 13
    Python files because `pyflakes` was not installed.
  - `make test`: passed 97 selected tests, skipped 2 optional adapter modules,
    and deselected 3 full E2E tests.
  - `make validate-contracts`: passed 9 schema/contract tests.
  - `make test-e2e-gc`: passed 15 real-GC fixture tests and deselected 3 full
    E2E tests.
  - `make package-smoke`: first hit the expected isolated PEP 517 network
    restriction while fetching build dependencies, then retried with
    `--no-build-isolation` and passed. The smoke verified CLI/API/MCP `--help`
    commands and installed bundle data including ADR 0004.
  - Updated `docs/architecture/RELEASE_EVIDENCE.md` with the fresh
    release-check result and reran `PYTHONPATH=tools python3 -m pytest
    tests/test_manifest.py -v`: passed, 19 tests.
  - Re-checked external workflow state after the issue-resolution release gate:
    `gh auth status` still reports the default `yaravind` token is invalid.
    `gh run list` for `Test JVM Memory Leak Debugger Skill` on branch
    `codex/maturity-roadmap` succeeded with `[]`. `gh run list` for
    `MAT Runtime Smoke` still returned `could not find any workflows named MAT
    Runtime Smoke`, matching the uncommitted/unpushed workflow file.
- Final blocked-audit check, 2026-05-23 18:11 EDT:
  - Current local evidence docs (`MATURITY_COMPLETION_AUDIT.md`,
    `RELEASE_EVIDENCE.md`, and `ISSUE_RESOLUTION_MATRIX.md`) show all local
    maturity requirements are ready locally and that the remaining completion
    requirements are external workflow proofs after commit/push.
  - Re-checked `gh auth status`; it still reports the default `yaravind` token
    is invalid.
  - `gh run list` for `Test JVM Memory Leak Debugger Skill` on branch
    `codex/maturity-roadmap` still succeeded with `[]`.
  - `gh run list` for `MAT Runtime Smoke` still returned `could not find any
    workflows named MAT Runtime Smoke`.
  - The branch remains unpushed and the workflow remains unavailable remotely.
    Because repo rules prohibit staging/committing/pushing without explicit
    user authorization, no further meaningful local progress remains before
    explicit commit/push authorization or an external-state change.
- Commit/push authorization, 2026-05-23:
  - User explicitly authorized staging, committing, and pushing with the
    instruction: "go ahead with the staging, committing and pushing. make sure
    to refer correct GitHub issues".
  - Proceeding with a comprehensive issue-linked maturity commit on
    `codex/maturity-roadmap` because the runtime, packaging, CI, docs, and
    contract changes are tightly coupled and have been verified together.
  - Re-checked external workflow state after the completion-audit release
    gate: `gh auth status` still reports the default `yaravind` token is
    invalid. `gh run list` for `Test JVM Memory Leak Debugger Skill` on branch
    `codex/maturity-roadmap` succeeded with `[]`. `gh run list` for
    `MAT Runtime Smoke` still returned `could not find any workflows named MAT
    Runtime Smoke`, matching the uncommitted/unpushed workflow file.
- Later issue-resolution evidence matrix, 2026-05-23 18:09 EDT:
  - Added `docs/architecture/ISSUE_RESOLUTION_MATRIX.md`, mapping GitHub
    issues #1 through #14 to local implementation evidence and remaining
    external proof.
  - Linked the matrix from the PRD, maturity completion audit, and release
    evidence snapshot.
  - Wired the matrix into `pyproject.toml`, `setup.py`, CI package-data smoke,
    package smoke, and manifest tests so installed bundles carry the issue
    resolution evidence.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    19 tests.
  - `make validate-manifests`: passed.
  - `make package-smoke`: passed and confirmed installed bundle data includes
    `docs/architecture/ISSUE_RESOLUTION_MATRIX.md`.
- Later full local release gate after issue-resolution matrix packaging,
  2026-05-23 18:10 EDT:
  - `make release-check`: passed from the current worktree.
  - It ran `make lint`, `make test`, `make validate-manifests`,
    `make validate-contracts`, `make test-e2e-gc`, and `make package-smoke`.
  - `make lint` used the dependency-free `py_compile` fallback across 13
    Python files because `pyflakes` was not installed.
  - `make test`: passed 97 selected tests, skipped 2 optional adapter modules,
    and deselected 3 full E2E tests.
  - `make validate-contracts`: passed 9 schema/contract tests.
  - `make test-e2e-gc`: passed 15 real-GC fixture tests and deselected 3 full
    E2E tests.
  - `make package-smoke`: first hit the expected isolated PEP 517 network
    restriction while fetching build dependencies, then retried with
    `--no-build-isolation` and passed. The smoke verified CLI/API/MCP `--help`
    commands and installed bundle data including
    `docs/architecture/ISSUE_RESOLUTION_MATRIX.md`.
  - Updated `docs/architecture/RELEASE_EVIDENCE.md` with the fresh
    release-check result and reran `PYTHONPATH=tools python3 -m pytest
    tests/test_manifest.py -v`: passed, 19 tests.
  - Re-checked external workflow state after the ADR 0004 release-check:
    `gh auth status` still reports the default `yaravind` token is invalid.
    `gh run list` for `Test JVM Memory Leak Debugger Skill` on branch
    `codex/maturity-roadmap` succeeded with `[]`. `gh run list` for
    `MAT Runtime Smoke` still returned `could not find any workflows named MAT
    Runtime Smoke`, matching the uncommitted/unpushed workflow file.
- Later completion-audit packaging work, 2026-05-23 18:05 EDT:
  - Added `docs/architecture/MATURITY_COMPLETION_AUDIT.md`, a
    requirement-by-requirement audit that maps the original maturity goal to
    local evidence and the two remaining external workflow proofs.
  - Linked the audit from `docs/architecture/RELEASE_EVIDENCE.md` and
    `docs/architecture/RELEASE_READINESS_CHECKLIST.md`.
  - Wired the audit into `pyproject.toml`, `setup.py`, CI package-data smoke,
    package smoke, and manifest tests so installed bundles carry the completion
    audit.
  - `PYTHONPATH=tools python3 -m pytest tests/test_manifest.py -v`: passed,
    19 tests.
  - `make validate-manifests`: passed.
  - `make package-smoke`: passed and confirmed installed bundle data includes
    `docs/architecture/MATURITY_COMPLETION_AUDIT.md`.
  - Re-checked `gh auth status`; it still reports the default `yaravind` token
    is invalid. The first issue comment attempt hit a network error, then
    succeeded after network approval.
  - Added #2 completion-audit packaging follow-up note:
    https://github.com/yaravind/jvm-memory-leak-debugger/issues/2#issuecomment-4526647504
- Later full local release gate after completion audit packaging,
  2026-05-23 18:07 EDT:
  - `make release-check`: passed from the current worktree.
  - It ran `make lint`, `make test`, `make validate-manifests`,
    `make validate-contracts`, `make test-e2e-gc`, and `make package-smoke`.
  - `make lint` used the dependency-free `py_compile` fallback across 13
    Python files because `pyflakes` was not installed.
  - `make test`: passed 97 selected tests, skipped 2 optional adapter modules,
    and deselected 3 full E2E tests.
  - `make validate-contracts`: passed 9 schema/contract tests.
  - `make test-e2e-gc`: passed 15 real-GC fixture tests and deselected 3 full
    E2E tests.
  - `make package-smoke`: first hit the expected isolated PEP 517 network
    restriction while fetching build dependencies, then retried with
    `--no-build-isolation` and passed. The smoke verified CLI/API/MCP `--help`
    commands and installed bundle data including
    `docs/architecture/MATURITY_COMPLETION_AUDIT.md`.
  - Updated `docs/architecture/RELEASE_EVIDENCE.md` with the fresh
    release-check result and reran `PYTHONPATH=tools python3 -m pytest
    tests/test_manifest.py -v`: passed, 19 tests.
