"""
Signal Response Models
"""
from pydantic import BaseModel, Field
from typing import Literal


class SignalResponse(BaseModel):
    """Response model for /signal endpoint"""
    signal: Literal["BUY", "SELL", "HOLD"] = Field(..., description="Trading signal")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    regime: Literal["BULL", "BEAR", "SIDEWAYS"] = Field(..., description="Market regime")
    regime_confidence: float = Field(..., ge=0.0, le=1.0, description="Regime confidence")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score (0-1)")
    reason: str = Field(..., description="Reason for signal")
    timestamp: str = Field(..., description="Response timestamp (ISO format)")

