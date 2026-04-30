# Infrastructure Notes — v1 (Current Reality)

**Date**: 2025-11-16  
**Status**: Production v1 (Hardened VPS)

---

## Overview

Capital Shield v1 runs on a hardened VPS with FastAPI, Nginx reverse proxy, TLS termination, and systemd service management. This is the **current reality** for shadow-live and early pilot deployments.

AWS/ECS/Lambda/SOC2 architecture is **future-state** (post-raise).

---

## Hosting Stack

### Server
- **Provider**: Hardened VPS (generic, no specific vendor lock-in)
- **OS**: Linux (Ubuntu/Debian-based)
- **Access**: SSH key-based authentication only (no password login)
- **Firewall**: UFW configured (ports 22, 80, 443 only)

### Application Layer
- **Framework**: FastAPI (Python 3.9+)
- **ASGI Server**: Uvicorn
- **Process Manager**: systemd
- **Service Name**: `boonmindx-capital-shield.service`

### Reverse Proxy
- **Proxy**: Nginx
- **TLS**: Let's Encrypt (Certbot for auto-renewal)
- **Config**: `/etc/nginx/sites-available/capital-shield`
- **Features**:
  - HTTP → HTTPS redirect
  - Proxy headers (X-Real-IP, X-Forwarded-For)
  - Rate limiting at proxy level (optional, currently handled by app)

### Logging
- **Application Logs**: JSON-formatted, written to `/var/log/capital-shield/`
- **Rotation**: logrotate configured (daily, keep 30 days)
- **Nginx Logs**: `/var/log/nginx/capital-shield.access.log` and `.error.log`
- **Systemd Logs**: `journalctl -u boonmindx-capital-shield`

---

## Service Management

### Start/Stop/Restart
```bash
sudo systemctl start boonmindx-capital-shield
sudo systemctl stop boonmindx-capital-shield
sudo systemctl restart boonmindx-capital-shield
sudo systemctl status boonmindx-capital-shield
```

### View Logs
```bash
# Application logs
sudo journalctl -u boonmindx-capital-shield -f

# Nginx logs
sudo tail -f /var/log/nginx/capital-shield.access.log
```

### Reload Nginx (after config changes)
```bash
sudo nginx -t  # Test config
sudo systemctl reload nginx
```

---

## Security

### SSH Hardening
- Key-based authentication only
- Root login disabled
- Fail2ban configured (optional but recommended)

### TLS/SSL
- Let's Encrypt certificates
- Auto-renewal via Certbot cron job
- HTTPS enforced (HTTP redirects to HTTPS)

### API Security
- API key authentication (`X-API-Key` header)
- Rate limiting (10 req/s per IP for protected endpoints)
- Structured logging (no secrets in logs)

### Secrets Management
- Environment variables via systemd `EnvironmentFile`
- `.env` files never committed to Git
- API keys rotated regularly

---

## Deployment Process (v1)

1. **SSH into server**
   ```bash
   ssh -i ~/.ssh/capital_shield_key deploy@<SERVER_IP>
   ```

2. **Pull latest code**
   ```bash
   cd ~/boonmindx_capital_shield
   git pull origin main
   ```

3. **Update dependencies (if needed)**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Restart service**
   ```bash
   sudo systemctl restart boonmindx-capital-shield
   ```

5. **Verify health**
   ```bash
   curl https://<DOMAIN>/api/v1/healthz
   ```

---

## Monitoring (v1)

### Health Checks
- **Endpoint**: `/api/v1/healthz`
- **Expected**: `{"status": "ok", "uptime": <seconds>, ...}`
- **Frequency**: Every 60s (external monitoring service)

### Metrics
- **Uptime**: Tracked via systemd
- **Request counts**: Logged in Nginx access logs
- **Error rates**: Logged in application logs
- **Latency**: Logged per-request in application logs

### Alerts (Manual for v1)
- SSH into server and check logs if health check fails
- No automated alerting yet (future: PagerDuty/Slack integration)

---

## Future State (Post-Raise)

The following are **planned** but not yet implemented:

- **AWS ECS/Lambda**: Containerized deployment with auto-scaling
- **Redis**: Distributed rate limiting and caching
- **Prometheus/Grafana**: Real-time metrics and dashboards
- **CloudWatch**: Centralized logging
- **Multi-region**: Geographic redundancy
- **SOC2 Type II**: Compliance certification
- **24/7 On-call**: SRE rotation

---

## Quick Reference

| Component | Current (v1) | Future (Post-Raise) |
|-----------|--------------|---------------------|
| Hosting | Hardened VPS | AWS ECS/Lambda |
| Proxy | Nginx | AWS ALB + Nginx |
| TLS | Let's Encrypt | AWS Certificate Manager |
| Logging | Local files + rotation | CloudWatch |
| Monitoring | Manual + health checks | Prometheus/Grafana |
| Secrets | systemd EnvironmentFile | AWS Secrets Manager |
| Scaling | Vertical (upgrade VPS) | Horizontal (auto-scaling) |
| Compliance | None | SOC2 Type II |

---

## Contact

For infrastructure questions or deployment issues, contact the engineering team (currently: Carl Boon + AI collaborators).

**Last Updated**: 2025-11-16

