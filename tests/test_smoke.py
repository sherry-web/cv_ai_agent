"""
End-to-end (E2E) smoke tests for the CV AI Agent application.

These tests validate that the application:
- Starts correctly
- Handles its core endpoints without crashing
- Emits meaningful logs during startup and request handling

We use pytest's `caplog` fixture to ensure:
- INFO logs are emitted for successful startup and normal request flows
- WARNING or ERROR logs appear if failures are triggered

Absolute imports are used so pytest can run from the project root without
PYTHONPATH hacks, making this suite CI/CD safe on Windows, Linux, Docker,
and GitHub Actions.
"""

import pytest
import logging
from app import create_app


@pytest.fixture(scope="module")
def client(caplog):
    """
    Provides a Flask test client for smoke tests.

    - Scope is module-level to simulate near-production usage
    - Captures logs during app creation and request handling
    - Ensures startup emits INFO-level logs
    """
    caplog.set_level(logging.INFO)

    # App creation itself should produce logs
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_smoke_startup_and_health(client, caplog):
    """
    Verifies:
    - The application responds on /health
    - INFO logs are emitted during basic request handling
    """

    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert "status" in data
    assert data["status"] in ["healthy", "ok", "up"]

    # Logging verification: at least one INFO log must exist
    assert any(
        record.levelname == "INFO" for record in caplog.records
    ), "Expected INFO logs during startup or /health request"


def test_smoke_readiness_endpoint(client, caplog):
    """
    Verifies:
    - The readiness endpoint responds correctly
    - INFO logs are emitted for readiness checks
    """

    response = client.get("/ready")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert "ready" in data
    assert data["ready"] is True

    # Logging verification
    assert any(
        record.levelname == "INFO" for record in caplog.records
    ), "Expected INFO logs for /ready endpoint"


def test_smoke_logging_presence(client, caplog):
    """
    Ensures that logs are consistently produced for basic application activity.

    This test does not depend on exact message text, only that:
    - Logs exist
    - They contain meaningful severity levels
    """

    # Trigger a few standard requests
    client.get("/health")
    client.get("/ready")
    client.get("/")

    # At least some logs must exist
    assert len(caplog.records) > 0, "Expected logs to be generated during smoke tests"

    # Ensure we have INFO logs for normal flows
    assert any(
        record.levelname == "INFO" for record in caplog.records
    ), "Expected INFO logs during normal request handling"


def test_smoke_failure_logging(client, caplog):
    """
    Verifies that incorrect endpoints trigger WARNING or ERROR logs.

    This confirms that the application logs failure scenarios properly,
    which is critical for production observability.
    """

    response = client.get("/this-endpoint-does-not-exist")
    assert response.status_code == 404
    assert response.is_json

    # Logging verification for failure case
    assert any(
        record.levelname in ("WARNING", "ERROR") for record in caplog.records
    ), "Expected WARNING or ERROR logs for invalid endpoint access"
