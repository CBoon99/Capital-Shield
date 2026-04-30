"""
Tests for Regime Endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_regime_missing_api_key():
    """Test that regime endpoint requires API key"""
    response = client.post(
        "/api/v1/regime",
        json={
            "asset": "BTC",
            "price_history": [100, 102, 101, 105]
        }
    )
    assert response.status_code == 401


def test_regime_valid_request():
    """Test valid regime request"""
    response = client.post(
        "/api/v1/regime",
        json={
            "asset": "BTC",
            "price_history": [100, 102, 101, 105]
        },
        headers={"X-API-Key": "test_pro_key_67890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "regime" in data
    assert "confidence" in data
    assert "signals" in data
    assert data["regime"] in ["BULL", "BEAR", "SIDEWAYS"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert "sma_slope" in data["signals"]
    assert "rsi" in data["signals"]

