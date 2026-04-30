"""
Tier Access Control Module

Enforces tier-based API access limits and tracks usage for billing.
"""
from fastapi import HTTPException, status
from typing import Dict, Optional
from app.core.config import TIER_LIMITS
from app.db.usage import track_api_call, get_daily_usage


class TierAccessControl:
    """Manages tier-based access control and usage tracking"""
    
    LIMITS = TIER_LIMITS
    
    @classmethod
    def check_access(cls, api_key: str, api_key_info: Dict, endpoint: str, 
                    allow_overage: bool = True) -> Dict:
        """
        Check if API call is allowed based on tier limits
        
        Args:
            api_key: The API key making the request
            api_key_info: API key metadata from auth module
            endpoint: The endpoint being accessed
            allow_overage: If True, allow calls beyond limit (for overage billing)
        
        Returns:
            Dictionary with access decision and usage info
        
        Raises:
            HTTPException: 429 if limit exceeded and overage not allowed
        """
        tier = api_key_info.get('tier', 'starter')
        tier_config = cls.LIMITS.get(tier, cls.LIMITS['starter'])
        
        # Check if endpoint requires live access
        if not tier_config.get('live_access', True):
            # Simulation-only tier can only access simulation endpoints
            if not endpoint.startswith('/api/v1/simulation'):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Tier '{tier}' does not have live API access. Simulation endpoints only."
                )
        
        # Get daily limit
        daily_limit = tier_config.get('daily_calls', 10000)
        
        # Track the API call
        track_api_call(api_key, endpoint)
        
        # Check current daily usage
        current_usage = get_daily_usage(api_key)
        
        # Enterprise tier has unlimited calls
        if daily_limit == float('inf'):
            return {
                'allowed': True,
                'daily_usage': current_usage,
                'daily_limit': None,
                'remaining': None,
                'overage': False
            }
        
        # Check if limit exceeded
        if current_usage > daily_limit:
            if allow_overage:
                # Allow but mark as overage
                overage_calls = current_usage - daily_limit
                return {
                    'allowed': True,
                    'daily_usage': current_usage,
                    'daily_limit': daily_limit,
                    'remaining': 0,
                    'overage': True,
                    'overage_calls': overage_calls
                }
            else:
                # Block the request
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Daily API call limit exceeded",
                        "tier": tier,
                        "daily_limit": daily_limit,
                        "current_usage": current_usage,
                        "upgrade_url": "/#pricing"
                    }
                )
        
        # Within limit
        remaining = daily_limit - current_usage
        return {
            'allowed': True,
            'daily_usage': current_usage,
            'daily_limit': daily_limit,
            'remaining': remaining,
            'overage': False
        }
    
    @classmethod
    def get_tier_info(cls, tier: str) -> Dict:
        """Get tier configuration information"""
        return cls.LIMITS.get(tier, cls.LIMITS['starter'])
    
    @classmethod
    def check_endpoint_access(cls, tier: str, endpoint: str) -> bool:
        """
        Check if a tier has access to a specific endpoint
        
        Args:
            tier: The tier name
            endpoint: The endpoint path
        
        Returns:
            True if access is allowed, False otherwise
        """
        tier_config = cls.LIMITS.get(tier, cls.LIMITS['starter'])
        
        # Simulation-only tier can only access simulation endpoints
        if not tier_config.get('live_access', True):
            return endpoint.startswith('/api/v1/simulation')
        
        return True
