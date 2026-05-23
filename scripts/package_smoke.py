#!/usr/bin/env python3
"""
Run a non-editable package install smoke test outside the source checkout.

The smoke proves that console commands and bundled skill resources work after a
normal package install, which is the path most non-source harnesses should use.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


REQUIRED_BUNDLE_FILES = [
    "skill.json",
    "instructions/system_prompt.md",
    "references/fix_patterns.md",
    "references/preflight_checklist.md",
    "examples/custom_patterns.json",
    "schemas/memory_leak_report.json",
    "schemas/recommendation_patterns.json",
    "harnesses/codex_skill.example.json",
    "harnesses/copilot_extension.example.json",
    "harnesses/direct_function_dispatch.example.json",
    "harnesses/installed_commands.example.json",
    "docs/adr/0003-use-schema-backed-custom-recommendation-patterns.md",
    "docs/adr/0004-keep-full-heap-replay-as-external-release-evidence.md",
    "docs/architecture/ISSUE_RESOLUTION_MATRIX.md",
    "docs/architecture/MATURITY_COMPLETION_AUDIT.md",
    "docs/architecture/RELEASE_EVIDENCE.md",
    "docs/architecture/RELEASE_READINESS_CHECKLIST.md",
]


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_command(venv_dir: Path, command: str) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{command}.exe"
    return venv_dir / "bin" / command


def _run(args, cwd: Path) -> None:
    print("+", " ".join(str(arg) for arg in args))
    subprocess.run(args, cwd=str(cwd), check=True)


def _print_packaging_state(python: Path, cwd: Path) -> None:
    code = (
        "import sys\n"
        "print('smoke python:', sys.version.split()[0])\n"
        "try:\n"
        "    import setuptools\n"
        "    print('smoke setuptools:', setuptools.__version__)\n"
        "except Exception as exc:\n"
        "    print('smoke setuptools: unavailable', exc)"
    )
    _run([str(python), "-c", code], cwd=cwd)


def _create_venv(venv_dir: Path, system_site_packages: bool = False) -> Path:
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    print(f"Creating smoke venv: {venv_dir}")
    venv.EnvBuilder(with_pip=True, system_site_packages=system_site_packages).create(venv_dir)
    return _venv_python(venv_dir)


def _install_package(python: Path, repo_root: Path, cwd: Path) -> None:
    try:
        _run([str(python), "-m", "pip", "install", str(repo_root), "--no-deps"], cwd=cwd)
    except subprocess.CalledProcessError:
        raise


def _verify_installed_bundle(python: Path, cwd: Path) -> None:
    required = repr(REQUIRED_BUNDLE_FILES)
    code = (
        "import pathlib, skill_resources, sys; "
        "root=pathlib.Path(sys.prefix)/'share'/'jvm-memory-leak-debugger'; "
        f"required={required}; "
        "missing=[p for p in required if not (root/p).exists()]; "
        "assert not missing, missing; "
        "manifest=skill_resources.load_json('skill.json', {}); "
        "assert manifest['id']=='jvm-memory-leak-debugger', manifest; "
        "assert len(manifest['tools'])==4, manifest['tools']; "
        "readiness=skill_resources.find_repo_file('docs/architecture/RELEASE_READINESS_CHECKLIST.md'); "
        "assert readiness and readiness.exists(), readiness; "
        "print(root)"
    )
    _run([str(python), "-c", code], cwd=cwd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root to install from.",
    )
    parser.add_argument(
        "--work-dir",
        default=None,
        type=Path,
        help="Directory for the temporary venv and outside-repo smoke cwd.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep the temporary smoke directory for debugging.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    temp_parent = args.work_dir
    if temp_parent is None:
        temp_parent = Path(tempfile.mkdtemp(prefix="jvm-memleak-package-smoke-"))
        cleanup_parent = True
    else:
        temp_parent = temp_parent.resolve()
        if temp_parent.exists():
            shutil.rmtree(temp_parent)
        temp_parent.mkdir(parents=True)
        cleanup_parent = False

    try:
        venv_dir = temp_parent / "venv"
        outside_repo = temp_parent / "outside-repo"
        outside_repo.mkdir()

        python = _create_venv(venv_dir)
        _print_packaging_state(python, outside_repo)
        try:
            _install_package(python, repo_root, outside_repo)
        except subprocess.CalledProcessError:
            print(
                "PEP 517 isolated install failed; retrying with local build "
                "backend packages via --no-build-isolation."
            )
            python = _create_venv(venv_dir, system_site_packages=True)
            _print_packaging_state(python, outside_repo)
            _run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    str(repo_root),
                    "--no-deps",
                    "--no-build-isolation",
                ],
                cwd=outside_repo,
            )

        _run([str(_venv_command(venv_dir, "jvm-memory-leak-debugger")), "--help"], cwd=outside_repo)
        _run([str(_venv_command(venv_dir, "jvm-memory-leak-debugger-api")), "--help"], cwd=outside_repo)
        _run([str(_venv_command(venv_dir, "jvm-memory-leak-debugger-mcp")), "--help"], cwd=outside_repo)
        _verify_installed_bundle(python, outside_repo)
        print("package smoke OK")
        return 0
    finally:
        if args.keep:
            print(f"Kept smoke directory: {temp_parent}")
        elif cleanup_parent or args.work_dir is not None:
            shutil.rmtree(temp_parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
