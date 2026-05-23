"""
test_cli.py - CLI presentation checks.
"""

import debug_memory_leak


def test_runtime_diagnostics_human_output_includes_curl(capsys):
    debug_memory_leak._print_runtime_diagnostics({
        "platform_key": "linux-x86_64",
        "platform_supported": True,
        "java_17_plus": True,
        "java_home": "/opt/jdk-17",
        "mat_version": "1.16.1",
        "mat_home": "/tmp/eclipse-mat",
        "mat_installed": False,
        "mat_eclipse_dir": None,
        "curl_available": False,
        "can_auto_install_mat": False,
        "ready_for_analysis": False,
        "errors": ["curl is required to download Eclipse MAT on first run."],
    })

    output = capsys.readouterr().out

    assert "curl:          False" in output
    assert "Auto-install:  False" in output
    assert "curl is required" in output
