import pytest
import logging
from cv_ai_agent.app import create_app

@pytest.fixture
def client(caplog):
    app = create_app()
    app.config["TESTING"] = True
    caplog.set_level(logging.INFO)
    with app.test_client() as client:
        yield client

def test_health_endpoint(client, caplog):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data.get("status") in ["healthy", "ok", "up"]
    assert any(record.levelname == "INFO" for record in caplog.records)

def test_ready_endpoint(client, caplog):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data.get("status") in ["ready", "healthy", "ok", "up"]
    assert any(record.levelname == "INFO" for record in caplog.records)
