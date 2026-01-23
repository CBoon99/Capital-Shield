# Rate Limit Profiles - BoonMindX Capital Shield

**Date**: November 14, 2025  
**Phase**: Phase 3, Day 1  
**Status**: Configuration Guide

---

## Overview

This document defines rate limiting profiles for different environments (local, staging, production). Rate limits protect the API from abuse and ensure fair resource allocation.

---

## Rate Limit Architecture

### Two-Layer Rate Limiting

1. **Application-Level** (FastAPI middleware)
   - IP-based rate limiting
   - Token bucket algorithm
   - Configurable per endpoint

2. **Infrastructure-Level** (Cloudflare / Nginx)
   - Additional DDoS protection
   - Geographic rate limiting (optional)
   - WAF rules

---

## Profile Definitions

### Local Profile (Development)

**Purpose**: Strict limits for local development and testing

**Configuration**:
```python
RATE_LIMIT_PER_SECOND = 10
RATE_LIMIT_BURST = 20
```

**Per-Endpoint Limits**:

| Endpoint | Limit (req/s) | Burst | Notes |
|----------|--------------:|------:|-------|
| `/api/v1/healthz` | Unlimited | - | Public endpoint |
| `/api/v1/dashboard/metrics` | Unlimited | - | Public endpoint |
| `/api/v1/signal` | 10 | 20 | Protected endpoint |
| `/api/v1/filter` | 10 | 20 | Protected endpoint |
| `/api/v1/risk` | 10 | 20 | Protected endpoint |
| `/api/v1/regime` | 10 | 20 | Protected endpoint |

**Rationale**: 
- Prevents accidental overload during development
- Encourages proper load testing practices
- Low enough to catch rate limit issues early

---

### Staging Profile (Load Testing & Demos)

**Purpose**: Relaxed limits to enable distributed load testing and investor demonstrations

**Configuration**:
```python
RATE_LIMIT_PER_SECOND = 200
RATE_LIMIT_BURST = 400
```

**Per-Endpoint Limits**:

| Endpoint | Limit (req/s) | Burst | Notes |
|----------|--------------:|------:|-------|
| `/api/v1/healthz` | Unlimited | - | Public endpoint |
| `/api/v1/dashboard/metrics` | Unlimited | - | Public endpoint |
| `/api/v1/signal` | 200 | 400 | Relaxed for load testing |
| `/api/v1/filter` | 200 | 400 | Relaxed for load testing |
| `/api/v1/risk` | 200 | 400 | Relaxed for load testing |
| `/api/v1/regime` | 200 | 400 | Relaxed for load testing |

**Rationale**:
- Enables distributed load testing from multiple IPs
- Allows investor demos without rate limit interruptions
- Still provides protection against abuse
- High enough to validate performance under load

**Load Testing Scenarios**:
- 10 concurrent workers × 4 endpoints = 40 req/s per IP
- 25 concurrent workers × 4 endpoints = 100 req/s per IP
- 50 concurrent workers × 4 endpoints = 200 req/s per IP
- 100 concurrent workers × 4 endpoints = 400 req/s per IP (burst)

---

### Production Profile (Live Customer Traffic)

**Purpose**: Balanced limits for production use, preventing abuse while allowing legitimate high-volume usage

**Configuration**:
```python
RATE_LIMIT_PER_SECOND = 50
RATE_LIMIT_BURST = 100
```

**Per-Endpoint Limits**:

| Endpoint | Limit (req/s) | Burst | Notes |
|----------|--------------:|------:|-------|
| `/api/v1/healthz` | Unlimited | - | Public endpoint |
| `/api/v1/dashboard/metrics` | Unlimited | - | Public endpoint |
| `/api/v1/signal` | 50 | 100 | Production limit |
| `/api/v1/filter` | 50 | 100 | Production limit |
| `/api/v1/risk` | 50 | 100 | Production limit |
| `/api/v1/regime` | 50 | 100 | Production limit |

**Rationale**:
- Prevents abuse and DDoS attacks
- Allows legitimate high-frequency trading use cases
- Burst allows for traffic spikes
- Can be adjusted per API key tier (see below)

---

## API Key Tier-Based Limits (Future)

### Free Tier

| Endpoint | Limit (req/s) | Daily Limit |
|----------|--------------:|------------:|
| `/api/v1/signal` | 5 | 10,000 |
| `/api/v1/filter` | 5 | 10,000 |

### Pro Tier

| Endpoint | Limit (req/s) | Daily Limit |
|----------|--------------:|------------:|
| `/api/v1/signal` | 25 | 100,000 |
| `/api/v1/filter` | 25 | 100,000 |

### Professional Tier

| Endpoint | Limit (req/s) | Daily Limit |
|----------|--------------:|------------:|
| `/api/v1/signal` | 50 | 1,000,000 |
| `/api/v1/filter` | 50 | 1,000,000 |

### Enterprise Tier

| Endpoint | Limit (req/s) | Daily Limit |
|----------|--------------:|------------:|
| `/api/v1/signal` | Custom | Unlimited |
| `/api/v1/filter` | Custom | Unlimited |

---

## Implementation

### Environment Variable Configuration

Set in `.env` file:

```bash
# Rate Limiting Configuration
RATE_LIMIT_PER_SECOND=200
RATE_LIMIT_BURST=400

# Per-endpoint rate limits (requests per second)
RATE_LIMIT_HEALTHZ=-1
RATE_LIMIT_DASHBOARD=-1
RATE_LIMIT_SIGNAL=200
RATE_LIMIT_FILTER=200
```

### Code Configuration

In `app/core/config.py`:

```python
# Rate Limiting (Phase 1: In-memory)
RATE_LIMIT_PER_SECOND = int(os.getenv("RATE_LIMIT_PER_SECOND", "10"))
RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "20"))

# Per-endpoint limits
RATE_LIMIT_ENDPOINTS = {
    "/api/v1/healthz": int(os.getenv("RATE_LIMIT_HEALTHZ", "-1")),
    "/api/v1/dashboard/metrics": int(os.getenv("RATE_LIMIT_DASHBOARD", "-1")),
    "/api/v1/signal": int(os.getenv("RATE_LIMIT_SIGNAL", str(RATE_LIMIT_PER_SECOND))),
    "/api/v1/filter": int(os.getenv("RATE_LIMIT_FILTER", str(RATE_LIMIT_PER_SECOND))),
}
```

---

## Rate Limit Behavior

### Token Bucket Algorithm

- **Bucket Size**: `RATE_LIMIT_BURST` tokens
- **Refill Rate**: `RATE_LIMIT_PER_SECOND` tokens per second
- **Request Cost**: 1 token per request

### Response Codes

- **200 OK**: Request allowed (token consumed)
- **429 Too Many Requests**: Rate limit exceeded (no token available)
- **503 Service Unavailable**: System overload (fallback)

### Rate Limit Headers

Responses include rate limit headers:

```
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 150
X-RateLimit-Reset: 1637000000
```

---

## Testing Rate Limits

### Local Testing

```bash
# Test rate limit (should get 429 after limit)
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/v1/signal \
    -H "X-API-Key: test_free_key_12345" \
    -H "Content-Type: application/json" \
    -d '{"asset":"BTC","price_history":[100,101,102,103,104]}'
  sleep 0.1
done
```

### Load Testing

```bash
# Use load test framework with API key
python3 -m load_tests.api_load_benchmark \
  --base-url https://staging.boonmindx.com \
  --concurrency 50 \
  --duration-seconds 30 \
  --endpoints signal filter \
  --api-key staging_enterprise_key_fghij \
  --output-dir reports/perf/staging
```

---

## Monitoring & Alerts

### Metrics to Monitor

- Rate limit hit rate (429 responses)
- Requests per second per endpoint
- Top IPs by request volume
- API key usage patterns

### Alerting Thresholds

- **Warning**: Rate limit hit rate > 5%
- **Critical**: Rate limit hit rate > 20%
- **Info**: New IP hitting limits consistently

---

## Best Practices

1. **Start Conservative**: Begin with lower limits, increase based on usage
2. **Monitor Closely**: Track rate limit hits and adjust accordingly
3. **Document Limits**: Clearly communicate limits to API users
4. **Provide Headers**: Include rate limit headers in responses
5. **Graceful Degradation**: Return 429 with retry-after header
6. **Whitelist IPs**: Allow whitelisting for enterprise customers

---

## Migration Between Profiles

### Local → Staging

1. Update `.env` file with staging profile values
2. Restart application
3. Verify rate limits are relaxed
4. Run load tests to validate

### Staging → Production

1. Review staging usage patterns
2. Set production limits based on actual usage
3. Update `.env` file
4. Deploy to production
5. Monitor closely for first 24 hours

---

## References

- `ENVIRONMENT_VARIABLES_TEMPLATE.env` - Environment variable template
- `app/core/rate_limit.py` - Rate limiting implementation
- `app/core/config.py` - Configuration management

---

*Last updated: November 14, 2025*

