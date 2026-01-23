"""
Slippage & Latency Modeling - BoonMindX Capital Shield (v1)

Purpose:
- Provide simple, explicit models for slippage and latency impact
- Allow simulations to run with or without execution costs
- Keep assumptions transparent and configurable

This is NOT a microstructure engine. It is a first-order approximation for:
- Backtests
- FP tests
- Opportunity cost analysis

ASSUMPTIONS:
- Fixed or volatility-scaled slippage (basis points)
- Latency penalty as additional bps cost
- No spread dynamics, partial fills, or market impact modeling
- First-order approximation only
"""
from dataclasses import dataclass
from typing import Optional, List
import numpy as np


@dataclass
class ExecutionCostConfig:
    """Configuration for execution cost models"""
    enabled: bool = False
    slippage_model: str = "fixed_bps"  # ["fixed_bps", "vol_scaled"]
    fixed_bps: float = 5.0  # Fixed slippage in basis points
    base_bps: float = 3.0  # Base bps for volatility-scaled model
    latency_ms: int = 50  # Latency in milliseconds


def slippage_fixed_bps(price: float, notional: float, bps: float = 5.0) -> float:
    """
    Apply fixed basis-point slippage to a trade.
    
    Args:
        price: Executed price (before slippage)
        notional: Trade notional size (position change * price)
        bps: Basis points of slippage (5 bps = 0.05%)
        
    Returns:
        Effective cost (currency units) to subtract from equity
        
    Example:
        >>> slippage_fixed_bps(100.0, 10000.0, 5.0)
        5.0  # 5 bps of 10,000 = 5.0
    """
    if notional <= 0:
        return 0.0
    
    # Convert bps to decimal (5 bps = 0.0005)
    slippage_decimal = bps / 10000.0
    
    # Calculate cost
    cost = notional * slippage_decimal
    
    return cost


def slippage_vol_scaled(
    price: float,
    notional: float,
    volatility: float,
    base_bps: float = 3.0
) -> float:
    """
    Apply volatility-scaled slippage to a trade.
    
    Uses recent volatility to scale base bps:
    - Low volatility (e.g., < 1%) → base bps
    - High volatility (e.g., > 3%) → base bps * volatility_multiplier
    
    Args:
        price: Executed price (before slippage)
        notional: Trade notional size
        volatility: Recent volatility (e.g., rolling std of returns, normalized)
        base_bps: Base slippage in basis points
        
    Returns:
        Effective cost (currency units)
        
    Example:
        >>> slippage_vol_scaled(100.0, 10000.0, 0.02, 3.0)
        6.0  # 3 bps * 2.0 volatility multiplier = 6 bps
    """
    if notional <= 0:
        return 0.0
    
    # Normalize volatility (assume 1% = 1.0 multiplier)
    # If volatility is 2%, multiplier is 2.0
    volatility_multiplier = max(1.0, volatility * 100)  # Scale to percentage
    
    # Cap multiplier at reasonable level (e.g., 5x)
    volatility_multiplier = min(volatility_multiplier, 5.0)
    
    # Calculate effective bps
    effective_bps = base_bps * volatility_multiplier
    
    # Convert to cost
    slippage_decimal = effective_bps / 10000.0
    cost = notional * slippage_decimal
    
    return cost


def latency_penalty_bps(latency_ms: int) -> float:
    """
    Map latency in ms to extra bps cost (very coarse model).
    
    Latency buckets:
    - 0-10 ms  -> +0 bps (ultra-low latency)
    - 10-50 ms -> +1 bps (low latency)
    - 50-200 ms -> +3 bps (medium latency)
    - >200 ms  -> +5 bps (high latency)
    
    Args:
        latency_ms: Latency in milliseconds
        
    Returns:
        Additional bps cost
        
    Example:
        >>> latency_penalty_bps(25)
        1.0  # 25 ms falls in 10-50 ms bucket → +1 bps
        >>> latency_penalty_bps(150)
        3.0  # 150 ms falls in 50-200 ms bucket → +3 bps
    """
    if latency_ms < 10:
        return 0.0
    elif latency_ms < 50:
        return 1.0
    elif latency_ms < 200:
        return 3.0
    else:
        return 5.0


def calculate_execution_cost(
    price: float,
    notional: float,
    config: ExecutionCostConfig,
    volatility: Optional[float] = None
) -> float:
    """
    Calculate total execution cost (slippage + latency) for a trade.
    
    Args:
        price: Executed price
        notional: Trade notional size
        config: Execution cost configuration
        volatility: Optional volatility for vol-scaled model
        
    Returns:
        Total execution cost (currency units)
    """
    if not config.enabled or notional <= 0:
        return 0.0
    
    # Calculate slippage
    if config.slippage_model == "fixed_bps":
        slippage_cost = slippage_fixed_bps(price, notional, config.fixed_bps)
    elif config.slippage_model == "vol_scaled":
        vol = volatility if volatility is not None else 0.01  # Default 1% vol
        slippage_cost = slippage_vol_scaled(price, notional, vol, config.base_bps)
    else:
        # Unknown model, use fixed
        slippage_cost = slippage_fixed_bps(price, notional, config.fixed_bps)
    
    # Calculate latency penalty
    latency_bps = latency_penalty_bps(config.latency_ms)
    latency_cost = slippage_fixed_bps(price, notional, latency_bps)
    
    # Total cost
    total_cost = slippage_cost + latency_cost
    
    return total_cost


def calculate_volatility_from_history(price_history: List[float], window: int = 20) -> float:
    """
    Calculate rolling volatility from price history.
    
    Args:
        price_history: List of prices (oldest to newest)
        window: Rolling window size
        
    Returns:
        Volatility (standard deviation of returns)
    """
    if len(price_history) < 2:
        return 0.01  # Default 1% volatility
    
    # Convert to returns
    prices = np.array(price_history[-window:]) if len(price_history) >= window else np.array(price_history)
    returns = np.diff(prices) / prices[:-1]
    
    # Calculate standard deviation
    volatility = float(np.std(returns)) if len(returns) > 0 else 0.01
    
    return volatility


