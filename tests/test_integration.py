"""
Integration tests for CV AI Agent CRUD endpoints.
Uses absolute imports for pytest compatibility across Windows, Linux, and CI/CD pipelines.
Verifies logging for CRUD operations.
"""

import pytest
import logging
from cv_ai_agent.app import create_app

@pytest.fixture
def client(caplog):
    """
    Provides a Flask test client for integration tests.
    Uses in-memory SQLite database and captures logs with caplog.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["DATABASE_URI"] = "sqlite:///:memory:"
    caplog.set_level(logging.INFO)
    with app.test_client() as client:
        yield client

def test_crud_create(client, caplog):
    """Test creating a project and verify logging."""
    payload = {"name": "Integration Project", "description": "Mocked DB test"}
    response = client.post("/projects", json=payload)
    assert response.status_code in [200, 201]
    data = response.get_json()
    assert data["name"] == payload["name"]
    assert any(record.levelname == "INFO" for record in caplog.records)

def test_crud_read(client, caplog):
    """Test reading projects and verify logging."""
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(record.levelname == "INFO" for record in caplog.records)

def test_crud_update(client, caplog):
    """Test updating a project and verify logging."""
    response = client.get("/projects")
    projects = response.get_json()
    if projects:
        project_id = projects[0]["id"]
        payload = {"name": "Updated Integration", "description": "Updated description"}
        resp = client.put(f"/projects/{project_id}", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == payload["name"]
        assert any(record.levelname == "INFO" for record in caplog.records)

def test_crud_delete(client, caplog):
    """Test deleting a project and verify logging."""
    response = client.get("/projects")
    projects = response.get_json()
    if projects:
        project_id = projects[0]["id"]
        resp = client.delete(f"/projects/{project_id}")
        assert resp.status_code in [200, 204]
        response = client.get("/projects")
        projects = response.get_json()
        assert all(p["id"] != project_id for p in projects)
        assert any(record.levelname == "INFO" for record in caplog.records)
