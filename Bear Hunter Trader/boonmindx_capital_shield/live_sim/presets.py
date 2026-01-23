"""
BoonMindX Capital Shield Configuration Presets

Three named BoonMindX Capital Shield modes for different risk profiles:
- CONSERVATIVE: Maximum protection, lower drawdown threshold
- BALANCED: Standard protection, moderate threshold
- AGGRESSIVE: Minimal protection, higher threshold, permissive mode
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import os


@dataclass
class CapitalShieldPreset:
    """Capital Shield configuration preset"""
    name: str
    capital_shield_mode: str  # "STRICT" or "PERMISSIVE"
    max_drawdown_threshold: float  # Negative threshold (e.g., -0.10)
    block_bear_buys: bool
    health_check_enabled: bool = True
    engine_mode: str = "LIVE"  # "LIVE" or "MOCK"
    description: str = ""


# Preset definitions
PRESETS = {
    "conservative": CapitalShieldPreset(
        name="CONSERVATIVE",
        capital_shield_mode="STRICT",
        max_drawdown_threshold=-0.05,  # 5% max drawdown
        block_bear_buys=True,
        health_check_enabled=True,
        engine_mode="LIVE",
        description="Maximum capital protection. Lower drawdown threshold, strict regime guard, bear buys blocked."
    ),
    "balanced": CapitalShieldPreset(
        name="BALANCED",
        capital_shield_mode="STRICT",
        max_drawdown_threshold=-0.10,  # 10% max drawdown
        block_bear_buys=True,
        health_check_enabled=True,
        engine_mode="LIVE",
        description="Standard protection. Moderate drawdown threshold, strict regime guard, bear buys blocked."
    ),
    "aggressive": CapitalShieldPreset(
        name="AGGRESSIVE",
        capital_shield_mode="PERMISSIVE",
        max_drawdown_threshold=-0.15,  # 15% max drawdown
        block_bear_buys=False,  # Warnings only, no hard block
        health_check_enabled=True,
        engine_mode="LIVE",
        description="Minimal protection. Higher drawdown threshold, permissive regime guard, bear buys allowed with warnings."
    )
}


def get_preset(name: str) -> Optional[CapitalShieldPreset]:
    """
    Get preset by name (case-insensitive)
    
    Args:
        name: Preset name ("conservative", "balanced", "aggressive")
        
    Returns:
        CapitalShieldPreset or None if not found
    """
    name_lower = name.lower()
    return PRESETS.get(name_lower)


def apply_preset(name: str) -> Dict[str, Any]:
    """
    Apply preset configuration to environment
    
    This sets environment variables that will be read by config module.
    Note: This affects global state, so use with care in tests.
    
    Args:
        name: Preset name ("conservative", "balanced", "aggressive")
        
    Returns:
        Dict with applied configuration values
        
    Raises:
        ValueError: If preset name is invalid
    """
    preset = get_preset(name)
    if not preset:
        raise ValueError(f"Unknown preset: {name}. Valid options: {list(PRESETS.keys())}")
    
    # Store original values for restoration
    original_values = {}
    
    # Apply preset values
    os.environ['CAPITAL_SHIELD_MODE'] = preset.capital_shield_mode
    os.environ['MAX_DRAWDOWN_THRESHOLD'] = str(preset.max_drawdown_threshold)
    os.environ['BLOCK_BEAR_BUYS'] = str(preset.block_bear_buys).lower()
    os.environ['HEALTH_CHECK_ENABLED'] = str(preset.health_check_enabled).lower()
    os.environ['ENGINE_MODE'] = preset.engine_mode
    
    return {
        'CAPITAL_SHIELD_MODE': preset.capital_shield_mode,
        'MAX_DRAWDOWN_THRESHOLD': preset.max_drawdown_threshold,
        'BLOCK_BEAR_BUYS': preset.block_bear_buys,
        'HEALTH_CHECK_ENABLED': preset.health_check_enabled,
        'ENGINE_MODE': preset.engine_mode
    }


def get_preset_config(name: str) -> Dict[str, Any]:
    """
    Get preset configuration as dict without applying to environment
    
    Args:
        name: Preset name
        
    Returns:
        Dict with configuration values
    """
    preset = get_preset(name)
    if not preset:
        raise ValueError(f"Unknown preset: {name}. Valid options: {list(PRESETS.keys())}")
    
    return {
        'name': preset.name,
        'capital_shield_mode': preset.capital_shield_mode,
        'max_drawdown_threshold': preset.max_drawdown_threshold,
        'block_bear_buys': preset.block_bear_buys,
        'health_check_enabled': preset.health_check_enabled,
        'engine_mode': preset.engine_mode,
        'description': preset.description
    }


def list_presets() -> Dict[str, Dict[str, Any]]:
    """
    List all available presets
    
    Returns:
        Dict mapping preset names to their configurations
    """
    return {name: get_preset_config(name) for name in PRESETS.keys()}


if __name__ == "__main__":
    import json
    print("Available BoonMindX Capital Shield Presets:")
    print(json.dumps(list_presets(), indent=2))

