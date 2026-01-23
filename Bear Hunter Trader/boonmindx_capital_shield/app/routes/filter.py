"""
Filter Endpoint - BoonMindX Capital Shield Trade Gatekeeper
"""
import time
from fastapi import APIRouter, Request, Depends
from app.core.auth import verify_api_key
from app.core.rate_limit import check_rate_limit
from app.core.logging import log_request, setup_logging
from app.core.engine_adapter import filter_trade as engine_filter_trade
from app.core.safety_rails import check_safety_rails
from app.models.filter import FilterResponse
from app.utils.validators import FilterRequest

router = APIRouter()
logger = setup_logging()


@router.post("/filter", response_model=FilterResponse)
async def filter_trade_endpoint(
    request: Request,
    filter_request: FilterRequest,
    api_key_info: dict = Depends(verify_api_key)
):
    """
    BoonMindX Capital Shield trade filter - Binary decision on whether trade is allowed
    
    This is the core BoonMindX Capital Shield endpoint that prevents bad trades.
    Even if engine says "GO", safety rails can veto the trade.
    """
    start_time = time.time()
    
    # Check rate limit
    check_rate_limit(request)
    
    # Get filter decision from engine adapter (handles MOCK/LIVE mode switching)
    engine_response = engine_filter_trade(
        asset=filter_request.asset,
        action=filter_request.action,
        price_history=filter_request.price_history,
        volume_history=filter_request.volume_history
    )
    
    # Apply safety rails (even if engine says "GO", BoonMindX Capital Shield can veto)
    safety_allowed, safety_reason = check_safety_rails(
        asset=filter_request.asset,
        action=filter_request.action,
        regime=engine_response.regime
    )
    
    # Final decision: engine decision AND safety rails must both allow
    final_trade_allowed = engine_response.trade_allowed and safety_allowed
    
    # Update reason if safety rails blocked the trade
    if not safety_allowed:
        reason = f"Safety rail blocked: {safety_reason}"
        confidence = min(engine_response.confidence, 0.3)  # Reduce confidence if blocked
    else:
        reason = engine_response.reason
        confidence = engine_response.confidence
    
    response = FilterResponse(
        trade_allowed=final_trade_allowed,
        confidence=confidence,
        regime=engine_response.regime,
        reason=reason,
        risk_level=engine_response.risk_level,
        timestamp=engine_response.timestamp
    )
    
    # Log request
    latency_ms = (time.time() - start_time) * 1000
    log_request(logger, request, "/filter", latency_ms, api_key_info.get("name"))
    
    return response

