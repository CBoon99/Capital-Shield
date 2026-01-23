"""
Strategy Integration — BoonMindX Capital Shield

Internal integration point for strategy plugins.
"""

from typing import Any, Dict, Optional

from .registry import get_strategy
from .strategy_base import SignalDecision


def generate_strategy_signal(
    strategy_name: str, market_snapshot: Dict[str, Any]
) -> Optional[SignalDecision]:
    """
    Generate a signal using a registered strategy plugin.

    This is an internal integration function. Strategies generate signals,
    which are then evaluated by Capital Shield's safety rails.

    Args:
        strategy_name: Name of registered strategy
        market_snapshot: Dictionary containing market data:
            - price_history: List of prices
            - volume_history: List of volumes (optional)
            - asset: Asset symbol (optional)
            - Additional strategy-specific fields (optional)

    Returns:
        SignalDecision if strategy found and signal generated, None otherwise

    Example:
        >>> market_data = {
        ...     "price_history": [100, 102, 101, 105, 103],
        ...     "volume_history": [1000, 1200, 1100, 1300, 1250],
        ...     "asset": "BTC"
        ... }
        >>> signal = generate_strategy_signal("example_demo", market_data)
        >>> if signal:
        ...     print(f"Action: {signal.action}, Confidence: {signal.confidence}")
    """
    strategy = get_strategy(strategy_name)
    if not strategy:
        return None

    try:
        return strategy.generate_signal(market_snapshot)
    except Exception as e:
        # Log error but don't expose internal details
        # In production, this would use proper logging
        return None
