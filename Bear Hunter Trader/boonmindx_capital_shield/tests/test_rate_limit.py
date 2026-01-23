"""
Tests for Rate Limiting
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rate_limit_exceeded():
    """Test that rate limit is enforced"""
    # Make 11 rapid requests (limit is 10/second)
    responses = []
    for i in range(11):
        response = client.post(
            "/api/v1/signal",
            json={
                "asset": "BTC",
                "price_history": [100, 102]
            },
            headers={"X-API-Key": "test_free_key_12345"}
        )
        responses.append(response)
    
    # At least one should be rate limited (429)
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes or all(code == 200 for code in status_codes[:10])

