"""
Regime Endpoint
"""
import time
from fastapi import APIRouter, Request, Depends
from app.core.auth import verify_api_key
from app.core.rate_limit import check_rate_limit
from app.core.logging import log_request, setup_logging
from app.core.engine_adapter import get_regime
from app.models.regime import RegimeResponse
from app.utils.validators import RegimeRequest

router = APIRouter()
logger = setup_logging()


@router.post("/regime", response_model=RegimeResponse)
async def get_regime_endpoint(
    request: Request,
    regime_request: RegimeRequest,
    api_key_info: dict = Depends(verify_api_key)
):
    """
    Get market regime classification for an asset
    
    Returns regime from BearHunter engine (LIVE mode) or deterministic mock (MOCK mode)
    """
    start_time = time.time()
    
    # Check rate limit
    check_rate_limit(request)
    
    # Get regime from engine adapter (handles MOCK/LIVE mode switching)
    response = get_regime(
        asset=regime_request.asset,
        price_history=regime_request.price_history,
        volume_history=regime_request.volume_history
    )
    
    # Log request
    latency_ms = (time.time() - start_time) * 1000
    log_request(logger, request, "/regime", latency_ms, api_key_info.get("name"))
    
    return response

