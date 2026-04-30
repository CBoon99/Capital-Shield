"""
Tests for MOCK/LIVE mode switching
"""
import pytest
import os
from app.core.config import ENGINE_MODE, CAPITAL_SHIELD_MODE
from app.core.engine_adapter import get_signal, get_regime


class TestModeSwitching:
    """Test mode switching between MOCK and LIVE"""
    
    def test_mock_mode_default(self):
        """Test that MOCK mode is default"""
        # Clear any existing ENGINE_MODE
        if "ENGINE_MODE" in os.environ:
            del os.environ["ENGINE_MODE"]
        
        # Reload config to get default
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        
        assert app.core.config.ENGINE_MODE == "MOCK"
    
    def test_live_mode_env_var(self):
        """Test that LIVE mode can be set via env var"""
        original_mode = os.environ.get("ENGINE_MODE")
        
        try:
            os.environ["ENGINE_MODE"] = "LIVE"
            
            from importlib import reload
            import app.core.config
            reload(app.core.config)
            
            assert app.core.config.ENGINE_MODE == "LIVE"
            
        finally:
            if original_mode:
                os.environ["ENGINE_MODE"] = original_mode
            elif "ENGINE_MODE" in os.environ:
                del os.environ["ENGINE_MODE"]
    
    def test_mock_mode_behavior(self):
        """Test that MOCK mode returns deterministic results"""
        original_mode = os.environ.get("ENGINE_MODE", "MOCK")
        os.environ["ENGINE_MODE"] = "MOCK"
        
        try:
            price_history = [100, 105, 110, 115, 120]
            
            # Call twice - should get same result
            response1 = get_signal("BTC", price_history)
            response2 = get_signal("BTC", price_history)
            
            # In MOCK mode, same inputs should give same outputs
            assert response1.signal == response2.signal
            assert response1.regime == response2.regime
            
        finally:
            os.environ["ENGINE_MODE"] = original_mode
    
    def test_capital_shield_mode_permissive_default(self):
        """Test that PERMISSIVE is default Capital Shield mode"""
        original_mode = os.environ.get("CAPITAL_SHIELD_MODE")
        
        try:
            if "CAPITAL_SHIELD_MODE" in os.environ:
                del os.environ["CAPITAL_SHIELD_MODE"]
            if "SHIELD_MODE" in os.environ:
                del os.environ["SHIELD_MODE"]
            
            from importlib import reload
            import app.core.config
            reload(app.core.config)
            
            assert app.core.config.CAPITAL_SHIELD_MODE == "PERMISSIVE"
            
        finally:
            if original_mode:
                os.environ["CAPITAL_SHIELD_MODE"] = original_mode
            elif "CAPITAL_SHIELD_MODE" in os.environ:
                del os.environ["CAPITAL_SHIELD_MODE"]
    
    def test_capital_shield_mode_strict_env_var(self):
        """Test that STRICT mode can be set via env var"""
        original_mode = os.environ.get("CAPITAL_SHIELD_MODE")
        
        try:
            os.environ["CAPITAL_SHIELD_MODE"] = "STRICT"
            
            from importlib import reload
            import app.core.config
            reload(app.core.config)
            
            assert app.core.config.CAPITAL_SHIELD_MODE == "STRICT"
            
        finally:
            if original_mode:
                os.environ["CAPITAL_SHIELD_MODE"] = original_mode
            elif "CAPITAL_SHIELD_MODE" in os.environ:
                del os.environ["CAPITAL_SHIELD_MODE"]

