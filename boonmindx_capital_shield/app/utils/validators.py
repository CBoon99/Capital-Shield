"""
Request Validators
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SignalRequest(BaseModel):
    """Request model for /signal endpoint"""
    asset: str = Field(..., description="Asset symbol (e.g., BTC, ETH)")
    price_history: List[float] = Field(..., description="Historical prices", min_length=1)
    volume_history: Optional[List[float]] = Field(None, description="Historical volumes")
    timestamp: Optional[str] = Field(None, description="Request timestamp (ISO format)")
    
    @field_validator('asset')
    @classmethod
    def validate_asset(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Asset symbol must be 1-10 characters')
        return v.upper()


class RiskRequest(BaseModel):
    """Request model for /risk endpoint"""
    asset: str = Field(..., description="Asset symbol")
    proposed_position_size: float = Field(..., gt=0, description="Proposed position size")
    current_equity: float = Field(..., gt=0, description="Current equity")
    price_history: List[float] = Field(..., min_items=1)
    leverage: float = Field(1.0, ge=1.0, le=10.0, description="Leverage multiplier")


class FilterRequest(BaseModel):
    """Request model for /filter endpoint"""
    asset: str = Field(..., description="Asset symbol")
    action: str = Field(..., description="Proposed action: BUY or SELL")
    price_history: List[float] = Field(..., min_length=1)
    volume_history: Optional[List[float]] = None
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        if v.upper() not in ['BUY', 'SELL']:
            raise ValueError('Action must be BUY or SELL')
        return v.upper()


class RegimeRequest(BaseModel):
    """Request model for /regime endpoint"""
    asset: str = Field(..., description="Asset symbol")
    price_history: List[float] = Field(..., min_length=1)
    volume_history: Optional[List[float]] = None


class MetricsRequest(BaseModel):
    """Request model for /metrics endpoint"""
    trades: List[dict] = Field(..., description="List of trade records")
    equity_curve: List[float] = Field(..., min_length=1, description="Equity curve values")

