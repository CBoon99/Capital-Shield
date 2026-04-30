"""
Filter Response Models
"""
from pydantic import BaseModel, Field
from typing import Literal


class FilterResponse(BaseModel):
    """Response model for /filter endpoint"""
    trade_allowed: bool = Field(..., description="Whether trade is allowed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    regime: Literal["BULL", "BEAR", "SIDEWAYS"] = Field(..., description="Market regime")
    reason: str = Field(..., description="Reason for decision")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(..., description="Risk level")
    timestamp: str = Field(..., description="Response timestamp")

