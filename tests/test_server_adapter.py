"""
test_server_adapter.py - FastAPI adapter smoke tests.

These tests require the optional server extra and are skipped in core-only
environments.
"""
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
testclient = pytest.importorskip("fastapi.testclient")

import server
import server_adapter


FIXTURES = Path(__file__).parent / "fixtures"
GC_LOG = FIXTURES / "gc-16615.log"


def test_http_health_and_manifest_routes():
    client = testclient.TestClient(server.app)

    health = client.get("/health")
    manifest = client.get("/skill.json")

    assert health.status_code == 200
    assert health.json()["skill"] == "jvm-memory-leak-debugger"
    assert manifest.status_code == 200
    assert {tool["name"] for tool in manifest.json()["tools"]} == set(server.TOOLS)
    assert {tool["name"] for tool in server_adapter.skill_manifest()["tools"]} == set(server_adapter.TOOLS)


def test_http_tool_catalog_lists_routes_and_parameters():
    client = testclient.TestClient(server.app)

    response = client.get("/tools")

    assert response.status_code == 200
    tools = response.json()["tools"]
    assert {tool["name"] for tool in tools} == set(server.TOOLS)
    for tool in tools:
        assert tool["method"] == "POST"
        assert tool["route"] == f"/tools/{tool['name']}"
        assert "type" in tool["parameters"]


def test_http_analyze_gc_log_route():
    client = testclient.TestClient(server.app)

    response = client.post("/tools/analyze_gc_log", json={"gc_log_path": str(GC_LOG)})

    assert response.status_code == 200
    assert response.json()["config"]["collector"] == "G1"
    assert response.json()["full_gc_count"] == 33


def test_http_dispatch_errors_use_client_status_codes():
    client = testclient.TestClient(server.app)

    response = client.post("/tools/analyze_gc_log", json={})

    assert response.status_code == 422
    assert response.json()["type"] == "ToolDispatchError"
    assert "gc_log_path" in response.json()["error"]


def test_http_rejects_non_object_tool_body():
    client = testclient.TestClient(server.app)

    response = client.post("/tools/analyze_gc_log", json=[])

    assert response.status_code == 422
    assert response.json()["type"] == "ToolDispatchError"
    assert "JSON object" in response.json()["error"]


def test_http_rejects_invalid_json_body():
    client = testclient.TestClient(server.app)

    response = client.post(
        "/tools/analyze_gc_log",
        content="{not-json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": "Invalid JSON request body.",
        "type": "InvalidRequestBody",
    }
