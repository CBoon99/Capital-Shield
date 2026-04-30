# Logging Pipeline - BoonMindX Capital Shield

**Date**: November 14, 2025  
**Phase**: Phase 3, Day 1  
**Status**: Configuration Guide

---

## Overview

This document describes the logging architecture for BoonMindX Capital Shield staging and production environments. Logging is critical for debugging, performance monitoring, security auditing, and compliance.

---

## Log Categories

### 1. Application Logs

**Purpose**: General application events, request/response logging

**Location**: `/var/log/boonmindx_capital_shield/app.log`

**Format**: JSON (structured logging)

**Levels**: INFO, WARNING, ERROR, CRITICAL

**Content**:
- API requests (endpoint, method, status code, latency)
- Application startup/shutdown
- Configuration loading
- General application events

**Rotation**: 100MB, keep 10 files

---

### 2. Performance Logs

**Purpose**: Performance metrics, latency tracking, throughput monitoring

**Location**: `/var/log/boonmindx_capital_shield/performance.log`

**Format**: JSON

**Content**:
- Request latency (p50, p95, p99)
- Throughput (requests/second)
- Endpoint-specific metrics
- Worker process metrics
- Memory/CPU usage

**Rotation**: 100MB, keep 10 files

**Sampling**: Can be sampled (e.g., 1 in 10 requests) for high-volume endpoints

---

### 3. Error Logs

**Purpose**: Errors, exceptions, failures

**Location**: `/var/log/boonmindx_capital_shield/error.log`

**Format**: JSON

**Levels**: ERROR, CRITICAL

**Content**:
- Exception stack traces
- Error messages
- Failed requests
- System errors
- Integration failures

**Rotation**: 50MB, keep 20 files (errors are important)

**Alerting**: Immediate alerts for CRITICAL errors

---

### 4. Audit Logs

**Purpose**: Security auditing, compliance, request tracking

**Location**: `/var/log/boonmindx_capital_shield/audit.log`

**Format**: JSON (immutable, append-only)

**Content**:
- All API requests (full request/response)
- API key usage
- Authentication events
- Authorization decisions
- Rate limit hits
- Configuration changes
- Admin actions

**Rotation**: 500MB, keep 30 files (long retention for compliance)

**Security**: Encrypted, append-only, tamper-evident

---

### 5. Access Logs

**Purpose**: HTTP access logging (Nginx/Cloudflare level)

**Location**: `/var/log/nginx/access.log` (if using Nginx)

**Format**: Combined log format

**Content**:
- IP addresses
- Request methods
- URLs
- Status codes
- Response sizes
- User agents

**Rotation**: Managed by Nginx logrotate

---

## Log Structure

### JSON Log Format

```json
{
  "timestamp": "2025-11-14T12:34:56.789Z",
  "level": "INFO",
  "module": "logging",
  "function": "log_request",
  "line": 69,
  "message": "API request",
  "endpoint": "/api/v1/signal",
  "method": "POST",
  "status_code": 200,
  "latency_ms": 5.23,
  "api_key_id": "staging_pro_key_67890",
  "user_ip": "203.0.113.45",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_agent": "python-requests/2.28.0"
}
```

### Audit Log Format

```json
{
  "timestamp": "2025-11-14T12:34:56.789Z",
  "event_type": "api_request",
  "endpoint": "/api/v1/filter",
  "method": "POST",
  "api_key_id": "staging_pro_key_67890",
  "api_key_tier": "pro",
  "user_ip": "203.0.113.45",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "request_body": {
    "asset": "BTC",
    "action": "BUY",
    "price_history": [100.0, 101.0, 102.0]
  },
  "response_status": 200,
  "response_body": {
    "trade_allowed": true,
    "confidence": 0.85
  },
  "latency_ms": 5.23,
  "rate_limit_status": "allowed"
}
```

---

## Log Rotation

### Configuration

Create `/etc/logrotate.d/boonmindx-capital-shield`:

```
/var/log/boonmindx_capital_shield/*.log {
    daily
    rotate 10
    compress
    delaycompress
    missingok
    notifempty
    create 0644 capital-shield capital-shield
    sharedscripts
    postrotate
        systemctl reload capital-shield > /dev/null 2>&1 || true
    endscript
}

# Special handling for audit logs (longer retention)
/var/log/boonmindx_capital_shield/audit.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 capital-shield capital-shield
    sharedscripts
    postrotate
        systemctl reload capital-shield > /dev/null 2>&1 || true
    endscript
}
```

### Manual Rotation

```bash
# Test logrotate configuration
sudo logrotate -d /etc/logrotate.d/boonmindx-capital-shield

# Force rotation
sudo logrotate -f /etc/logrotate.d/boonmindx-capital-shield
```

---

## Cloud Logging Integration

### AWS CloudWatch (If Using AWS)

**Setup**:

1. Install CloudWatch agent:
```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

2. Configure agent (`/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json`):
```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/boonmindx_capital_shield/app.log",
            "log_group_name": "boonmindx-capital-shield-staging/app",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          },
          {
            "file_path": "/var/log/boonmindx_capital_shield/error.log",
            "log_group_name": "boonmindx-capital-shield-staging/error",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          },
          {
            "file_path": "/var/log/boonmindx_capital_shield/audit.log",
            "log_group_name": "boonmindx-capital-shield-staging/audit",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
```

3. Start agent:
```bash
sudo systemctl start amazon-cloudwatch-agent
sudo systemctl enable amazon-cloudwatch-agent
```

### External Log Aggregation (Optional)

**Options**:
- **Datadog**: APM + logging
- **Splunk**: Enterprise log management
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Loki**: Grafana's log aggregation

---

## Log Analysis & Monitoring

### Key Metrics to Track

1. **Error Rate**: Errors per minute
2. **Latency**: p50, p95, p99 per endpoint
3. **Throughput**: Requests per second
4. **Rate Limit Hits**: 429 responses per minute
5. **API Key Usage**: Requests per API key tier

### Log Queries

**Find errors in last hour**:
```bash
grep '"level":"ERROR"' /var/log/boonmindx_capital_shield/error.log | \
  jq -r 'select(.timestamp > (now - 3600))'
```

**Top endpoints by latency**:
```bash
cat /var/log/boonmindx_capital_shield/performance.log | \
  jq -r 'select(.endpoint) | "\(.endpoint) \(.latency_ms)"' | \
  awk '{sum[$1]+=$2; count[$1]++} END {for (i in sum) print i, sum[i]/count[i]}' | \
  sort -k2 -rn
```

**API key usage**:
```bash
cat /var/log/boonmindx_capital_shield/audit.log | \
  jq -r 'select(.api_key_id) | .api_key_id' | \
  sort | uniq -c | sort -rn
```

---

## Security Considerations

### Log Encryption

**At Rest**:
- Encrypt log files on disk (LUKS, EBS encryption)
- Restrict file permissions (640 for audit logs)

**In Transit**:
- Use TLS for log shipping
- Encrypt CloudWatch agent communication

### Access Control

```bash
# Set log directory permissions
sudo chown -R capital-shield:capital-shield /var/log/boonmindx_capital_shield
sudo chmod 755 /var/log/boonmindx_capital_shield
sudo chmod 640 /var/log/boonmindx_capital_shield/*.log
sudo chmod 600 /var/log/boonmindx_capital_shield/audit.log
```

### PII Handling

- **Do NOT log**: Passwords, API keys (full values), sensitive user data
- **Do log**: API key IDs (hashed or truncated), request metadata, timestamps

---

## Alerting

### Error Alerts

**Critical Errors** (immediate):
- Application crashes
- Database connection failures
- SSL certificate expiration warnings

**Warning Alerts** (within 5 minutes):
- Error rate > 5%
- Latency p95 > 100ms
- Rate limit hit rate > 10%

### Monitoring Tools

- **UptimeRobot**: HTTP endpoint monitoring
- **CloudWatch Alarms**: AWS-native alerting
- **PagerDuty**: On-call alerting
- **Slack**: Team notifications

---

## Log Retention Policy

| Log Type | Retention | Reason |
|----------|-----------|--------|
| Application Logs | 10 days | Debugging, troubleshooting |
| Performance Logs | 30 days | Performance analysis, optimization |
| Error Logs | 90 days | Error tracking, pattern analysis |
| Audit Logs | 1 year | Compliance, security auditing |

---

## Implementation Checklist

- [ ] Create log directory: `/var/log/boonmindx_capital_shield`
- [ ] Set directory permissions
- [ ] Configure log rotation
- [ ] Update application logging configuration
- [ ] Test log writing
- [ ] Set up CloudWatch agent (if AWS)
- [ ] Configure log aggregation (if using)
- [ ] Set up alerting
- [ ] Document log access procedures
- [ ] Test log rotation
- [ ] Verify log retention

---

## References

- `ENVIRONMENT_VARIABLES_TEMPLATE.env` - Logging configuration
- `app/core/logging.py` - Logging implementation
- AWS CloudWatch Logs: https://docs.aws.amazon.com/cloudwatch/
- Logrotate: https://linux.die.net/man/8/logrotate

---

*Last updated: November 14, 2025*

