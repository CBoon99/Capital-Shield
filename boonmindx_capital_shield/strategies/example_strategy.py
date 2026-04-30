"""
Example Strategy — DEMO ONLY

This is a demonstration strategy plugin. It is NOT a production strategy
and makes NO claims about profitability, returns, or performance.

This strategy is provided solely to demonstrate the plugin interface.
"""

from typing import Any, Dict

from .strategy_base import Action, SignalDecision, StrategyBase


class ExampleStrategy(StrategyBase):
    """
    Example strategy plugin (DEMO ONLY).

    This strategy demonstrates the plugin interface with simple,
    non-financial logic. It is NOT intended for production use.

    WARNING: This is a demonstration strategy only. It makes no
    claims about profitability, returns, or performance.
    """

    @property
    def name(self) -> str:
        """Strategy name."""
        return "example_demo"

    @property
    def version(self) -> str:
        """Strategy version."""
        return "1.0.0"

    def generate_signal(self, market_snapshot: Dict[str, Any]) -> SignalDecision:
        """
        Generate a signal based on market data (DEMO ONLY).

        This implementation uses simple, non-financial logic for
        demonstration purposes only.

        Args:
            market_snapshot: Dictionary containing market data:
                - price_history: List of prices (required)
                - volume_history: List of volumes (optional)
                - asset: Asset symbol (optional)
                - rsi: RSI value (optional, for demo)

        Returns:
            SignalDecision with action, confidence, reason, and metadata

        Raises:
            ValueError: If market_snapshot is invalid
        """
        # Validate required fields
        if not isinstance(market_snapshot, dict):
            raise ValueError("market_snapshot must be a dictionary")

        price_history = market_snapshot.get("price_history")
        if not price_history or not isinstance(price_history, list) or len(price_history) < 2:
            return SignalDecision(
                action=Action.HOLD,
                confidence=0.5,
                reason="Insufficient price data for demo strategy",
                meta={"demo": True, "error": "insufficient_data"},
            )

        # Demo logic: Simple RSI-based example (NOT production logic)
        # This is for demonstration only and makes no performance claims
        rsi = market_snapshot.get("rsi")
        asset = market_snapshot.get("asset", "UNKNOWN")

        if rsi is not None and isinstance(rsi, (int, float)):
            # Demo logic: If RSI exists and is below 30, suggest BUY
            # This is purely for demonstration and makes no claims
            if rsi < 30:
                return SignalDecision(
                    action=Action.BUY,
                    confidence=0.6,
                    reason=f"Demo strategy: RSI below 30 for {asset} (DEMO ONLY)",
                    meta={
                        "demo": True,
                        "rsi": rsi,
                        "asset": asset,
                        "warning": "This is a demonstration strategy only",
                    },
                )
            elif rsi > 70:
                return SignalDecision(
                    action=Action.SELL,
                    confidence=0.6,
                    reason=f"Demo strategy: RSI above 70 for {asset} (DEMO ONLY)",
                    meta={
                        "demo": True,
                        "rsi": rsi,
                        "asset": asset,
                        "warning": "This is a demonstration strategy only",
                    },
                )

        # Default: HOLD
        return SignalDecision(
            action=Action.HOLD,
            confidence=0.5,
            reason=f"Demo strategy: No clear signal for {asset} (DEMO ONLY)",
            meta={
                "demo": True,
                "asset": asset,
                "warning": "This is a demonstration strategy only",
            },
        )
