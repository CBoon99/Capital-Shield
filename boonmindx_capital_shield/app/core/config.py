"""
Configuration for BoonMindX Capital Shield API
"""
import os
from typing import Dict, List

# API Configuration
API_TITLE = "BoonMindX Capital Shield API"
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Tier Definitions
TIER_LIMITS: Dict[str, Dict] = {
    "simulation_only": {
        "daily_calls": 1000,
        "live_access": False,
        "monthly_price_gbp": 19,
        "annual_price_gbp": 149,  # one-time perpetual
        "overage_rate_gbp": 0.0  # No overages for simulation-only
    },
    "starter": {
        "daily_calls": 10000,
        "live_access": True,
        "monthly_price_gbp": 49,
        "annual_price_gbp": 490,
        "overage_rate_gbp": 0.0001  # £0.0001 per additional call
    },
    "professional": {
        "daily_calls": 100000,
        "live_access": True,
        "monthly_price_gbp": 199,
        "annual_price_gbp": 1990,
        "overage_rate_gbp": 0.0001  # £0.0001 per additional call
    },
    "enterprise": {
        "daily_calls": float('inf'),  # unlimited
        "live_access": True,
        "monthly_price_gbp": None,  # Custom pricing
        "annual_price_gbp": None,  # Custom pricing
        "overage_rate_gbp": 0.0  # No overages for enterprise
    }
}

# API Keys (Phase 1: In-memory, Phase 2: Database)
# Format: api_key -> {"tier": "simulation_only|starter|professional|enterprise", "name": "key_name", "stripe_customer_id": "cus_xxx"}
API_KEYS: Dict[str, Dict[str, str]] = {
    "test_simulation_key_12345": {
        "tier": "simulation_only",
        "name": "Test Simulation Key",
        "rate_limit": 1000  # requests per day
    },
    "test_starter_key_67890": {
        "tier": "starter",
        "name": "Test Starter Key",
        "rate_limit": 10000  # requests per day
    },
    "test_professional_key_abcde": {
        "tier": "professional",
        "name": "Test Professional Key",
        "rate_limit": 100000  # requests per day
    },
    "test_enterprise_key_fghij": {
        "tier": "enterprise",
        "name": "Test Enterprise Key",
        "rate_limit": -1  # unlimited
    }
}

# Rate Limiting (Phase 1: In-memory)
RATE_LIMIT_PER_SECOND = 10  # Max requests per second per IP
RATE_LIMIT_BURST = 20  # Burst allowance

# Server Configuration
HOST = os.getenv("SHIELD_API_HOST", "0.0.0.0")
PORT = int(os.getenv("SHIELD_API_PORT", "8000"))
DEBUG = os.getenv("SHIELD_API_DEBUG", "false").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "json"  # Structured JSON logging

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://bearhuntercapital.com"
]

# Engine Mode: "MOCK" or "LIVE"
ENGINE_MODE = os.getenv("ENGINE_MODE", "MOCK").upper()  # Default to MOCK for safety

# BearHunter Engine Paths
BEARHUNTER_ENGINE_PATH = os.getenv("BEARHUNTER_ENGINE_PATH", "testing_area")

# Capital Shield Mode: "STRICT" or "PERMISSIVE"
CAPITAL_SHIELD_MODE = os.getenv("CAPITAL_SHIELD_MODE", os.getenv("SHIELD_MODE", "PERMISSIVE")).upper()

# Safety Rails Configuration
MAX_DRAWDOWN_THRESHOLD = float(os.getenv("MAX_DRAWDOWN_THRESHOLD", "-0.10"))  # -10%
BLOCK_BEAR_BUYS = os.getenv("BLOCK_BEAR_BUYS", "false").lower() == "true"
HEALTH_CHECK_ENABLED = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"

# Engine Health
ENGINE_HEALTH_CHECK_INTERVAL = int(os.getenv("ENGINE_HEALTH_CHECK_INTERVAL", "60"))  # seconds
ENGINE_TIMEOUT = int(os.getenv("ENGINE_TIMEOUT", "5"))  # seconds

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# Database Configuration (for usage tracking)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./capital_shield.db")  # SQLite for beta, PostgreSQL for production
