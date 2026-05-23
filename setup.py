from setuptools import setup


CORE_MODULES = [
    "correlator",
    "debug_memory_leak",
    "dispatch",
    "gc_parser",
    "mat_runner",
    "pipeline",
    "reporter",
    "schema_validator",
    "server_adapter",
    "skill_resources",
    "mcp_adapter",
]

DATA_FILES = [
    (
        "share/jvm-memory-leak-debugger",
        ["README.md", "SKILL.md", "skill.json"],
    ),
    (
        "share/jvm-memory-leak-debugger/instructions",
        ["instructions/system_prompt.md"],
    ),
    (
        "share/jvm-memory-leak-debugger/references",
        [
            "references/fix_patterns.md",
            "references/g1gc_phases.md",
            "references/harness_configuration.md",
            "references/jvm_flags.md",
            "references/mat_installation.md",
            "references/preflight_checklist.md",
        ],
    ),
    (
        "share/jvm-memory-leak-debugger/assets",
        ["assets/report_template.md", "assets/skill_card.md"],
    ),
    (
        "share/jvm-memory-leak-debugger/examples",
        ["examples/conversation_examples.md", "examples/custom_patterns.json"],
    ),
    (
        "share/jvm-memory-leak-debugger/schemas",
        [
            "schemas/gc_analysis_result.json",
            "schemas/memory_leak_report.json",
            "schemas/recommendation_patterns.json",
        ],
    ),
    (
        "share/jvm-memory-leak-debugger/harnesses",
        [
            "harnesses/claude_desktop_config.example.json",
            "harnesses/codex_skill.example.json",
            "harnesses/copilot_extension.example.json",
            "harnesses/direct_function_dispatch.example.json",
            "harnesses/http_bridge.example.json",
            "harnesses/installed_commands.example.json",
        ],
    ),
    (
        "share/jvm-memory-leak-debugger/docs/adr",
        [
            "docs/adr/0000-record-architecture-decisions-template.md",
            "docs/adr/0001-use-pinned-cross-platform-mat-zip-distributions.md",
            "docs/adr/0002-use-pyproject-for-portable-cli-and-optional-adapter-extras.md",
            "docs/adr/0003-use-schema-backed-custom-recommendation-patterns.md",
            "docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md",
        ],
    ),
    (
        "share/jvm-memory-leak-debugger/docs/architecture",
        [
            "docs/architecture/ISSUE_RESOLUTION_MATRIX.md",
            "docs/architecture/JVM_MEMORY_LEAK_DEBUGGER_MATURITY_PRD.md",
            "docs/architecture/MATURITY_COMPLETION_AUDIT.md",
            "docs/architecture/RELEASE_EVIDENCE.md",
            "docs/architecture/RELEASE_READINESS_CHECKLIST.md",
        ],
    ),
]

setup(
    name="jvm-memory-leak-debugger",
    version="1.0.0",
    description="Portable JVM memory leak debugging skill and CLI for heap dumps and G1 GC logs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    py_modules=CORE_MODULES,
    package_dir={"": "tools"},
    install_requires=[],
    extras_require={
        "mcp": ["mcp>=1.0.0; python_version >= '3.10'"],
        "server": ["fastapi>=0.111.0", "uvicorn[standard]>=0.29.0"],
        "all": [
            "mcp>=1.0.0; python_version >= '3.10'",
            "fastapi>=0.111.0",
            "uvicorn[standard]>=0.29.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jvm-memory-leak-debugger=debug_memory_leak:main",
            "jvm-memory-leak-debugger-api=server_adapter:main",
            "jvm-memory-leak-debugger-mcp=mcp_adapter:main",
        ]
    },
    data_files=DATA_FILES,
)
