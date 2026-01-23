"""
Structured JSON Logging
"""
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Optional
from fastapi import Request


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
        if hasattr(record, "api_key_id"):
            log_data["api_key_id"] = record.api_key_id
        if hasattr(record, "user_ip"):
            log_data["user_ip"] = record.user_ip
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        return json.dumps(log_data)


def setup_logging():
    """Configure structured JSON logging"""
    logger = logging.getLogger("boonmindx_capital_shield")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger


def log_request(
    logger: logging.Logger,
    request: Request,
    endpoint: str,
    latency_ms: float,
    api_key_id: Optional[str] = None,
    request_id: Optional[str] = None
):
    """Log API request with structured data"""
    extra = {
        "endpoint": endpoint,
        "latency_ms": round(latency_ms, 2),
        "api_key_id": api_key_id or "anonymous",
        "user_ip": request.client.host if request.client else "unknown",
        "request_id": request_id or str(uuid.uuid4())
    }
    logger.info(f"API request: {endpoint}", extra=extra)

