from unittest.mock import patch


def test_health_endpoint_healthy(client):
    response = client.get("/api/v1/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "app_name" in data
    assert "database" in data
    assert "system" in data
    assert "python_version" in data["system"]


def test_health_endpoint_mocked_success(client):
    with patch("app.api.v1.health.check_db_connection", return_value=(True, 4.5, "Database operational")):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"]["connected"] is True
        assert data["database"]["latency_ms"] == 4.5
        assert data["database"]["message"] == "Database operational"


def test_health_endpoint_degraded(client):
    with patch("app.api.v1.health.check_db_connection", return_value=(False, 120.0, "Connection refused")):
        response = client.get("/api/v1/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"]["connected"] is False
