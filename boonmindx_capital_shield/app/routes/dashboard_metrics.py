"""
Dashboard Metrics Endpoint

GET endpoint for dashboard to fetch current metrics state
"""
import time
from fastapi import APIRouter, Request
from app.core.logging import log_request, setup_logging
from app.core.safety_rails import _current_metrics, _system_health_status
from app.core.config import CAPITAL_SHIELD_MODE
from app.utils.time import get_current_timestamp

router = APIRouter()
logger = setup_logging()


@router.get("/dashboard/metrics")
async def get_dashboard_metrics(request: Request):
    """
    Get current metrics state for dashboard (no auth required for dashboard)
    
    Returns current metrics if available, or default values
    """
    start_time = time.time()
    
    # Get current metrics from safety rails
    metrics = _current_metrics or {}
    
    # Calculate pnl_percent from equity if available
    equity = metrics.get("equity", 100000.0)
    initial_equity = 100000.0  # Default initial equity
    pnl_percent = ((equity - initial_equity) / initial_equity) if initial_equity > 0 else 0.0
    
    # Build response
    response = {
        "equity": equity,
        "pnl_percent": metrics.get("pnl_percent", pnl_percent),
        "max_drawdown": metrics.get("max_drawdown", 0.0),
        "trades": metrics.get("total_trades", 0),
        "blocked_trades": metrics.get("blocked_trades", 0),
        "preset": "BALANCED",  # Default, could be read from config
        "capital_shield_mode": CAPITAL_SHIELD_MODE,
        "health_status": "ok" if _system_health_status else "unhealthy",
        "timestamp": get_current_timestamp()
    }
    
    # Log request
    latency_ms = (time.time() - start_time) * 1000
    log_request(logger, request, "/dashboard/metrics", latency_ms)
    
    return response

