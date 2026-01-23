"""
BearHunter Bridge - Direct engine calls for baseline mode

This provides direct access to BearHunter engine without Shield safety rails.
Used for baseline comparisons in live simulations.
"""
import os
import sys
from typing import List, Optional
from app.models.signal import SignalResponse
from app.models.risk import RiskResponse
from app.models.filter import FilterResponse
from app.models.regime import RegimeResponse, RegimeSignals
from app.utils.time import get_current_timestamp

# BearHunter engine instance
_bear_detector = None
_engine_initialized = False


def _init_bearhunter_engine():
    """Initialize BearHunter engine"""
    global _bear_detector, _engine_initialized
    
    if _engine_initialized:
        return
    
    try:
        # Add BearHunter engine path to sys.path
        # Try multiple possible paths
        possible_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "testing_area")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../testing_area")),
            "testing_area",  # Relative from project root
        ]
        
        engine_path = None
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "bear_detector.py")):
                engine_path = os.path.abspath(path)
                break
        
        if engine_path and engine_path not in sys.path:
            sys.path.insert(0, engine_path)
        
        # Import BearHunter components
        from bear_detector import BearDetector
        
        # Initialize detector with default params
        _bear_detector = BearDetector()
        _engine_initialized = True
        
    except Exception as e:
        # For testing, allow graceful fallback
        import traceback
        print(f"Warning: BearHunter engine unavailable ({e})")
        print(traceback.format_exc())
        _engine_initialized = True
        _bear_detector = None
        # Don't raise - allow tests to proceed with mocked data
    
    _engine_initialized = True


def get_signal(
    asset: str,
    price_history: List[float],
    volume_history: Optional[List[float]] = None
) -> SignalResponse:
    """
    Get trading signal directly from BearHunter engine (no Shield)
    
    Args:
        asset: Asset symbol
        price_history: Historical prices (oldest to newest)
        volume_history: Optional historical volumes
        
    Returns:
        SignalResponse with signal, confidence, regime, etc.
    """
    _init_bearhunter_engine()
    
    if _bear_detector is None:
        # Fallback to simple mock for testing when engine unavailable
        # In production, this should raise an error
        price_change = (price_history[-1] - price_history[0]) / price_history[0] if len(price_history) > 1 else 0
        if price_change > 0.05:
            signal = "BUY"
            confidence = 0.85
            regime = "BULL"
        elif price_change < -0.05:
            signal = "SELL"
            confidence = 0.80
            regime = "BEAR"
        else:
            signal = "HOLD"
            confidence = 0.60
            regime = "SIDEWAYS"
        
        return SignalResponse(
            signal=signal,
            confidence=confidence,
            regime=regime,
            regime_confidence=0.90,
            risk_score=min(abs(price_change) * 2, 1.0),
            reason=f"Baseline fallback: {regime} regime (engine unavailable)",
            timestamp=get_current_timestamp()
        )
    
    # Get regime from BearHunter
    regime_result = _bear_detector.get_regime(price_history, volume_history)
    
    regime = regime_result['regime']
    confidence_dict = regime_result['confidence']
    
    # Map BearHunter action to signal
    action = regime_result['action']
    if action == 'TRADE_AGGRESSIVE':
        signal = "BUY"
        confidence = confidence_dict.get('bull', 0.7)
    elif action == 'TRADE_DEFENSIVE':
        signal = "SELL"
        confidence = confidence_dict.get('bear', 0.7)
    else:  # TRADE_MODERATE
        signal = "HOLD"
        confidence = confidence_dict.get('sideways', 0.6)
    
    # Calculate risk score from volatility
    volatility = regime_result.get('volatility', 0.0)
    risk_score = min(volatility * 10, 1.0)  # Scale to 0-1
    
    # Get regime confidence (max of bull/bear/sideways)
    regime_confidence = max(
        confidence_dict.get('bull', 0),
        confidence_dict.get('bear', 0),
        confidence_dict.get('sideways', 0)
    )
    
    reason = f"BearHunter baseline: {regime} regime detected, {action}"
    
    return SignalResponse(
        signal=signal,
        confidence=float(confidence),
        regime=regime,
        regime_confidence=float(regime_confidence),
        risk_score=float(risk_score),
        reason=reason,
        timestamp=get_current_timestamp()
    )


def filter_trade(
    asset: str,
    action: str,
    price_history: List[float],
    volume_history: Optional[List[float]] = None
) -> FilterResponse:
    """
    Check if trade is allowed (baseline - no safety rails)
    
    In baseline mode, we only check the engine signal, no safety rails.
    
    Args:
        asset: Asset symbol
        action: Proposed action (BUY or SELL)
        price_history: Historical prices
        volume_history: Optional historical volumes
        
    Returns:
        FilterResponse with trade_allowed decision (always allows if signal matches)
    """
    _init_bearhunter_engine()
    
    if _bear_detector is None:
        # Fallback for testing
        signal_response = get_signal(asset, price_history, volume_history)
        trade_allowed = (action == "BUY" and signal_response.signal == "BUY") or \
                       (action == "SELL" and signal_response.signal == "SELL")
        return FilterResponse(
            trade_allowed=trade_allowed,
            confidence=signal_response.confidence,
            regime=signal_response.regime,
            reason=f"Baseline fallback: {'allowed' if trade_allowed else 'blocked by signal'}",
            risk_level="LOW" if trade_allowed else "MEDIUM",
            timestamp=get_current_timestamp()
        )
    
    # Get regime from BearHunter
    regime_result = _bear_detector.get_regime(price_history, volume_history)
    regime = regime_result['regime']
    confidence_dict = regime_result['confidence']
    
    # Get signal
    signal_response = get_signal(asset, price_history, volume_history)
    
    # In baseline mode, allow trade if signal matches action
    # No safety rails - pure engine decision
    if action == "BUY":
        trade_allowed = signal_response.signal == "BUY"
        confidence = confidence_dict.get('bull', 0.7) if trade_allowed else confidence_dict.get('bear', 0.3)
        reason = f"Baseline: {regime} regime - BUY {'allowed' if trade_allowed else 'blocked by signal'}"
        risk_level = "LOW" if trade_allowed and regime == "BULL" else "MEDIUM" if trade_allowed else "HIGH"
    else:  # SELL
        trade_allowed = signal_response.signal == "SELL"
        confidence = confidence_dict.get('bear', 0.7) if trade_allowed else confidence_dict.get('bull', 0.3)
        reason = f"Baseline: {regime} regime - SELL {'allowed' if trade_allowed else 'blocked by signal'}"
        risk_level = "LOW" if trade_allowed else "MEDIUM"
    
    return FilterResponse(
        trade_allowed=trade_allowed,
        confidence=float(confidence),
        regime=regime,
        reason=reason,
        risk_level=risk_level,
        timestamp=get_current_timestamp()
    )


def get_regime(
    asset: str,
    price_history: List[float],
    volume_history: Optional[List[float]] = None
) -> RegimeResponse:
    """
    Get market regime directly from BearHunter engine
    
    Args:
        asset: Asset symbol
        price_history: Historical prices
        volume_history: Optional historical volumes
        
    Returns:
        RegimeResponse with regime classification
    """
    _init_bearhunter_engine()
    
    if _bear_detector is None:
        # Fallback for testing
        signal_response = get_signal(asset, price_history, volume_history)
        from app.models.regime import RegimeSignals
        return RegimeResponse(
            regime=signal_response.regime,
            confidence=signal_response.regime_confidence,
            signals=RegimeSignals(
                sma_slope=0.0,
                rsi=50.0,
                volatility=0.0,
                momentum=0.0
            ),
            regime_stability=1,
            last_change=None,
            timestamp=get_current_timestamp()
        )
    
    regime_result = _bear_detector.get_regime(price_history, volume_history)
    
    regime = regime_result['regime']
    confidence_dict = regime_result['confidence']
    
    # Get regime confidence (max of bull/bear/sideways)
    confidence = max(
        confidence_dict.get('bull', 0),
        confidence_dict.get('bear', 0),
        confidence_dict.get('sideways', 0)
    )
    
    # Extract signals
    signals = RegimeSignals(
        sma_slope=regime_result.get('sma_short_slope', 0.0),
        rsi=regime_result.get('rsi', 50.0),
        volatility=regime_result.get('volatility', 0.0),
        momentum=regime_result.get('momentum', 0.0)
    )
    
    regime_stability = regime_result.get('regime_stability_counter', 0)
    
    return RegimeResponse(
        regime=regime,
        confidence=float(confidence),
        signals=signals,
        regime_stability=int(regime_stability),
        last_change=None,
        timestamp=get_current_timestamp()
    )


def get_risk(
    asset: str,
    proposed_position_size: float,
    current_equity: float,
    price_history: List[float],
    leverage: float = 1.0
) -> RiskResponse:
    """
    Get risk assessment directly from BearHunter engine (no Shield)
    
    Args:
        asset: Asset symbol
        proposed_position_size: Proposed position size
        current_equity: Current equity
        price_history: Historical prices
        leverage: Leverage multiplier
        
    Returns:
        RiskResponse with risk assessment
    """
    _init_bearhunter_engine()
    
    if _bear_detector is None:
        # Fallback for testing
        signal_response = get_signal(asset, price_history)
        volatility = abs((price_history[-1] - price_history[0]) / price_history[0]) if len(price_history) > 1 else 0.1
        risk_score = min(volatility * 2, 1.0)
        max_risk_fraction = 0.05
        recommended_size = current_equity * max_risk_fraction * leverage
        return RiskResponse(
            risk_allowed=risk_score < 0.5,
            max_risk_fraction=max_risk_fraction,
            recommended_position_size=recommended_size,
            risk_score=risk_score,
            regime=signal_response.regime,
            warning=None,
            max_drawdown_estimate=min(volatility * 1.5, 0.20),
            timestamp=get_current_timestamp()
        )
    
    regime_result = _bear_detector.get_regime(price_history)
    regime = regime_result['regime']
    volatility = regime_result.get('volatility', 0.0)
    
    # Calculate risk metrics (baseline - no safety rails)
    risk_score = min(volatility * 10, 1.0)
    max_risk_fraction = 0.05  # 5% max risk
    
    # Adjust risk based on regime
    if regime == "BEAR":
        max_risk_fraction *= 0.5  # Reduce risk in bear markets
        warning = "Bear regime detected - defensive positioning recommended"
    elif regime == "BULL":
        warning = None
    else:
        warning = "Sideways market - moderate risk"
    
    # Calculate recommended position size
    recommended_size = current_equity * max_risk_fraction * leverage
    
    # Risk allowed if risk score < 0.5 and not extreme volatility
    risk_allowed = risk_score < 0.5 and volatility < 0.1
    
    max_drawdown_estimate = min(volatility * 1.5, 0.20)
    
    return RiskResponse(
        risk_allowed=risk_allowed,
        max_risk_fraction=max_risk_fraction,
        recommended_position_size=recommended_size,
        risk_score=float(risk_score),
        regime=regime,
        warning=warning,
        max_drawdown_estimate=float(max_drawdown_estimate),
        timestamp=get_current_timestamp()
    )

