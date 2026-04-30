"""
API Key Authentication
"""
from fastapi import Header, HTTPException, status
from typing import Optional
from .config import API_KEYS


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> dict:
    """
    Verify API key from X-API-Key header
    
    Returns:
        dict: API key metadata (tier, name, rate_limit)
    
    Raises:
        HTTPException: 401 if key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header."
        )
    
    if x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key."
        )
    
    return API_KEYS[x_api_key]

