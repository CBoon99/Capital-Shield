"""
Tests for Capital Shield configuration presets
"""
import os
import pytest
from live_sim.presets import (
    get_preset,
    apply_preset,
    get_preset_config,
    list_presets,
    PRESETS
)


class TestPresets:
    """Test preset functionality"""
    
    def test_presets_have_expected_parameters(self):
        """Verify all presets have expected parameters"""
        for preset_name, preset in PRESETS.items():
            assert preset.name
            assert preset.capital_shield_mode in ["STRICT", "PERMISSIVE"]
            assert preset.max_drawdown_threshold < 0  # Negative threshold
            assert isinstance(preset.block_bear_buys, bool)
            assert isinstance(preset.health_check_enabled, bool)
            assert preset.engine_mode in ["LIVE", "MOCK"]
    
    def test_get_preset(self):
        """Test getting preset by name"""
        # Test valid names (case-insensitive)
        assert get_preset("conservative") is not None
        assert get_preset("CONSERVATIVE") is not None
        assert get_preset("Conservative") is not None
        
        assert get_preset("balanced") is not None
        assert get_preset("aggressive") is not None
        
        # Test invalid name
        assert get_preset("invalid") is None
    
    def test_get_preset_config(self):
        """Test getting preset config as dict"""
        config = get_preset_config("conservative")
        
        assert 'name' in config
        assert 'capital_shield_mode' in config
        assert 'max_drawdown_threshold' in config
        assert 'block_bear_buys' in config
        assert 'description' in config
        
        assert config['name'] == "CONSERVATIVE"
        assert config['capital_shield_mode'] == "STRICT"
        assert config['max_drawdown_threshold'] == -0.05
    
    def test_apply_preset_sets_expected_values(self):
        """Test applying preset sets environment variables"""
        # Store original values
        original_values = {}
        env_keys = ['CAPITAL_SHIELD_MODE', 'SHIELD_MODE', 'MAX_DRAWDOWN_THRESHOLD', 'BLOCK_BEAR_BUYS', 'HEALTH_CHECK_ENABLED']
        for key in env_keys:
            original_values[key] = os.environ.get(key)
        
        try:
            # Apply conservative preset
            result = apply_preset("conservative")
            
            # Verify environment variables set
            assert os.environ.get('CAPITAL_SHIELD_MODE') == "STRICT"
            assert float(os.environ.get('MAX_DRAWDOWN_THRESHOLD')) == -0.05
            assert os.environ.get('BLOCK_BEAR_BUYS').lower() == 'true'
            
            # Verify return value
            assert result['CAPITAL_SHIELD_MODE'] == "STRICT"
            assert result['MAX_DRAWDOWN_THRESHOLD'] == -0.05
            assert result['BLOCK_BEAR_BUYS'] is True
            
            # Apply aggressive preset
            apply_preset("aggressive")
            assert os.environ.get('CAPITAL_SHIELD_MODE') == "PERMISSIVE"
            assert float(os.environ.get('MAX_DRAWDOWN_THRESHOLD')) == -0.15
            assert os.environ.get('BLOCK_BEAR_BUYS').lower() == 'false'
            
        finally:
            # Restore original values
            for key, value in original_values.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    
    def test_apply_preset_invalid_name(self):
        """Test applying invalid preset raises error"""
        with pytest.raises(ValueError, match="Unknown preset"):
            apply_preset("invalid_preset")
    
    def test_list_presets(self):
        """Test listing all presets"""
        presets = list_presets()
        
        assert 'conservative' in presets
        assert 'balanced' in presets
        assert 'aggressive' in presets
        
        # Verify structure
        for preset_name, config in presets.items():
            assert 'name' in config
            assert 'capital_shield_mode' in config
            assert 'max_drawdown_threshold' in config
    
    def test_preset_differences(self):
        """Verify presets have different configurations"""
        conservative = get_preset_config("conservative")
        balanced = get_preset_config("balanced")
        aggressive = get_preset_config("aggressive")
        
        # Conservative should have lowest drawdown threshold
        assert conservative['max_drawdown_threshold'] > balanced['max_drawdown_threshold']
        assert balanced['max_drawdown_threshold'] > aggressive['max_drawdown_threshold']
        
        # Conservative and balanced should be STRICT, aggressive PERMISSIVE
        assert conservative['capital_shield_mode'] == "STRICT"
        assert balanced['capital_shield_mode'] == "STRICT"
        assert aggressive['capital_shield_mode'] == "PERMISSIVE"
        
        # Conservative and balanced should block bear buys, aggressive should not
        assert conservative['block_bear_buys'] is True
        assert balanced['block_bear_buys'] is True
        assert aggressive['block_bear_buys'] is False

