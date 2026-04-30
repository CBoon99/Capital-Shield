"""
Regime Response Models
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional


class RegimeSignals(BaseModel):
    """Regime detection signals"""
    sma_slope: float = Field(..., description="SMA slope indicator")
    rsi: float = Field(..., ge=0.0, le=100.0, description="RSI value")
    volatility: float = Field(..., ge=0.0, description="Volatility measure")
    momentum: float = Field(..., description="Momentum indicator")


class RegimeResponse(BaseModel):
    """Response model for /regime endpoint"""
    regime: Literal["BULL", "BEAR", "SIDEWAYS"] = Field(..., description="Market regime")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Regime confidence")
    signals: RegimeSignals = Field(..., description="Underlying signals")
    regime_stability: int = Field(..., ge=0, description="Consecutive periods in regime")
    last_change: Optional[str] = Field(None, description="Last regime change timestamp")
    timestamp: str = Field(..., description="Response timestamp")

