"""
Risk Response Models
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional


class RiskResponse(BaseModel):
    """Response model for /risk endpoint"""
    risk_allowed: bool = Field(..., description="Whether trade is allowed")
    max_risk_fraction: float = Field(..., ge=0.0, le=1.0, description="Max risk fraction")
    recommended_position_size: float = Field(..., ge=0.0, description="Recommended position size")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score (0-1)")
    regime: Literal["BULL", "BEAR", "SIDEWAYS"] = Field(..., description="Market regime")
    warning: Optional[str] = Field(None, description="Risk warning if any")
    max_drawdown_estimate: float = Field(..., ge=0.0, le=1.0, description="Estimated max drawdown")
    timestamp: str = Field(..., description="Response timestamp")

