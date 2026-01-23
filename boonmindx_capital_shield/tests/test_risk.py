"""
Tests for Risk Endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_risk_missing_api_key():
    """Test that risk endpoint requires API key"""
    response = client.post(
        "/api/v1/risk",
        json={
            "asset": "ETH",
            "proposed_position_size": 10000,
            "current_equity": 100000,
            "price_history": [2000, 2050, 2100],
            "leverage": 5.0
        }
    )
    assert response.status_code == 401


def test_risk_valid_request():
    """Test valid risk request"""
    response = client.post(
        "/api/v1/risk",
        json={
            "asset": "ETH",
            "proposed_position_size": 10000,
            "current_equity": 100000,
            "price_history": [2000, 2050, 2100],
            "leverage": 5.0
        },
        headers={"X-API-Key": "test_pro_key_67890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_allowed" in data
    assert "risk_score" in data
    assert "regime" in data
    assert isinstance(data["risk_allowed"], bool)
    assert 0.0 <= data["risk_score"] <= 1.0

