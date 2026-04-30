"""
Metrics Response Models
"""
from pydantic import BaseModel, Field


class MetricsResponse(BaseModel):
    """Response model for /metrics endpoint"""
    sharpe: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., le=0.0, description="Maximum drawdown (negative)")
    win_rate: float = Field(..., ge=0.0, le=1.0, description="Win rate (0-1)")
    total_pnl: float = Field(..., description="Total profit/loss")
    pnl_percent: float = Field(..., description="P/L as percentage")
    trades: int = Field(..., ge=0, description="Number of trades")
    timestamp: str = Field(..., description="Response timestamp")

