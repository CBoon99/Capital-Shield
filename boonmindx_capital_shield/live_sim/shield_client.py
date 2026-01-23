"""
BoonMindX Capital Shield Client for Live Simulation

Direct in-process calls to BoonMindX Capital Shield adapter and safety rails (no HTTP)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.engine_adapter import (
    get_signal,
    get_risk,
    filter_trade,
    get_regime
)
from app.core.safety_rails import (
    check_safety_rails,
    set_system_health,
    set_current_metrics
)
from app.models.signal import SignalResponse
from app.models.filter import FilterResponse
from app.models.risk import RiskResponse
from app.models.regime import RegimeResponse


class CapitalShieldClient:
    """
    Client for interacting with BoonMindX Capital Shield API components directly
    
    This simulates what an external client would see, but uses
    direct function calls instead of HTTP for performance.
    """
    
    def __init__(self, engine_mode: str = "MOCK", capital_shield_mode: str = "PERMISSIVE"):
        """
        Initialize BoonMindX Capital Shield client
        
        Args:
            engine_mode: "MOCK" or "LIVE"
            capital_shield_mode: "PERMISSIVE" or "STRICT"
        """
        self.engine_mode = engine_mode
        self.capital_shield_mode = capital_shield_mode
        self._blocked_trades = []  # Track blocked trades for reporting
        self._preset_name = None  # Will be set by runner for FP tracking
    
    def get_signal(
        self,
        asset: str,
        price_history: List[float],
        volume_history: Optional[List[float]] = None
    ) -> SignalResponse:
        """
        Get trading signal for an asset
        
        Args:
            asset: Asset symbol
            price_history: Historical prices (oldest to newest)
            volume_history: Optional historical volumes
            
        Returns:
            SignalResponse with signal, confidence, regime, etc.
        """
        return get_signal(asset, price_history, volume_history)
    
    def filter_trade(
        self,
        asset: str,
        action: str,
        price_history: List[float],
        volume_history: Optional[List[float]] = None,
        current_price: Optional[float] = None,
        current_equity: Optional[float] = None,
        timestamp: Optional[str] = None
    ) -> FilterResponse:
        """
        Check if trade is allowed (BoonMindX Capital Shield filter)
        
        This includes both engine decision and safety rails.
        
        Args:
            asset: Asset symbol
            action: "BUY" or "SELL"
            price_history: Historical prices
            volume_history: Optional historical volumes
            current_price: Current price (for FP tracking)
            current_equity: Current equity (for FP tracking)
            timestamp: Timestamp string (for FP tracking)
            
        Returns:
            FilterResponse with trade_allowed decision
        """
        # Get filter decision from engine adapter
        response = filter_trade(asset, action, price_history, volume_history)
        
        # Safety rails are already applied in filter_trade endpoint,
        # but we can add additional checks here if needed
        
        # Track blocked trades with detailed information for FP classification
        if not response.trade_allowed:
            # Determine which rail triggered the block
            rail_triggered = "unknown"
            reason_lower = response.reason.lower()
            if "drawdown" in reason_lower:
                rail_triggered = "drawdown"
            elif "regime" in reason_lower or "bear" in reason_lower:
                rail_triggered = "regime"
            elif "health" in reason_lower:
                rail_triggered = "health"
            elif "preset" in reason_lower or "threshold" in reason_lower:
                rail_triggered = "preset"
            
            self._blocked_trades.append({
                'asset': asset,
                'action': action,
                'rail': rail_triggered,
                'preset': self._preset_name or 'unknown',
                'reason': response.reason,
                'regime': response.regime,
                'confidence': response.confidence,
                'timestamp': timestamp or datetime.now().isoformat(),
                'price': current_price or (price_history[-1] if price_history else None),
                'equity': current_equity
            })
        
        return response
    
    def get_regime(
        self,
        asset: str,
        price_history: List[float],
        volume_history: Optional[List[float]] = None
    ) -> RegimeResponse:
        """
        Get market regime classification
        
        Args:
            asset: Asset symbol
            price_history: Historical prices
            volume_history: Optional historical volumes
            
        Returns:
            RegimeResponse with regime, confidence, signals
        """
        return get_regime(asset, price_history, volume_history)
    
    def get_risk(
        self,
        asset: str,
        proposed_position_size: float,
        current_equity: float,
        price_history: List[float],
        leverage: float = 1.0
    ) -> RiskResponse:
        """
        Get risk assessment for a proposed trade
        
        Args:
            asset: Asset symbol
            proposed_position_size: Proposed position size
            current_equity: Current equity
            price_history: Historical prices
            leverage: Leverage multiplier
            
        Returns:
            RiskResponse with risk assessment
        """
        return get_risk(
            asset,
            proposed_position_size,
            current_equity,
            price_history,
            leverage
        )
    
    def get_blocked_trades(self) -> List[Dict[str, Any]]:
        """Get list of trades blocked by BoonMindX Capital Shield"""
        return self._blocked_trades.copy()
    
    def reset_blocked_trades(self):
        """Reset blocked trades list"""
        self._blocked_trades = []
    
    def set_system_health(self, healthy: bool):
        """Set system health status (for testing)"""
        set_system_health(healthy)
    
    def set_current_metrics(self, metrics: Optional[Dict[str, Any]]):
        """Set current metrics for safety rail checks"""
        set_current_metrics(metrics)
    
    def set_preset_name(self, preset_name: str):
        """Set preset name for FP tracking"""
        self._preset_name = preset_name

