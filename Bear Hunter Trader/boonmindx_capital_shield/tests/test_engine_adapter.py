"""
Tests for Engine Adapter
"""
import pytest
import os
from app.core.engine_adapter import (
    get_signal,
    get_risk,
    filter_trade,
    get_regime
)
from app.core.config import ENGINE_MODE


class TestEngineAdapter:
    """Test engine adapter in MOCK and LIVE modes"""
    
    def test_get_signal_mock_mode(self):
        """Test get_signal in MOCK mode"""
        # Ensure MOCK mode
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "MOCK"
        
        try:
            price_history = [100, 105, 110, 115, 120]  # Bullish trend
            
            response = get_signal("BTC", price_history)
            
            assert response.signal in ["BUY", "SELL", "HOLD"]
            assert 0.0 <= response.confidence <= 1.0
            assert response.regime in ["BULL", "BEAR", "SIDEWAYS"]
            assert 0.0 <= response.risk_score <= 1.0
            assert response.timestamp is not None
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
    
    def test_get_signal_bearish(self):
        """Test get_signal with bearish price history"""
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "MOCK"
        
        try:
            price_history = [120, 115, 110, 105, 100]  # Bearish trend
            
            response = get_signal("BTC", price_history)
            
            # Should detect bearish trend
            assert response.regime in ["BEAR", "SIDEWAYS"]
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
    
    def test_get_risk_mock_mode(self):
        """Test get_risk in MOCK mode"""
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "MOCK"
        
        try:
            price_history = [100, 102, 104, 106, 108]
            
            response = get_risk(
                asset="BTC",
                proposed_position_size=1000,
                current_equity=10000,
                price_history=price_history,
                leverage=1.0
            )
            
            assert isinstance(response.risk_allowed, bool)
            assert 0.0 <= response.max_risk_fraction <= 1.0
            assert response.recommended_position_size >= 0
            assert 0.0 <= response.risk_score <= 1.0
            assert response.regime in ["BULL", "BEAR", "SIDEWAYS"]
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
    
    def test_filter_trade_mock_mode(self):
        """Test filter_trade in MOCK mode"""
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "MOCK"
        
        try:
            price_history = [100, 105, 110, 115, 120]  # Bullish
            
            # Test BUY
            response = filter_trade("BTC", "BUY", price_history)
            
            assert isinstance(response.trade_allowed, bool)
            assert 0.0 <= response.confidence <= 1.0
            assert response.regime in ["BULL", "BEAR", "SIDEWAYS"]
            assert response.reason is not None
            assert response.risk_level in ["LOW", "MEDIUM", "HIGH"]
            
            # Test SELL
            response_sell = filter_trade("BTC", "SELL", price_history)
            assert isinstance(response_sell.trade_allowed, bool)
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
    
    def test_get_regime_mock_mode(self):
        """Test get_regime in MOCK mode"""
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "MOCK"
        
        try:
            price_history = [100, 105, 110, 115, 120]
            
            response = get_regime("BTC", price_history)
            
            assert response.regime in ["BULL", "BEAR", "SIDEWAYS"]
            assert 0.0 <= response.confidence <= 1.0
            assert response.signals is not None
            assert response.signals.rsi >= 0
            assert response.regime_stability >= 0
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
    
    def test_insufficient_data(self):
        """Test adapter handles insufficient data gracefully"""
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "MOCK"
        
        try:
            # Single price point
            price_history = [100]
            
            # Should not crash, return default values
            response = get_signal("BTC", price_history)
            assert response.signal in ["BUY", "SELL", "HOLD"]
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
    
    def test_live_mode_fallback(self):
        """Test that LIVE mode falls back to MOCK if engine unavailable"""
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "LIVE"
        
        try:
            # Set invalid engine path to force fallback
            original_path = os.environ.get("BEARHUNTER_ENGINE_PATH", "testing_area")
            os.environ["BEARHUNTER_ENGINE_PATH"] = "/nonexistent/path"
            
            price_history = [100, 105, 110]
            
            # Should fallback to MOCK without crashing
            response = get_signal("BTC", price_history)
            assert response.signal in ["BUY", "SELL", "HOLD"]
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
            os.environ["BEARHUNTER_ENGINE_PATH"] = original_path

