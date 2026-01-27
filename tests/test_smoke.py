"""
End-to-end (E2E) smoke tests for CV AI Agent application.
Uses absolute imports for pytest compatibility across Windows, Linux, and CI/CD pipelines.
Verifies logging for key operations.
"""

import pytest
import logging
from cv_ai_agent.app import create_app

@pytest.fixture(scope="module")
def client(caplog):
    """
    Provides a Flask test client for E2E smoke tests.
    Scope is module-level to simulate real usage across multiple requests.
    Captures logs using caplog for verification.
    """
    app = create_app()
    app.config["TESTING"] = True
    caplog.set_level(logging.INFO)
    with app.test_client() as client:
        yield client

def test_smoke_health_and_status(client, caplog):
    """Verify /health and /status endpoints respond correctly and log INFO messages."""
    for endpoint in ["/health", "/status"]:
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.is_json
        data = response.get_json()
        assert "status" in data
        assert any(record.levelname == "INFO" for record in caplog.records)

def test_smoke_crud_operations(client, caplog):
    """Perform end-to-end CRUD operations and verify responses and logging."""
    # CREATE
    payload = {"name": "Smoke Test Project", "description": "E2E smoke test"}
    response = client.post("/projects", json=payload)
    assert response.status_code in [200, 201]
    project_id = response.get_json().get("id")
    assert project_id is not None
    assert any(record.levelname == "INFO" for record in caplog.records)

    # READ
    response = client.get("/projects")
    projects = response.get_json()
    assert any(p["id"] == project_id for p in projects)
    assert any(record.levelname == "INFO" for record in caplog.records)

    # UPDATE
    update_payload = {"name": "Smoke Test Updated", "description": "Updated E2E"}
    response = client.put(f"/projects/{project_id}", json=update_payload)
    updated = response.get_json()
    assert updated["name"] == update_payload["name"]
    assert any(record.levelname == "INFO" for record in caplog.records)

    # DELETE
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code in [200, 204]
    response = client.get("/projects")
    projects = response.get_json()
    assert all(p["id"] != project_id for p in projects)
    assert any(record.levelname == "INFO" for record in caplog.records)

def test_smoke_logging_verification(client, caplog):
    """Ensure that logs are generated for all E2E requests."""
    for req in [
        (client.get, "/health"),
        (client.get, "/status"),
        (client.get, "/projects"),
        (client.post, "/projects", {"name": "Log Test", "description": "Logging"}),
        (client.put, "/projects/1", {"name": "Log Updated", "description": "Updated"}),
        (client.delete, "/projects/1")
    ]:
        func, endpoint, *payload = req
        func(endpoint, json=payload[0] if payload else None)
    assert len(caplog.records) > 0
    methods_logged = [m for m in ["GET", "POST", "PUT", "DELETE"]
                      if any(m in r.message for r in caplog.records)]
    assert set(methods_logged) >= {"GET", "POST", "PUT", "DELETE"}
