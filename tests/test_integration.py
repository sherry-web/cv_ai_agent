"""
Integration tests for CV AI Agent CRUD endpoints.

These tests validate both functional correctness and logging behavior.
We use pytest's `caplog` fixture to ensure that:
- Successful integration flows emit INFO logs
- Failure scenarios emit WARNING or ERROR logs when applicable

Absolute imports are used so pytest can run from the project root
without PYTHONPATH hacks, making the suite CI/CD safe on
Windows, Linux, Docker, and GitHub Actions.
"""

import pytest
import logging
from app import create_app


@pytest.fixture
def client(caplog):
    """
    Provides a Flask test client for integration tests.

    - Uses an in-memory SQLite database to keep tests isolated
    - Captures logs using pytest's caplog for verification
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["DATABASE_URI"] = "sqlite:///:memory:"
    caplog.set_level(logging.INFO)

    with app.test_client() as client:
        yield client


def test_crud_create(client, caplog):
    """
    Test creating a project and verify logging behavior.

    Expectations:
    - Endpoint returns success status
    - Project is created correctly
    - At least one INFO log is emitted
    """
    payload = {"name": "Integration Project", "description": "Mocked DB test"}
    response = client.post("/projects", json=payload)

    assert response.status_code in [200, 201]
    data = response.get_json()
    assert data["name"] == payload["name"]

    # Logging verification
    assert any(
        record.levelname == "INFO" for record in caplog.records
    ), "Expected at least one INFO log for CREATE operation"


def test_crud_read(client, caplog):
    """
    Test reading projects and verify logging behavior.

    Expectations:
    - Endpoint returns a list
    - At least one INFO log is emitted
    """
    response = client.get("/projects")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

    # Logging verification
    assert any(
        record.levelname == "INFO" for record in caplog.records
    ), "Expected at least one INFO log for READ operation"


def test_crud_update(client, caplog):
    """
    Test updating a project and verify logging behavior.

    Expectations:
    - Update succeeds when a project exists
    - At least one INFO log is emitted
    - If update fails, WARNING or ERROR logs must exist
    """
    response = client.get("/projects")
    projects = response.get_json()

    if projects:
        project_id = projects[0]["id"]
        payload = {"name": "Updated Integration", "description": "Updated description"}
        resp = client.put(f"/projects/{project_id}", json=payload)

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == payload["name"]

        # Logging verification for success
        assert any(
            record.levelname == "INFO" for record in caplog.records
        ), "Expected INFO log for UPDATE operation"
    else:
        # If no project exists, ensure a warning or error is logged
        assert any(
            record.levelname in ("WARNING", "ERROR") for record in caplog.records
        ), "Expected WARNING or ERROR log when UPDATE cannot be performed"


def test_crud_delete(client, caplog):
    """
    Test deleting a project and verify logging behavior.

    Expectations:
    - Delete succeeds when a project exists
    - At least one INFO log is emitted
    - If deletion fails, WARNING or ERROR logs must exist
    """
    response = client.get("/projects")
    projects = response.get_json()

    if projects:
        project_id = projects[0]["id"]
        resp = client.delete(f"/projects/{project_id}")

        assert resp.status_code in [200, 204]

        response = client.get("/projects")
        projects = response.get_json()
        assert all(p["id"] != project_id for p in projects)

        # Logging verification for success
        assert any(
            record.levelname == "INFO" for record in caplog.records
        ), "Expected INFO log for DELETE operation"
    else:
        # If no project exists, ensure a warning or error is logged
        assert any(
            record.levelname in ("WARNING", "ERROR") for record in caplog.records
        ), "Expected WARNING or ERROR log when DELETE cannot be performed"
