"""
Risk Endpoint
"""
import time
from fastapi import APIRouter, Request, Depends
from app.core.auth import verify_api_key
from app.core.rate_limit import check_rate_limit
from app.core.logging import log_request, setup_logging
from app.core.engine_adapter import get_risk
from app.models.risk import RiskResponse
from app.utils.validators import RiskRequest

router = APIRouter()
logger = setup_logging()


@router.post("/risk", response_model=RiskResponse)
async def assess_risk(
    request: Request,
    risk_request: RiskRequest,
    api_key_info: dict = Depends(verify_api_key)
):
    """
    Assess risk for a proposed trade
    
    Returns risk assessment from BearHunter engine (LIVE mode) or deterministic mock (MOCK mode)
    """
    start_time = time.time()
    
    # Check rate limit
    check_rate_limit(request)
    
    # Get risk assessment from engine adapter (handles MOCK/LIVE mode switching)
    response = get_risk(
        asset=risk_request.asset,
        proposed_position_size=risk_request.proposed_position_size,
        current_equity=risk_request.current_equity,
        price_history=risk_request.price_history,
        leverage=risk_request.leverage
    )
    
    # Log request
    latency_ms = (time.time() - start_time) * 1000
    log_request(logger, request, "/risk", latency_ms, api_key_info.get("name"))
    
    return response

