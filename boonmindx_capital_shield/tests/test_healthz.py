"""
Tests for Health Check Endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz_no_auth():
    """Test that healthz endpoint doesn't require auth"""
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200


def test_healthz_response():
    """Test healthz response structure"""
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "uptime" in data
    assert "version" in data
    assert data["status"] == "ok"
    assert isinstance(data["uptime"], int)
    assert data["uptime"] >= 0


def test_healthz_always_ok():
    """Test that healthz always returns ok status"""
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

