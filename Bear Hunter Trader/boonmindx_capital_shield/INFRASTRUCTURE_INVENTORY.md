# Infrastructure Inventory — BoonMindX Capital Shield
**Date**: 2025-11-16  
**Purpose**: Honest technical inventory for framework monetization

---

## Executive Summary

BoonMindX Capital Shield is a **risk management API framework** that sits between trading signal generators and execution. It provides deterministic safety rails, simulation/validation tooling, and monitoring infrastructure. This is **infrastructure code**, not a trading strategy.

**Core Value**: Prevents bad trades from reaching execution, with empirical validation tooling.

---

## 1. API Service (FastAPI)

### Purpose
REST API that provides risk filtering, signal evaluation, and metrics calculation for trading systems.

### Key Files
- `app/main.py` — FastAPI application entry point
- `app/routes/` — 7 route modules:
  - `signal.py` — Trading signal endpoint
  - `risk.py` — Risk assessment endpoint
  - `filter.py` — **Core trade filtering endpoint** (safety rails + engine)
  - `regime.py` — Market regime detection
  - `healthz.py` — Health check (public, no auth)
  - `metrics.py` — Performance metrics calculation
  - `dashboard_metrics.py` — Dashboard data endpoint
- `app/core/auth.py` — API key authentication (in-memory, tiered)
- `app/core/rate_limit.py` — IP-based rate limiting (10 req/s default)
- `app/core/config.py` — Configuration (env-driven)
- `app/models/` — Pydantic schemas for request/response validation

### External Dependencies
- `fastapi==0.104.1` — Web framework
- `uvicorn[standard]==0.24.0` — ASGI server
- `pydantic==2.5.0` — Data validation
- `httpx==0.25.0` — HTTP client (for tests)

### Inputs/Outputs
**API Endpoints** (all under `/api/v1/`):
- `POST /signal` — Get trading signal (BUY/SELL/HOLD) for asset
- `POST /risk` — Assess risk level for trade
- `POST /filter` — **Core endpoint**: Binary allow/block decision
- `POST /regime` — Detect market regime (BULL/BEAR/SIDEWAYS)
- `GET /healthz` — Health check (public, no auth)
- `POST /metrics` — Calculate performance metrics (Sharpe, drawdown, win rate)
- `GET /dashboard/metrics` — Dashboard data (public, no auth)

**Authentication**: API key via `X-API-Key` header (4 tiers: free/pro/professional/enterprise)

**Rate Limiting**: 10 requests/second per IP (configurable)

### Maturity
**PRODUCTION** — Fully functional API with auth, rate limiting, structured logging, CORS support.

### Notes for Buyers
- **No database**: API keys are in-memory (config file). Easy to add DB layer.
- **Mock/LIVE mode**: Can run in MOCK mode (deterministic) or LIVE mode (connects to trading engine).
- **OpenAPI docs**: Auto-generated at `/docs` endpoint.
- **Structured logging**: JSON logs for production monitoring.

---

## 2. Risk & Safety Rails

### Purpose
Deterministic hard limits that prevent trades from executing if they violate risk thresholds.

### Key Files
- `app/core/safety_rails.py` — Core safety rail logic
- `app/core/engine_adapter.py` — Adapter for trading engine integration
- `live_sim/presets.py` — Three risk presets (CONSERVATIVE/BALANCED/AGGRESSIVE)

### External Dependencies
None (pure Python logic)

### Inputs/Outputs
**Function**: `check_safety_rails(asset, action, regime) -> (allowed: bool, reason: str)`

**Checks Performed**:
1. **Max Drawdown Check** — Blocks if current drawdown exceeds threshold (e.g., -10%)
2. **Health Check** — Blocks if system health is unhealthy
3. **Regime Guard** — Blocks BUY orders in BEAR regime (if STRICT mode)

**Presets**:
- **CONSERVATIVE**: -5% drawdown threshold, strict regime guard
- **BALANCED**: -10% drawdown threshold, strict regime guard (default)
- **AGGRESSIVE**: -15% drawdown threshold, permissive regime guard

### Maturity
**PRODUCTION** — Core logic is deterministic and tested. Integration with live metrics requires metrics endpoint to be called.

### Notes for Buyers
- **Veto power**: Even if trading engine says "GO", safety rails can block the trade.
- **Configurable thresholds**: All thresholds are env-driven.
- **Structured rejection reasons**: Machine-readable codes (e.g., `DD_BREACH`, `VOL_BREACH`).
- **No strategy logic**: This is pure risk management, not trading strategy.

---

## 3. Simulation Engine

### Purpose
Run historical simulations to validate safety rails and compare baseline vs. shielded performance.

### Key Files
- `live_sim/runner.py` — Main simulation orchestrator
- `live_sim/data_loader.py` — Historical data loading (CSV/JSON)
- `live_sim/shield_client.py` — API client for calling Capital Shield endpoints
- `live_sim/bearhunter_bridge.py` — Bridge to trading engine (if present)
- `live_sim/historical_validation.py` — Multi-dataset validation
- `live_sim/multi_validation.py` — Run validation across multiple datasets
- `live_sim/crash_tests.py` — Stress test scenarios (drawdown, health, regime)
- `live_sim/opportunity_cost_analysis.py` — Measure cost of safety (blocked trades)
- `live_sim/slippage_model.py` — Execution cost modeling
- `live_sim/fp_test_harness.py` — False positive test harness
- `live_sim/reporting.py` — Report generation (JSON/Markdown)
- `live_sim/rsa.py` — RSA (Relative Survival Alpha) calculation
- `live_sim/quick_demo.py` — One-command demo runner

### External Dependencies
- `pandas` — Data manipulation (not in requirements.txt, but used)
- `numpy` — Numerical operations (not in requirements.txt, but used)

### Inputs/Outputs
**CLI Commands**:
- `python3 -m live_sim.runner` — Run single simulation
- `python3 -m live_sim.multi_validation` — Run multi-dataset validation
- `python3 -m live_sim.crash_tests` — Run crash test scenarios
- `python3 -m live_sim.quick_demo` — Run quick demo

**Input**: Historical OHLCV data (CSV or JSON format)

**Output**: 
- Equity curves (CSV)
- Trade logs (CSV)
- Summary reports (JSON, Markdown)
- Comparison reports (baseline vs. shielded)

### Maturity
**BETA** — Functional but some components may need data format validation. RSA calculation is locked (v1 formula).

### Notes for Buyers
- **No live trading**: This is simulation-only. No execution integration.
- **Deterministic**: Same inputs produce same outputs (when engine is in MOCK mode).
- **Validation tooling**: Can test safety rails against historical crashes (2008, 2020, etc.).
- **Baseline comparison**: Can compare performance with/without safety rails.

---

## 4. Data Adapters

### Purpose
Fetch and normalize market data from external sources.

### Key Files
- `data/coin_gecko_client.py` — CoinGecko API client for cryptocurrency data

### External Dependencies
- `requests` — HTTP client (not in requirements.txt, but used)
- CoinGecko API (free tier, 10-50 calls/minute)

### Inputs/Outputs
**Function**: `fetch_ohlcv(symbol, days, interval) -> DataFrame`

**Data Format**: Normalized OHLCV (Open, High, Low, Close, Volume) with datetime index

**Rate Limiting**: Built-in (1.2s between requests = ~50/min)

### Maturity
**BETA** — Functional but only supports CoinGecko. No other data sources yet.

### Notes for Buyers
- **Single source**: Only CoinGecko implemented. Easy to add other sources (Alpha Vantage, Yahoo Finance, etc.).
- **Shadow-live mode**: Can poll live data and run through safety rails without executing trades.
- **Normalized format**: Output is standardized, making it easy to swap data sources.

---

## 5. Monitoring & Metrics

### Purpose
Health checks, performance metrics, and structured logging for production monitoring.

### Key Files
- `app/routes/healthz.py` — Health check endpoint
- `app/routes/metrics.py` — Performance metrics calculation
- `app/routes/dashboard_metrics.py` — Dashboard data endpoint
- `app/core/logging.py` — Structured JSON logging

### External Dependencies
None (pure FastAPI)

### Inputs/Outputs
**Endpoints**:
- `GET /api/v1/healthz` — Returns status, uptime, version (public, no auth)
- `POST /api/v1/metrics` — Calculates Sharpe, drawdown, win rate from trade history (auth required)
- `GET /api/v1/dashboard/metrics` — Dashboard data (public, no auth)

**Logging**: Structured JSON logs to stdout (can be piped to log aggregation services)

### Maturity
**PRODUCTION** — Functional health checks and metrics. Logging is structured and production-ready.

### Notes for Buyers
- **No external monitoring**: No Prometheus/Grafana integration yet. Logs are JSON, easy to integrate.
- **Metrics calculation**: Basic metrics (Sharpe, drawdown, win rate). Can be extended.
- **Health checks**: Simple uptime/status. Can be extended with dependency checks.

---

## 6. Dashboard

### Purpose
Web-based real-time monitoring dashboard for API status and metrics.

### Key Files
- `dashboard/index.html` — Dashboard HTML
- `dashboard/app.js` — JavaScript for polling and chart updates
- `dashboard/styles.css` — Styling

### External Dependencies
- Chart.js (CDN) — Chart rendering
- FastAPI static file serving

### Inputs/Outputs
**Access**: `http://localhost:8000/dashboard/` (when API is running)

**Data Source**: Polls `/api/v1/healthz` and `/api/v1/dashboard/metrics` every 10 seconds

**Displays**:
- System status (up/down)
- Uptime
- Equity curve chart
- Drawdown chart
- Current metrics (Sharpe, drawdown, win rate)

### Maturity
**BETA** — Functional but basic. Charts work, polling works, but UI is minimal.

### Notes for Buyers
- **No authentication**: Dashboard is public (can be secured with reverse proxy).
- **Real-time updates**: Polls every 10 seconds. Can be adjusted.
- **Chart.js**: Uses CDN, can be self-hosted.
- **Mobile-friendly**: Basic responsive design.

---

## 7. Deployment/Infrastructure Templates

### Purpose
Documentation and templates for deploying the API to production.

### Key Files
- `infra/ENV_AND_GITIGNORE_POLICY.md` — Environment variable policy
- `infra/SECURITY_SECRETS_POLICY.md` — Security and secrets management
- `infra/RATE_LIMIT_PROFILES.md` — Rate limiting configuration
- `infra/LOGGING_PIPELINE.md` — Logging setup
- `infra/DOMAIN_SETUP_INSTRUCTIONS.md` — Domain configuration
- `infra/ENVIRONMENT_VARIABLES_TEMPLATE.env` — Environment variable template
- `infra/providers/CHOSEN_PROVIDER/README.md` — Provider-specific deployment notes

### External Dependencies
None (documentation only)

### Inputs/Outputs
**Templates Provided**:
- Environment variable configuration
- Security policies
- Rate limiting profiles
- Logging setup instructions

**Missing** (not provided):
- Systemd service files
- Nginx configuration
- SSL/TLS setup
- Docker/Docker Compose files
- Kubernetes manifests

### Maturity
**UNVERIFIED** — Documentation exists but actual deployment runbooks were deleted during cleanup. Templates are placeholders.

### Notes for Buyers
- **Documentation only**: No actual deployment automation. Manual setup required.
- **Provider-agnostic**: Can deploy to any VPS/cloud provider.
- **Missing automation**: No Terraform, Ansible, or deployment scripts.

---

## 8. Testing

### Purpose
Comprehensive test suite to validate API functionality, safety rails, and simulation engine.

### Key Files
- `tests/test_safety_rails.py` — Safety rail tests
- `tests/test_signal.py` — Signal endpoint tests
- `tests/test_risk.py` — Risk endpoint tests
- `tests/test_filter.py` — Filter endpoint tests
- `tests/test_regime.py` — Regime detection tests
- `tests/test_healthz.py` — Health check tests
- `tests/test_rate_limit.py` — Rate limiting tests
- `tests/test_engine_adapter.py` — Engine adapter tests
- `tests/test_live_sim_basic.py` — Basic simulation tests
- `tests/test_live_sim_crash_tests.py` — Crash test validation
- `tests/test_multi_validation.py` — Multi-dataset validation tests
- `tests/test_presets.py` — Preset configuration tests
- `tests/test_quick_demo.py` — Quick demo tests
- `tests/test_mode_switching.py` — MOCK/LIVE mode switching tests
- `tests/test_investor_summary.py` — Report generation tests

### External Dependencies
- `pytest==7.4.3` — Test framework
- `pytest-asyncio==0.21.1` — Async test support
- `httpx==0.25.0` — HTTP client for API tests

### Inputs/Outputs
**Test Command**: `pytest tests/` (or `python -m pytest tests/`)

**Test Count**: ~81 test functions across 15 test files

**Coverage**:
- API endpoints (all routes)
- Safety rails (all checks)
- Rate limiting
- Authentication
- Simulation engine (basic flows)
- Crash tests
- Preset configurations
- Mode switching (MOCK/LIVE)

### Maturity
**PRODUCTION** — Comprehensive test suite. All tests pass. Good coverage of core functionality.

### Notes for Buyers
- **Fast execution**: Tests run in seconds (no external dependencies in most tests).
- **No integration tests**: Tests are unit/integration level. No end-to-end tests with real data.
- **Mock mode**: Most tests use MOCK mode (deterministic). LIVE mode tests are limited.

---

## 9. Operational Scripts

### Purpose
Shell scripts and Python utilities for local development and validation.

### Key Files
- `scripts/local_api_smoke_test.sh` — Start API and test healthz endpoint
- `scripts/run_quant_sanity_suite.sh` — Run quantitative validation scripts
- `scripts/local_mini_loadtest.sh` — Small load test against API
- `scripts/run_shadow_live_coingecko.py` — Shadow-live mode with CoinGecko
- `scripts/run_monte_carlo_round2.sh` — Monte Carlo stress test
- `scripts/test_v1_readiness.sh` — V1 readiness check
- `scripts/prelaunch_validation_suite.sh` — Full pre-launch validation
- `scripts/README.md` — Script documentation

### External Dependencies
- Bash shell
- Python 3
- curl (for smoke tests)

### Inputs/Outputs
**Scripts**:
- Start/stop API server
- Run validation suites
- Execute load tests
- Run shadow-live simulations

**Output**: Logs, reports, test results

### Maturity
**BETA** — Scripts work but may need path adjustments. Some scripts reference deleted files.

### Notes for Buyers
- **Local development**: Scripts are for local/dev use. Not production automation.
- **Sandbox limitations**: Some scripts may not work in restricted environments (port binding, etc.).
- **Documentation**: README explains each script's purpose.

---

## 10. Quantitative Validation Tools

### Purpose
Python modules for running quantitative validation (False Positives, Opportunity Cost, Execution Cost).

### Key Files
- `quant/run_monte_carlo_validation.py` — Monte Carlo validation driver
- `quant/run_monte_carlo_round2.py` — Custom Monte Carlo Round 2 (30m candles, 5% leverage)

### External Dependencies
- `live_sim/` modules
- Historical data files

### Inputs/Outputs
**Input**: Historical datasets (CSV/JSON)

**Output**: 
- Per-asset JSON results
- Aggregate summaries
- Markdown reports

### Maturity
**BETA** — Functional but dataset-dependent. Some datasets may be missing.

### Notes for Buyers
- **Validation tooling**: Used to validate safety rails against historical scenarios.
- **RSA calculation**: Uses locked v1 RSA formula (in `live_sim/rsa.py`).
- **Dataset requirements**: Needs properly formatted historical data.

---

## Most Valuable Differentiators

1. **Deterministic Safety Rails** — Hard limits that prevent bad trades, with structured rejection reasons
2. **Simulation/Validation Engine** — Can test safety rails against historical crashes before deploying
3. **API-First Design** — REST API that can be integrated into any trading stack
4. **Baseline Comparison** — Can compare performance with/without safety rails to measure cost of safety
5. **Preset Configurations** — Three risk profiles (CONSERVATIVE/BALANCED/AGGRESSIVE) out of the box

---

## What's Missing / Roadmap

### Missing (Not Implemented)
- **Database layer**: API keys are in-memory. No persistence.
- **Real broker integration**: No execution adapter. Simulation-only.
- **Advanced monitoring**: No Prometheus/Grafana integration.
- **Deployment automation**: No Docker, Kubernetes, or Terraform.
- **Multi-asset support**: Limited to single-asset evaluation.
- **Backtesting engine**: No built-in backtesting (only simulation).

### Roadmap (Honest Assessment)
- **Database integration**: Add PostgreSQL/MongoDB for API key persistence
- **Broker adapters**: Add execution adapters for major brokers (Binance, Interactive Brokers, etc.)
- **Advanced metrics**: Add more performance metrics (Sortino, Calmar, etc.)
- **Multi-asset portfolio**: Support portfolio-level risk management
- **Real-time data feeds**: Add WebSocket support for live data
- **Deployment automation**: Add Docker Compose, Kubernetes manifests

---

## Summary

**What You're Buying**:
- A functional risk management API framework
- Simulation/validation tooling
- Comprehensive test suite
- Basic monitoring dashboard
- Documentation (some gaps)

**What You're NOT Buying**:
- A profitable trading strategy
- Live trading execution
- Guaranteed returns
- Production deployment automation
- Advanced monitoring/alerting

**Best Use Case**: Quant funds, signal sellers, or developers who want to add risk management to their trading systems without building it from scratch.

---

**Inventory Date**: 2025-11-16  
**Status**: Production-ready API, Beta simulation tools, Unverified deployment docs
