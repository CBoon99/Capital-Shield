"""
Rate Limiting (Phase 1: In-memory token bucket)
"""
import time
from collections import defaultdict
from typing import Tuple
from fastapi import HTTPException, status, Request
from .config import RATE_LIMIT_PER_SECOND, RATE_LIMIT_BURST

# In-memory token buckets: {ip: (tokens, last_update)}
_token_buckets: defaultdict = defaultdict(lambda: (RATE_LIMIT_BURST, time.time()))


def check_rate_limit(request: Request) -> None:
    """
    Check rate limit for request IP using token bucket algorithm
    
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    # Get or initialize bucket for this IP
    tokens, last_update = _token_buckets[client_ip]
    
    # Refill tokens based on time elapsed
    time_elapsed = current_time - last_update
    tokens_to_add = time_elapsed * RATE_LIMIT_PER_SECOND
    tokens = min(RATE_LIMIT_BURST, tokens + tokens_to_add)
    
    # Check if request can be processed
    if tokens < 1:
        _token_buckets[client_ip] = (tokens, current_time)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_PER_SECOND} requests per second."
        )
    
    # Consume one token
    tokens -= 1
    _token_buckets[client_ip] = (tokens, current_time)

