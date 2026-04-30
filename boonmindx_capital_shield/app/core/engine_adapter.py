"""
Engine Adapter Layer - Clean abstraction between API and BearHunter engine
"""
import os
import sys
from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np

from app.core.config import ENGINE_MODE, BEARHUNTER_ENGINE_PATH
from app.models.signal import SignalResponse
from app.models.risk import RiskResponse
from app.models.filter import FilterResponse
from app.models.regime import RegimeResponse, RegimeSignals
from app.utils.time import get_current_timestamp

# BearHunter engine imports (only in LIVE mode)
_bear_detector = None
_engine_initialized = False


def _init_bearhunter_engine():
    """Initialize BearHunter engine (only called in LIVE mode)"""
    global _bear_detector, _engine_initialized
    
    if _engine_initialized:
        return
    
    if ENGINE_MODE == "LIVE":
        try:
            # Add BearHunter engine path to sys.path
            engine_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../..", BEARHUNTER_ENGINE_PATH)
            )
            if engine_path not in sys.path:
                sys.path.insert(0, engine_path)
            
            # Import BearHunter components
            from bear_detector import BearDetector
            
            # Initialize detector with default params
            _bear_detector = BearDetector()
            _engine_initialized = True
            
        except Exception as e:
            # Fallback to MOCK if engine unavailable
            print(f"Warning: BearHunter engine unavailable ({e}), falling back to MOCK mode")
            _engine_initialized = True  # Prevent retry loops
            _bear_detector = None
    
    _engine_initialized = True


def get_signal(
    asset: str,
    price_history: List[float],
    volume_history: Optional[List[float]] = None
) -> SignalResponse:
    """
    Get trading signal from BearHunter engine or MOCK
    
    Args:
        asset: Asset symbol
        price_history: Historical prices (oldest to newest)
        volume_history: Optional historical volumes
        
    Returns:
        SignalResponse with signal, confidence, regime, etc.
    """
    _init_bearhunter_engine()
    
    if ENGINE_MODE == "LIVE" and _bear_detector is not None:
        # LIVE mode: Use BearHunter engine
        try:
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
            
            reason = f"BearHunter engine: {regime} regime detected, {action}"
            
            return SignalResponse(
                signal=signal,
                confidence=float(confidence),
                regime=regime,
                regime_confidence=float(regime_confidence),
                risk_score=float(risk_score),
                reason=reason,
                timestamp=get_current_timestamp()
            )
            
        except Exception as e:
            # Fallback to MOCK on error
            print(f"Error in LIVE mode signal generation: {e}")
            return _get_mock_signal(asset, price_history)
    
    else:
        # MOCK mode: Deterministic mock logic
        return _get_mock_signal(asset, price_history)


def _get_mock_signal(asset: str, price_history: List[float]) -> SignalResponse:
    """MOCK mode signal generation (Phase 1 behavior)"""
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
    
    risk_score = min(abs(price_change) * 2, 1.0)
    
    return SignalResponse(
        signal=signal,
        confidence=confidence,
        regime=regime,
        regime_confidence=0.90,
        risk_score=risk_score,
        reason=f"Price change: {price_change:.2%}, deterministic signal generation",
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
    Get risk assessment from BearHunter engine or MOCK
    
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
    
    if ENGINE_MODE == "LIVE" and _bear_detector is not None:
        # LIVE mode: Use BearHunter engine
        try:
            regime_result = _bear_detector.get_regime(price_history)
            regime = regime_result['regime']
            volatility = regime_result.get('volatility', 0.0)
            
            # Calculate risk metrics
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
            
        except Exception as e:
            print(f"Error in LIVE mode risk assessment: {e}")
            return _get_mock_risk(asset, proposed_position_size, current_equity, price_history, leverage)
    
    else:
        # MOCK mode
        return _get_mock_risk(asset, proposed_position_size, current_equity, price_history, leverage)


def _get_mock_risk(
    asset: str,
    proposed_position_size: float,
    current_equity: float,
    price_history: List[float],
    leverage: float
) -> RiskResponse:
    """MOCK mode risk assessment (Phase 1 behavior)"""
    volatility = abs((price_history[-1] - price_history[0]) / price_history[0]) if len(price_history) > 1 else 0.1
    
    max_risk_fraction = 0.05
    risk_score = min(volatility * 2, 1.0)
    
    price_change = (price_history[-1] - price_history[0]) / price_history[0] if len(price_history) > 1 else 0
    if price_change > 0.03:
        regime = "BULL"
    elif price_change < -0.03:
        regime = "BEAR"
    else:
        regime = "SIDEWAYS"
    
    recommended_size = current_equity * max_risk_fraction * leverage
    risk_allowed = risk_score < 0.5
    
    warning = None
    if risk_score > 0.7:
        warning = "High volatility detected - reduce position size"
    elif regime == "BEAR":
        warning = "Bear regime detected - consider defensive positioning"
    
    max_drawdown_estimate = min(volatility * 1.5, 0.20)
    
    return RiskResponse(
        risk_allowed=risk_allowed,
        max_risk_fraction=max_risk_fraction,
        recommended_position_size=recommended_size,
        risk_score=risk_score,
        regime=regime,
        warning=warning,
        max_drawdown_estimate=max_drawdown_estimate,
        timestamp=get_current_timestamp()
    )


def filter_trade(
    asset: str,
    action: str,
    price_history: List[float],
    volume_history: Optional[List[float]] = None
) -> FilterResponse:
    """
    Shield-Class trade filter using BearHunter engine or MOCK
    
    Args:
        asset: Asset symbol
        action: Proposed action (BUY or SELL)
        price_history: Historical prices
        volume_history: Optional historical volumes
        
    Returns:
        FilterResponse with trade_allowed decision
    """
    _init_bearhunter_engine()
    
    if ENGINE_MODE == "LIVE" and _bear_detector is not None:
        # LIVE mode: Use BearHunter engine
        try:
            regime_result = _bear_detector.get_regime(price_history, volume_history)
            regime = regime_result['regime']
            confidence_dict = regime_result['confidence']
            
            # Determine if trade is allowed based on regime and action
            if action == "BUY":
                # Allow BUY in BULL or SIDEWAYS with positive momentum
                trade_allowed = regime in ["BULL", "SIDEWAYS"]
                confidence = confidence_dict.get('bull', 0.7) if trade_allowed else confidence_dict.get('bear', 0.3)
                reason = f"BearHunter: {regime} regime - BUY {'allowed' if trade_allowed else 'blocked'}"
                risk_level = "LOW" if trade_allowed and regime == "BULL" else "MEDIUM" if trade_allowed else "HIGH"
            else:  # SELL
                # Allow SELL in BEAR or when taking profits
                trade_allowed = regime == "BEAR" or confidence_dict.get('bear', 0) > 0.5
                confidence = confidence_dict.get('bear', 0.7) if trade_allowed else confidence_dict.get('bull', 0.3)
                reason = f"BearHunter: {regime} regime - SELL {'allowed' if trade_allowed else 'blocked'}"
                risk_level = "LOW" if trade_allowed else "MEDIUM"
            
            return FilterResponse(
                trade_allowed=trade_allowed,
                confidence=float(confidence),
                regime=regime,
                reason=reason,
                risk_level=risk_level,
                timestamp=get_current_timestamp()
            )
            
        except Exception as e:
            print(f"Error in LIVE mode filter: {e}")
            return _get_mock_filter(asset, action, price_history)
    
    else:
        # MOCK mode
        return _get_mock_filter(asset, action, price_history)


def _get_mock_filter(asset: str, action: str, price_history: List[float]) -> FilterResponse:
    """MOCK mode filter (Phase 1 behavior)"""
    price_change = (price_history[-1] - price_history[0]) / price_history[0] if len(price_history) > 1 else 0
    
    if price_change > 0.03:
        regime = "BULL"
    elif price_change < -0.03:
        regime = "BEAR"
    else:
        regime = "SIDEWAYS"
    
    if action == "BUY":
        trade_allowed = regime in ["BULL", "SIDEWAYS"] and price_change > -0.02
        confidence = 0.88 if trade_allowed else 0.45
        reason = "Clean MA10 breakout, RSI turning up, ADX > 25" if trade_allowed else "Bear regime or negative momentum detected"
        risk_level = "LOW" if trade_allowed and regime == "BULL" else "MEDIUM" if trade_allowed else "HIGH"
    else:  # SELL
        trade_allowed = regime == "BEAR" or price_change > 0.05
        confidence = 0.85 if trade_allowed else 0.50
        reason = "Bear regime or profit-taking signal" if trade_allowed else "Bull regime - consider holding"
        risk_level = "LOW" if trade_allowed else "MEDIUM"
    
    return FilterResponse(
        trade_allowed=trade_allowed,
        confidence=confidence,
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
    Get market regime from BearHunter engine or MOCK
    
    Args:
        asset: Asset symbol
        price_history: Historical prices
        volume_history: Optional historical volumes
        
    Returns:
        RegimeResponse with regime classification
    """
    _init_bearhunter_engine()
    
    if ENGINE_MODE == "LIVE" and _bear_detector is not None:
        # LIVE mode: Use BearHunter engine
        try:
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
                last_change=None,  # Could track regime changes if needed
                timestamp=get_current_timestamp()
            )
            
        except Exception as e:
            print(f"Error in LIVE mode regime detection: {e}")
            return _get_mock_regime(asset, price_history)
    
    else:
        # MOCK mode
        return _get_mock_regime(asset, price_history)


def _get_mock_regime(asset: str, price_history: List[float]) -> RegimeResponse:
    """MOCK mode regime detection (Phase 1 behavior)"""
    if len(price_history) < 2:
        regime = "SIDEWAYS"
        confidence = 0.5
    else:
        price_change = (price_history[-1] - price_history[0]) / price_history[0]
        
        if price_change > 0.03:
            regime = "BULL"
            confidence = 0.85
        elif price_change < -0.03:
            regime = "BEAR"
            confidence = 0.80
        else:
            regime = "SIDEWAYS"
            confidence = 0.70
    
    signals = RegimeSignals(
        sma_slope=price_change * 10 if len(price_history) > 1 else 0.0,
        rsi=50.0 + (price_change * 20) if len(price_history) > 1 else 50.0,
        volatility=abs(price_change) if len(price_history) > 1 else 0.0,
        momentum=price_change if len(price_history) > 1 else 0.0
    )
    
    return RegimeResponse(
        regime=regime,
        confidence=confidence,
        signals=signals,
        regime_stability=1,
        last_change=None,
        timestamp=get_current_timestamp()
    )

