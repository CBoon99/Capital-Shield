"""
BoonMindX Capital Shield Safety Rails - Hard limits to prevent bad trades
Even in LIVE mode, BoonMindX Capital Shield has veto power
"""
from typing import Tuple, Optional, Dict, Any
import app.core.config as config_module


# Global state for system health (could be replaced with actual health checks)
_system_health_status = True
_current_metrics: Optional[Dict[str, Any]] = None


def set_system_health(healthy: bool):
    """Set system health status (called by health check)"""
    global _system_health_status
    _system_health_status = healthy


def set_current_metrics(metrics: Dict[str, Any]):
    """Set current metrics for safety rail checks"""
    global _current_metrics
    _current_metrics = metrics


def check_safety_rails(
    asset: str,
    action: str,
    regime: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Check safety rails before allowing trade
    
    Args:
        asset: Asset symbol
        action: Proposed action (BUY or SELL)
        regime: Current market regime (optional, will be checked if provided)
        
    Returns:
        (allowed: bool, reason: str)
    """
    # Read config values dynamically to pick up env var changes
    capital_shield_mode = config_module.CAPITAL_SHIELD_MODE
    max_drawdown_threshold = config_module.MAX_DRAWDOWN_THRESHOLD
    block_bear_buys = config_module.BLOCK_BEAR_BUYS
    health_check_enabled = config_module.HEALTH_CHECK_ENABLED
    
    # Check 1: Max Drawdown Check (always active, regardless of mode)
    if _current_metrics is not None:
        max_drawdown = _current_metrics.get("max_drawdown", 0.0)
        if max_drawdown < max_drawdown_threshold:
            return False, f"Max drawdown threshold exceeded ({max_drawdown:.2%} < {max_drawdown_threshold:.2%})"
    
    # Check 2: Health Check (always active, regardless of mode)
    if health_check_enabled:
        if not _system_health_status:
            return False, "System health check failed - trading disabled"
    
    # Check 3: Regime Guard (only active in STRICT mode)
    # In PERMISSIVE mode, regime guard never hard-blocks trades
    if capital_shield_mode == "STRICT" and regime is not None:
        if regime == "BEAR" and action == "BUY":
            if block_bear_buys:
                return False, "Bear regime - defensive mode (BUY blocked)"
    
    return True, "Safety checks passed"


def check_max_drawdown(metrics: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    """
    Check if max drawdown exceeds threshold
    
    Args:
        metrics: Optional metrics dict (uses global if None)
        
    Returns:
        (allowed: bool, reason: str)
    """
    # Read config dynamically
    max_drawdown_threshold = config_module.MAX_DRAWDOWN_THRESHOLD
    
    metrics_to_check = metrics or _current_metrics
    
    if metrics_to_check is None:
        return True, "No metrics available - allowing trade"
    
    max_drawdown = metrics_to_check.get("max_drawdown", 0.0)
    
    if max_drawdown < max_drawdown_threshold:
        return False, f"Max drawdown threshold exceeded ({max_drawdown:.2%} < {max_drawdown_threshold:.2%})"
    
    return True, "Max drawdown check passed"


def check_health() -> Tuple[bool, str]:
    """
    Check system health
    
    Returns:
        (healthy: bool, reason: str)
    """
    # Read config dynamically
    health_check_enabled = config_module.HEALTH_CHECK_ENABLED
    
    if not health_check_enabled:
        return True, "Health check disabled"
    
    if not _system_health_status:
        return False, "System health check failed"
    
    return True, "System healthy"


def check_regime_guard(regime: str, action: str) -> Tuple[bool, str]:
    """
    Check regime-based guard rules
    
    In STRICT mode: Can veto trades (e.g., block BUY in BEAR if flag enabled)
    In PERMISSIVE mode: Never hard-blocks trades purely due to regime
    
    Args:
        regime: Current market regime
        action: Proposed action
        
    Returns:
        (allowed: bool, reason: str)
    """
    # Read config dynamically
    capital_shield_mode = config_module.CAPITAL_SHIELD_MODE
    block_bear_buys = config_module.BLOCK_BEAR_BUYS
    
    # In PERMISSIVE mode, regime guard never hard-blocks
    if capital_shield_mode != "STRICT":
        return True, "Regime guard not active (CAPITAL_SHIELD_MODE != STRICT)"
    
    # In STRICT mode, can block BUY in BEAR if flag enabled
    if regime == "BEAR" and action == "BUY":
        if block_bear_buys:
            return False, "Bear regime - defensive mode (BUY blocked)"
    
    return True, "Regime guard check passed"

