"""Tests for health endpoint and app startup."""


def test_app_creates(app):
    """Test that the Flask app is created successfully."""
    assert app is not None


def test_health_endpoint(client):
    """Test health endpoint returns valid response."""
    response = client.get("/health")
    assert response.status_code in (200, 503)
    data = response.get_json()
    assert "status" in data
    assert "checks" in data
    assert data["status"] in ("healthy", "degraded")


def test_404_handler(client):
    """Test 404 error returns JSON."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_system_info(client):
    """Test system info endpoint."""
    response = client.get("/api/system/info")
    assert response.status_code == 200
