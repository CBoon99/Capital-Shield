"""
Tests for Safety Rails
"""
import pytest
from app.core.safety_rails import (
    check_safety_rails,
    check_max_drawdown,
    check_health,
    check_regime_guard,
    set_system_health,
    set_current_metrics
)
from app.core.config import (
    MAX_DRAWDOWN_THRESHOLD,
    BLOCK_BEAR_BUYS,
    HEALTH_CHECK_ENABLED,
    CAPITAL_SHIELD_MODE
)
import os


class TestSafetyRails:
    """Test safety rail checks"""
    
    def test_safety_rails_all_pass(self):
        """Test safety rails when all checks pass"""
        # Set healthy state
        set_system_health(True)
        set_current_metrics({"max_drawdown": -0.05})  # Within threshold
        
        allowed, reason = check_safety_rails("BTC", "BUY", "BULL")
        
        assert allowed is True
        assert "passed" in reason.lower()
    
    def test_max_drawdown_block(self):
        """Test that max drawdown check blocks trades"""
        set_system_health(True)
        # Set drawdown below threshold
        set_current_metrics({"max_drawdown": -0.15})  # Below -10% threshold
        
        allowed, reason = check_safety_rails("BTC", "BUY", "BULL")
        
        assert allowed is False
        assert "drawdown" in reason.lower()
    
    def test_health_check_block(self):
        """Test that health check blocks trades when unhealthy"""
        set_system_health(False)
        set_current_metrics({"max_drawdown": -0.05})
        
        allowed, reason = check_safety_rails("BTC", "BUY", "BULL")
        
        assert allowed is False
        assert "health" in reason.lower()
    
    def test_regime_guard_strict_mode(self):
        """Test regime guard in STRICT mode"""
        original_mode = os.environ.get("CAPITAL_SHIELD_MODE", os.environ.get("SHIELD_MODE", "PERMISSIVE"))
        original_block = os.environ.get("BLOCK_BEAR_BUYS", "false")
        
        try:
            os.environ["CAPITAL_SHIELD_MODE"] = "STRICT"
            if "SHIELD_MODE" in os.environ:
                del os.environ["SHIELD_MODE"]
            os.environ["BLOCK_BEAR_BUYS"] = "true"
            
            # Reload config
            from importlib import reload
            import app.core.config
            reload(app.core.config)
            from app.core.safety_rails import check_safety_rails
            reload(app.core.safety_rails)
            
            set_system_health(True)
            set_current_metrics({"max_drawdown": -0.05})
            
            # BUY in BEAR regime should be blocked
            allowed, reason = check_safety_rails("BTC", "BUY", "BEAR")
            
            assert allowed is False
            assert "bear" in reason.lower() or "defensive" in reason.lower()
            
        finally:
            if original_mode:
                os.environ["CAPITAL_SHIELD_MODE"] = original_mode
            elif "CAPITAL_SHIELD_MODE" in os.environ:
                del os.environ["CAPITAL_SHIELD_MODE"]
            os.environ["BLOCK_BEAR_BUYS"] = original_block
    
    def test_regime_guard_permissive_mode(self):
        """Test regime guard allows trades in PERMISSIVE mode"""
        original_mode = os.environ.get("CAPITAL_SHIELD_MODE", os.environ.get("SHIELD_MODE", "PERMISSIVE"))
        
        try:
            os.environ["CAPITAL_SHIELD_MODE"] = "PERMISSIVE"
            if "SHIELD_MODE" in os.environ:
                del os.environ["SHIELD_MODE"]
            
            # Reload config to pick up env var change
            from importlib import reload
            import app.core.config
            reload(app.core.config)
            from app.core.safety_rails import check_safety_rails
            reload(app.core.safety_rails)
            
            set_system_health(True)
            set_current_metrics({"max_drawdown": -0.05})
            
            # BUY in BEAR regime should be allowed in permissive mode
            # Regime guard never hard-blocks in PERMISSIVE mode
            allowed, reason = check_safety_rails("BTC", "BUY", "BEAR")
            
            # Should pass (regime guard not active in permissive)
            assert allowed is True
            assert "passed" in reason.lower() or "not active" in reason.lower()
            
        finally:
            if original_mode:
                os.environ["CAPITAL_SHIELD_MODE"] = original_mode
            elif "CAPITAL_SHIELD_MODE" in os.environ:
                del os.environ["CAPITAL_SHIELD_MODE"]
    
    def test_check_max_drawdown(self):
        """Test max drawdown check function"""
        # Within threshold
        set_current_metrics({"max_drawdown": -0.05})
        allowed, reason = check_max_drawdown()
        assert allowed is True
        
        # Below threshold
        set_current_metrics({"max_drawdown": -0.15})
        allowed, reason = check_max_drawdown()
        assert allowed is False
        assert "drawdown" in reason.lower()
    
    def test_check_health(self):
        """Test health check function"""
        # Healthy
        set_system_health(True)
        healthy, reason = check_health()
        assert healthy is True
        
        # Unhealthy
        set_system_health(False)
        healthy, reason = check_health()
        assert healthy is False
    
    def test_check_regime_guard(self):
        """Test regime guard check function"""
        original_mode = os.environ.get("CAPITAL_SHIELD_MODE", os.environ.get("SHIELD_MODE", "PERMISSIVE"))
        original_block = os.environ.get("BLOCK_BEAR_BUYS", "false")
        
        try:
            os.environ["CAPITAL_SHIELD_MODE"] = "STRICT"
            if "SHIELD_MODE" in os.environ:
                del os.environ["SHIELD_MODE"]
            os.environ["BLOCK_BEAR_BUYS"] = "true"
            
            from importlib import reload
            import app.core.config
            reload(app.core.config)
            from app.core.safety_rails import check_regime_guard
            reload(app.core.safety_rails)
            
            # BUY in BEAR should be blocked
            allowed, reason = check_regime_guard("BEAR", "BUY")
            assert allowed is False
            
            # SELL in BEAR should be allowed
            allowed, reason = check_regime_guard("BEAR", "SELL")
            assert allowed is True
            
        finally:
            if original_mode:
                os.environ["CAPITAL_SHIELD_MODE"] = original_mode
            elif "CAPITAL_SHIELD_MODE" in os.environ:
                del os.environ["CAPITAL_SHIELD_MODE"]
            os.environ["BLOCK_BEAR_BUYS"] = original_block
    
    def test_no_metrics_available(self):
        """Test safety rails when no metrics available"""
        set_current_metrics(None)
        set_system_health(True)
        
        # Should allow trade if no metrics (graceful degradation)
        allowed, reason = check_safety_rails("BTC", "BUY", "BULL")
        
        # Health check should pass, drawdown check should pass (no metrics)
        assert allowed is True

