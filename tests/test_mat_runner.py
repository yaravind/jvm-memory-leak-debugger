"""
test_mat_runner.py - Focused tests for MAT runner public response behavior.
"""
from pathlib import Path
import subprocess
import zipfile

import pytest

import mat_runner


def test_parse_leak_suspects_omits_raw_page_text(tmp_path):
    report_zip = tmp_path / "sample_Leak_Suspects.zip"
    html = """
    <html><body>
      <h1>Problem Suspect 1</h1>
      <p>The memory is accumulated in one instance with 1,024 (12.5%) bytes.</p>
    </body></html>
    """

    with zipfile.ZipFile(report_zip, "w") as zf:
        zf.writestr("pages/suspect.html", html)

    findings = mat_runner._parse_leak_suspects(report_zip)

    assert "raw_text_by_page" not in findings
    assert findings["suspects"][0]["suspect_number"] == 1


def test_parse_leak_suspects_raises_when_problem_suspect_page_does_not_parse(tmp_path):
    report_zip = tmp_path / "broken_Leak_Suspects.zip"
    html = """
    <html><body>
      <h1>Problem Suspect</h1>
      <p>MAT changed this heading format and omitted the suspect number.</p>
    </body></html>
    """

    with zipfile.ZipFile(report_zip, "w") as zf:
        zf.writestr("pages/suspect.html", html)

    with pytest.raises(ValueError, match="Problem Suspect"):
        mat_runner._parse_leak_suspects(report_zip)


def test_parse_leak_suspects_prefers_problem_suspect_region_over_page_noise(tmp_path):
    report_zip = tmp_path / "sample_Leak_Suspects.zip"
    html = """
    <html><body>
      <nav>Problem Suspect navigation</nav>
      <div class="problem-suspect">
        <h1>Problem Suspect 1</h1>
        <p>The memory is accumulated in one instance with 2,048 (25.0%) bytes.</p>
      </div>
      <h2>Thread Stack</h2>
      <pre>at java.example.Outside.frame(Outside.java:10)</pre>
    </body></html>
    """

    with zipfile.ZipFile(report_zip, "w") as zf:
        zf.writestr("pages/suspect.html", html)

    findings = mat_runner._parse_leak_suspects(report_zip)

    suspect = findings["suspects"][0]
    assert suspect["suspect_number"] == 1
    assert suspect["retained_bytes"] == 2048
    assert suspect["retained_pct"] == 25.0
    assert suspect["stack_frames"] == []


def test_structure_findings_only_sets_accumulation_point_while_in_description():
    findings = mat_runner._structure_findings({
        "suspect.html": [
            "Problem Suspect 1",
            "Thread Stack",
            "java.example.Reader.readResultSet(Reader.java:10)",
        ]
    })

    assert findings["suspects"][0]["accumulation_point"] == ""


def test_run_mat_cleans_workspace_when_process_start_fails(tmp_path, monkeypatch):
    hprof = tmp_path / "dump.hprof"
    hprof.write_bytes(b"placeholder")
    workspace = tmp_path / "mat-workspace"

    monkeypatch.setattr(mat_runner, "ensure_mat", lambda mat_home: tmp_path)
    monkeypatch.setattr(mat_runner, "_find_java17", lambda: tmp_path)
    monkeypatch.setattr(mat_runner, "_equinox_jar", lambda eclipse_dir: tmp_path / "launcher.jar")
    monkeypatch.setattr(mat_runner.tempfile, "mkdtemp", lambda prefix: str(workspace))

    def fail_to_start(*args, **kwargs):
        raise RuntimeError("process failed before MAT could start")

    monkeypatch.setattr(mat_runner.subprocess, "Popen", fail_to_start)

    with pytest.raises(RuntimeError, match="process failed"):
        mat_runner.run_mat(str(hprof))

    assert not workspace.exists()


def test_run_mat_timeout_kills_process_and_cleans_workspace(tmp_path, monkeypatch):
    hprof = tmp_path / "dump.hprof"
    hprof.write_bytes(b"placeholder")
    workspace = tmp_path / "mat-workspace"

    class FakeStdout:
        def readline(self):
            return "MAT is still parsing\n"

    class FakeProcess:
        def __init__(self):
            self.stdout = FakeStdout()
            self.terminated = False
            self.killed = False
            self.wait_calls = 0

        def poll(self):
            return None

        def terminate(self):
            self.terminated = True

        def kill(self):
            self.killed = True

        def wait(self, timeout=None):
            self.wait_calls += 1
            if self.wait_calls == 1:
                raise subprocess.TimeoutExpired(cmd="mat", timeout=timeout)
            return -9

    fake_proc = FakeProcess()

    monkeypatch.setattr(mat_runner, "ensure_mat", lambda mat_home: tmp_path)
    monkeypatch.setattr(mat_runner, "_find_java17", lambda: tmp_path)
    monkeypatch.setattr(mat_runner, "_equinox_jar", lambda eclipse_dir: tmp_path / "launcher.jar")
    monkeypatch.setattr(mat_runner.tempfile, "mkdtemp", lambda prefix: str(workspace))
    monkeypatch.setattr(mat_runner.subprocess, "Popen", lambda *args, **kwargs: fake_proc)

    times = iter([0, 2])
    monkeypatch.setattr(mat_runner.time, "time", lambda: next(times))

    with pytest.raises(TimeoutError, match="MAT is still parsing"):
        mat_runner.run_mat(str(hprof), timeout_s=1)

    assert fake_proc.terminated is True
    assert fake_proc.killed is True
    assert not workspace.exists()


@pytest.mark.parametrize(
    ("system", "machine", "expected"),
    [
        ("Linux", "x86_64", "linux-x86_64"),
        ("Linux", "aarch64", "linux-aarch64"),
        ("Darwin", "arm64", "macos-aarch64"),
        ("Darwin", "x86_64", "macos-x86_64"),
        ("Windows", "AMD64", "windows-x86_64"),
    ],
)
def test_mat_distribution_selection(monkeypatch, system, machine, expected):
    monkeypatch.setattr(mat_runner.platform, "system", lambda: system)
    monkeypatch.setattr(mat_runner.platform, "machine", lambda: machine)

    dist = mat_runner._mat_distribution()

    assert dist.platform_key == expected
    assert dist.archive_name.endswith(".zip")
    assert len(dist.sha256) == 64


def test_mat_distribution_rejects_unsupported_platform(monkeypatch):
    monkeypatch.setattr(mat_runner.platform, "system", lambda: "Windows")
    monkeypatch.setattr(mat_runner.platform, "machine", lambda: "ARM64")

    with pytest.raises(RuntimeError, match="No Eclipse MAT"):
        mat_runner._mat_distribution()


def test_ensure_mat_detects_linux_zip_layout(tmp_path):
    mat_home = tmp_path / "mat"
    plugins = mat_home / "plugins"
    plugins.mkdir(parents=True)

    assert mat_runner.ensure_mat(mat_home) == mat_home


def test_ensure_mat_detects_macos_app_layout(tmp_path):
    mat_home = tmp_path / "MemoryAnalyzer.app"
    eclipse_dir = mat_home / "Contents" / "Eclipse"
    (eclipse_dir / "plugins").mkdir(parents=True)

    assert mat_runner.ensure_mat(mat_home) == eclipse_dir


def test_copy_extracted_root_replaces_existing_install(tmp_path):
    extract_dir = tmp_path / "extract"
    extracted_root = extract_dir / "mat"
    (extracted_root / "plugins").mkdir(parents=True)
    mat_home = tmp_path / "install"
    mat_home.mkdir()
    (mat_home / "old.txt").write_text("stale")

    mat_runner._copy_extracted_root(extract_dir, mat_home)

    assert (mat_home / "plugins").exists()
    assert not (mat_home / "old.txt").exists()


def test_find_java17_accepts_java17_home(tmp_path, monkeypatch):
    java_home = tmp_path / "jdk-17"
    java_bin = java_home / "bin" / ("java.exe" if mat_runner.os.name == "nt" else "java")
    java_bin.parent.mkdir(parents=True)
    java_bin.write_text("")

    monkeypatch.setenv("JAVA17_HOME", str(java_home))
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(mat_runner, "_java_major_version", lambda path: 17)

    assert mat_runner._find_java17() == java_home


def test_find_java17_rejects_old_java_home(tmp_path, monkeypatch):
    java_home = tmp_path / "jdk-11"
    java_bin = java_home / "bin" / ("java.exe" if mat_runner.os.name == "nt" else "java")
    java_bin.parent.mkdir(parents=True)
    java_bin.write_text("")

    monkeypatch.setenv("JAVA_HOME", str(java_home))
    monkeypatch.delenv("JAVA17_HOME", raising=False)
    monkeypatch.setattr(mat_runner, "_java_major_version", lambda path: 11)

    with pytest.raises(EnvironmentError, match="JAVA_HOME"):
        mat_runner._find_java17()


def test_runtime_diagnostics_reports_first_run_readiness(tmp_path, monkeypatch):
    java_home = tmp_path / "jdk-17"
    java_bin = java_home / "bin" / ("java.exe" if mat_runner.os.name == "nt" else "java")
    java_bin.parent.mkdir(parents=True)
    java_bin.write_text("")

    monkeypatch.setattr(mat_runner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(mat_runner.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(mat_runner, "_find_java17", lambda: java_home)
    monkeypatch.setattr(mat_runner, "_java_major_version", lambda path: 17)
    monkeypatch.setattr(mat_runner, "_curl_available", lambda: True)

    status = mat_runner.runtime_diagnostics(tmp_path / "mat")

    assert status["platform_key"] == "linux-x86_64"
    assert status["platform_supported"] is True
    assert status["java_17_plus"] is True
    assert status["mat_installed"] is False
    assert status["curl_available"] is True
    assert status["can_auto_install_mat"] is True
    assert status["ready_for_analysis"] is True


def test_runtime_diagnostics_requires_curl_for_first_run_download(tmp_path, monkeypatch):
    java_home = tmp_path / "jdk-17"

    monkeypatch.setattr(mat_runner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(mat_runner.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(mat_runner, "_find_java17", lambda: java_home)
    monkeypatch.setattr(mat_runner, "_java_major_version", lambda path: 17)
    monkeypatch.setattr(mat_runner, "_curl_available", lambda: False)

    status = mat_runner.runtime_diagnostics(tmp_path / "missing-mat")

    assert status["platform_supported"] is True
    assert status["java_17_plus"] is True
    assert status["mat_installed"] is False
    assert status["curl_available"] is False
    assert status["can_auto_install_mat"] is False
    assert status["ready_for_analysis"] is False
    assert any("curl is required" in error for error in status["errors"])


def test_runtime_diagnostics_allows_existing_mat_without_curl(tmp_path, monkeypatch):
    java_home = tmp_path / "jdk-17"
    mat_home = tmp_path / "mat"
    plugins = mat_home / "plugins"
    plugins.mkdir(parents=True)
    (plugins / "org.eclipse.equinox.launcher_1.0.0.jar").write_text("")

    monkeypatch.setattr(mat_runner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(mat_runner.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(mat_runner, "_find_java17", lambda: java_home)
    monkeypatch.setattr(mat_runner, "_java_major_version", lambda path: 17)
    monkeypatch.setattr(mat_runner, "_curl_available", lambda: False)

    status = mat_runner.runtime_diagnostics(mat_home)

    assert status["mat_installed"] is True
    assert status["equinox_launcher_found"] is True
    assert status["curl_available"] is False
    assert status["can_auto_install_mat"] is False
    assert status["ready_for_analysis"] is True


def test_runtime_diagnostics_rejects_broken_existing_mat_without_curl(tmp_path, monkeypatch):
    java_home = tmp_path / "jdk-17"
    mat_home = tmp_path / "mat"
    (mat_home / "plugins").mkdir(parents=True)

    monkeypatch.setattr(mat_runner.platform, "system", lambda: "Linux")
    monkeypatch.setattr(mat_runner.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(mat_runner, "_find_java17", lambda: java_home)
    monkeypatch.setattr(mat_runner, "_java_major_version", lambda path: 17)
    monkeypatch.setattr(mat_runner, "_curl_available", lambda: False)

    status = mat_runner.runtime_diagnostics(mat_home)

    assert status["mat_installed"] is True
    assert status["equinox_launcher_found"] is False
    assert status["can_auto_install_mat"] is False
    assert status["ready_for_analysis"] is False
    assert any("Equinox launcher jar not found" in error for error in status["errors"])
