"""
Health endpoint tests for CV AI Agent.

These tests validate both HTTP correctness and application logging behavior.
We use pytest's caplog fixture to ensure that the application emits logs for
key lifecycle and health-related operations.

Why this matters:
- Confirms the app is not failing silently
- Ensures logging is working in CI/CD, Docker, and production
- Adds confidence that monitoring and observability are active
- Does NOT change application behavior, only verifies it
"""

import logging
import pytest
from app import create_app


@pytest.fixture
def client(caplog):
    """
    Provides a Flask test client for health endpoint tests.
    Logging is captured via pytest's caplog fixture so we can assert that
    INFO / ERROR messages are emitted during requests.
    """
    app = create_app()
    app.config["TESTING"] = True

    # Capture INFO and above
    caplog.set_level(logging.INFO)

    with app.test_client() as client:
        yield client


def _has_log_level(caplog, level_name: str) -> bool:
    """
    Helper: Check if at least one log record of a given level exists.
    We do not match exact messages to avoid fragile tests.
    """
    return any(record.levelname == level_name for record in caplog.records)


def test_app_bootstraps_and_logs(client, caplog):
    """
    Verify the application starts correctly and emits at least one INFO log
    when the root endpoint is accessed.
    """
    response = client.get("/")
    assert response.status_code == 200

    # Logging verification
    assert _has_log_level(caplog, "INFO"), "Expected at least one INFO log on app bootstrap or request handling"


def test_health_endpoint_logs_info(client, caplog):
    """
    Verify /health endpoint:
    - Returns HTTP 200
    - Returns JSON payload
    - Emits at least one INFO log entry
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert "status" in data

    # Logging verification
    assert _has_log_level(caplog, "INFO"), "Expected INFO log for /health endpoint"


def test_ready_endpoint_logs_info(client, caplog):
    """
    Verify /ready endpoint:
    - Returns HTTP 200
    - Returns JSON payload
    - Emits at least one INFO log entry
    """
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert "ready" in data or "status" in data

    # Logging verification
    assert _has_log_level(caplog, "INFO"), "Expected INFO log for /ready endpoint"


def test_404_emits_warning_or_error_log(client, caplog):
    """
    Verify that invalid endpoints:
    - Return 404
    - Produce a WARNING or ERROR log entry

    This ensures error conditions are visible in logs and not silent.
    """
    response = client.get("/this-endpoint-does-not-exist")
    assert response.status_code == 404
    assert response.is_json

    data = response.get_json()
    assert any(key in data for key in ("error", "message", "status"))

    # Logging verification: allow WARNING or ERROR depending on implementation
    has_warning = _has_log_level(caplog, "WARNING")
    has_error = _has_log_level(caplog, "ERROR")

    assert has_warning or has_error, "Expected WARNING or ERROR log for 404 response"
