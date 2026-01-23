"""
Signal Endpoint
"""
import time
from fastapi import APIRouter, Request, Depends
from app.core.auth import verify_api_key
from app.core.rate_limit import check_rate_limit
from app.core.logging import log_request, setup_logging
from app.core.engine_adapter import get_signal
from app.models.signal import SignalResponse
from app.utils.validators import SignalRequest

router = APIRouter()
logger = setup_logging()


@router.post("/signal", response_model=SignalResponse)
async def get_signal_endpoint(
    request: Request,
    signal_request: SignalRequest,
    api_key_info: dict = Depends(verify_api_key)
):
    """
    Get trading signal for an asset
    
    Returns signal from BearHunter engine (LIVE mode) or deterministic mock (MOCK mode)
    """
    start_time = time.time()
    
    # Check rate limit
    check_rate_limit(request)
    
    # Get signal from engine adapter (handles MOCK/LIVE mode switching)
    response = get_signal(
        asset=signal_request.asset,
        price_history=signal_request.price_history,
        volume_history=signal_request.volume_history
    )
    
    # Log request
    latency_ms = (time.time() - start_time) * 1000
    log_request(logger, request, "/signal", latency_ms, api_key_info.get("name"))
    
    return response

