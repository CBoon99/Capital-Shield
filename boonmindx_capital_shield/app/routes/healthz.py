"""
Health Check Endpoint
"""
import time
from fastapi import APIRouter, Request
from app.core.logging import log_request, setup_logging
from app.core.version import API_VERSION
from app.utils.time import get_current_timestamp

router = APIRouter()
logger = setup_logging()

# Track startup time for uptime calculation
_start_time = time.time()


@router.get("/healthz")
async def health_check(request: Request):
    """
    Health check endpoint (no auth required)
    
    Returns API status and uptime
    """
    start_time = time.time()
    
    uptime_seconds = int(time.time() - _start_time)
    
    response = {
        "status": "ok",
        "uptime": uptime_seconds,
        "version": API_VERSION,
        "timestamp": get_current_timestamp()
    }
    
    # Log request
    latency_ms = (time.time() - start_time) * 1000
    log_request(logger, request, "/healthz", latency_ms)
    
    return response

