"""
Tests for Signal Endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_signal_missing_api_key():
    """Test that signal endpoint requires API key"""
    response = client.post(
        "/api/v1/signal",
        json={
            "asset": "BTC",
            "price_history": [100, 102, 101, 105]
        }
    )
    assert response.status_code == 401


def test_signal_invalid_api_key():
    """Test that invalid API key is rejected"""
    response = client.post(
        "/api/v1/signal",
        json={
            "asset": "BTC",
            "price_history": [100, 102, 101, 105]
        },
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401


def test_signal_valid_request():
    """Test valid signal request"""
    response = client.post(
        "/api/v1/signal",
        json={
            "asset": "BTC",
            "price_history": [100, 102, 101, 105]
        },
        headers={"X-API-Key": "test_free_key_12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "signal" in data
    assert "confidence" in data
    assert "regime" in data
    assert data["signal"] in ["BUY", "SELL", "HOLD"]
    assert 0.0 <= data["confidence"] <= 1.0


def test_signal_response_schema():
    """Test signal response schema"""
    response = client.post(
        "/api/v1/signal",
        json={
            "asset": "BTC",
            "price_history": [100, 102, 101, 105]
        },
        headers={"X-API-Key": "test_pro_key_67890"}
    )
    assert response.status_code == 200
    data = response.json()
    required_fields = ["signal", "confidence", "regime", "regime_confidence", 
                      "risk_score", "reason", "timestamp"]
    for field in required_fields:
        assert field in data

