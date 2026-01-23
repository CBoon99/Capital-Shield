"""
Metrics Endpoint
"""
import time
from fastapi import APIRouter, Request, Depends
from app.core.auth import verify_api_key
from app.core.rate_limit import check_rate_limit
from app.core.logging import log_request, setup_logging
from app.core.safety_rails import set_current_metrics
from app.models.metrics import MetricsResponse
from app.utils.validators import MetricsRequest
from app.utils.time import get_current_timestamp

router = APIRouter()
logger = setup_logging()


@router.post("/metrics", response_model=MetricsResponse)
async def get_metrics(
    request: Request,
    metrics_request: MetricsRequest,
    api_key_info: dict = Depends(verify_api_key)
):
    """
    Calculate performance metrics from trade history
    
    Returns Sharpe ratio, max drawdown, win rate, etc.
    """
    start_time = time.time()
    
    # Check rate limit
    check_rate_limit(request)
    
    # Mock deterministic metrics calculation
    # Phase 1: Deterministic mock, Phase 2: Connect to BearHunter engine
    trades = metrics_request.trades
    equity_curve = metrics_request.equity_curve
    
    if not trades or len(equity_curve) < 2:
        # Return default metrics if insufficient data
        response = MetricsResponse(
            sharpe=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_pnl=0.0,
            pnl_percent=0.0,
            trades=0,
            timestamp=get_current_timestamp()
        )
    else:
        # Calculate metrics from trades
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        total_trades = len(trades)
        win_rate = wins / total_trades if total_trades > 0 else 0.0
        
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        initial_equity = equity_curve[0] if equity_curve else 100000
        pnl_percent = (total_pnl / initial_equity) * 100 if initial_equity > 0 else 0.0
        
        # Calculate max drawdown
        peak = equity_curve[0]
        max_dd = 0.0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = (equity - peak) / peak if peak > 0 else 0.0
            max_dd = min(max_dd, dd)
        
        # Calculate Sharpe (simplified)
        if len(equity_curve) > 1:
            returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] 
                      for i in range(1, len(equity_curve))]
            avg_return = sum(returns) / len(returns) if returns else 0.0
            std_return = (sum((r - avg_return)**2 for r in returns) / len(returns))**0.5 if returns else 0.0
            sharpe = (avg_return / std_return) * (252**0.5) if std_return > 0 else 0.0
        else:
            sharpe = 0.0
        
        # Use fixed timestamp for determinism (Phase 1)
        # Phase 2: Use actual request timestamp
        fixed_timestamp = "2025-11-13T00:00:00Z"
        
        response = MetricsResponse(
            sharpe=round(sharpe, 2),
            max_drawdown=round(max_dd, 4),
            win_rate=round(win_rate, 4),
            total_pnl=round(total_pnl, 2),
            pnl_percent=round(pnl_percent, 2),
            trades=total_trades,
            timestamp=fixed_timestamp
        )
        
        # Update safety rails with current metrics (for max drawdown checks)
        set_current_metrics({
            "max_drawdown": max_dd,
            "sharpe": sharpe,
            "win_rate": win_rate,
            "total_pnl": total_pnl
        })
    
    # If no metrics available, clear safety rails
    if not trades or len(equity_curve) < 2:
        set_current_metrics(None)
    
    # Log request
    latency_ms = (time.time() - start_time) * 1000
    log_request(logger, request, "/metrics", latency_ms, api_key_info.get("name"))
    
    return response

