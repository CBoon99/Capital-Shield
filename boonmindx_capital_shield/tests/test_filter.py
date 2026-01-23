"""
Tests for Filter Endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_filter_missing_api_key():
    """Test that filter endpoint requires API key"""
    response = client.post(
        "/api/v1/filter",
        json={
            "asset": "SOL",
            "action": "BUY",
            "price_history": [50, 52, 51, 55]
        }
    )
    assert response.status_code == 401


def test_filter_valid_request():
    """Test valid filter request"""
    response = client.post(
        "/api/v1/filter",
        json={
            "asset": "SOL",
            "action": "BUY",
            "price_history": [50, 52, 51, 55]
        },
        headers={"X-API-Key": "test_pro_key_67890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "trade_allowed" in data
    assert "confidence" in data
    assert "regime" in data
    assert isinstance(data["trade_allowed"], bool)
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["regime"] in ["BULL", "BEAR", "SIDEWAYS"]


def test_filter_buy_action():
    """Test filter with BUY action"""
    response = client.post(
        "/api/v1/filter",
        json={
            "asset": "BTC",
            "action": "BUY",
            "price_history": [100, 105, 108, 110]  # Bullish
        },
        headers={"X-API-Key": "test_pro_key_67890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "trade_allowed" in data
    assert "regime" in data


def test_filter_sell_action():
    """Test filter with SELL action"""
    response = client.post(
        "/api/v1/filter",
        json={
            "asset": "BTC",
            "action": "SELL",
            "price_history": [100, 95, 92, 90]  # Bearish
        },
        headers={"X-API-Key": "test_pro_key_67890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "trade_allowed" in data

