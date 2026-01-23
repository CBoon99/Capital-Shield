# BoonMindX Capital Shield

**Risk-first trading infrastructure and execution safety framework for algorithmic trading systems**

Capital Shield is a strategy-agnostic deterministic risk controls framework that sits between trading signal generators and market execution. This risk-first trading infrastructure enforces hard execution constraints (max drawdown limits, regime guards, health checks) with structured rejection reasons, providing a validation harness to measure the cost of safety before deployment. Designed for integration into existing quantitative trading infrastructure, not as a profitable trading bot or alpha engine.

---

## What Capital Shield Is: Risk-First Trading Infrastructure

**BoonMindX Capital Shield** is a deterministic safety gateway that sits between trading signal generators and market execution. It enforces hard risk limits (max drawdown, regime guards, health checks) with structured rejection reasons, providing a validation harness to measure the cost of safety before deployment. The system is strategy-agnostic, API-first, and designed for integration into existing quantitative trading infrastructure.

**Key Differentiator**: Unlike alpha-seeking bots, signal sellers, or black-box strategies, Capital Shield is pure infrastructure. It enforces deterministic execution constraints regardless of trading signals. You bring your own strategy; Capital Shield enforces the safety rails.

---

## What It Is NOT

- ❌ **Not a trading strategy** — Does not generate buy/sell signals
- ❌ **Not a profitable trading bot** — Infrastructure, not alpha generation
- ❌ **Not a backtesting platform** — Simulation/validation tooling, not a full backtesting suite
- ❌ **Not a guarantee of profits** — Reduces risk, does not guarantee returns
- ❌ **Not financial advice** — Infrastructure software only
- ❌ **Not a live trading system** — No broker integration, simulation-only

---

## Why It Exists

The post-alpha era demands **risk-first infrastructure**. Capital Shield provides deterministic safety gates that integrate into any trading stack, with validation tooling to measure the cost of safety before deployment. It is strategy-agnostic: bring your own signals, and Capital Shield enforces the safety rails.

**Core Value**: Prevents bad trades from reaching execution, with empirical validation to measure the cost of safety.

---

## Architecture

```
┌─────────────────┐
│ Strategy/Signal │
│   Generator     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Capital Shield API            │
│   (FastAPI, Auth, Rate Limit)   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Safety Gates                  │
│   • Max Drawdown Check          │
│   • Regime Guard                │
│   • Health Check                │
│   • Structured Rejection        │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Execution       │
│ Adapter         │
│ (External)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Market       │
└─────────────────┘

Side Channels:
  • Metrics/Dashboard
  • Configuration
  • Simulation/Validation
```

**Separation of Concerns**: Risk enforcement happens before execution. The API integrates anywhere via REST endpoints.

---

## Features

### Core Capabilities

1. **Deterministic Safety Rails**
   - Max drawdown protection (configurable thresholds)
   - Regime guards (block BUY in BEAR regime)
   - Health checks (system status validation)
   - Structured rejection reasons (machine-readable codes)

2. **REST API**
   - 7 endpoints: Signal, Risk, Filter, Regime, Health, Metrics, Dashboard
   - API key authentication (tiered: free/pro/professional/enterprise)
   - IP-based rate limiting (10 req/s default, configurable)
   - Structured JSON logging
   - OpenAPI documentation at `/docs`

3. **Simulation/Validation Engine**
   - Historical simulation (test safety rails against crashes)
   - Baseline comparison (with/without safety rails)
   - Crash tests (stress scenarios)
   - Multi-dataset validation
   - RSA calculation (Relative Survival Alpha, v1 formula locked)

4. **Monitoring Dashboard**
   - Real-time metrics (equity curve, drawdown, Sharpe ratio, win rate)
   - System status (health check, uptime, version)
   - Web-based UI at `/dashboard/`

5. **Preset Configurations**
   - **CONSERVATIVE**: -5% drawdown threshold, strict regime guard
   - **BALANCED**: -10% drawdown threshold, strict regime guard (default)
   - **AGGRESSIVE**: -15% drawdown threshold, permissive regime guard

6. **Testing & Validation**
   - 81 tests (comprehensive pytest suite)
   - Quantitative validation (False Positives, Opportunity Cost, Execution Cost)
   - Monte Carlo stress tests

---

## Quickstart

### Prerequisites

- Python 3.8+
- pip
- curl (for testing)

### Installation

```bash
cd boonmindx_capital_shield
pip install -r requirements.txt
```

**Note**: Some modules require `pandas` and `numpy`. Install separately if needed:
```bash
pip install pandas numpy
```

### Run API

```bash
python -m app.main
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Verify it's running**:
```bash
curl http://localhost:8000/api/v1/healthz
```

**API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs.

### Run Tests

```bash
pytest tests/
```

**Expected**: All tests should pass (~81 tests).

### Run Simulation

```bash
python -m live_sim.quick_demo
```

**Note**: Requires historical data files in CSV format (OHLCV columns).

### Open Dashboard

```
http://localhost:8000/dashboard/
```

---

## Bring Your Own Strategy

Capital Shield is **strategy-agnostic**. It does not generate trading signals. Instead, it provides a safety gateway for your existing trading logic.

### Integration Pattern

1. **Your Strategy** generates a signal (BUY/SELL/HOLD)
2. **Capital Shield API** evaluates the signal against safety rails
3. **Decision**: Allow or block with structured rejection reason
4. **Your Execution** proceeds only if allowed

### API Endpoints

- `POST /api/v1/filter` — Core endpoint: Binary allow/block decision
- `POST /api/v1/signal` — Get trading signal (BUY/SELL/HOLD) for asset
- `POST /api/v1/risk` — Assess risk level for trade
- `POST /api/v1/regime` — Detect market regime (BULL/BEAR/SIDEWAYS)
- `GET /api/v1/healthz` — Health check (public, no auth)
- `POST /api/v1/metrics` — Calculate performance metrics
- `GET /api/v1/dashboard/metrics` — Dashboard data (public, no auth)

**Authentication**: API key via `X-API-Key` header.

**See**: `boonmindx_capital_shield/QUICKSTART.md` for detailed integration examples.

---

## Beta Status

**Controlled Beta**: Core API + safety rails are production-grade. Simulation adapters and deployment runbooks are under refinement.

**Public Release**: Q1 2026

### Roadmap

- Additional data adapters (beyond CoinGecko)
- Deployment runbooks (systemd/nginx templates)
- Strategy-agnostic connector interface
- Packaging + installer polish

---

## Security & Safety

### Security Features

- **API Key Authentication** — Tiered access control
- **IP-based Rate Limiting** — 10 req/s default (configurable)
- **Structured Logging** — JSON logs for production monitoring
- **CORS Support** — Configurable cross-origin policies
- **Input Validation** — Pydantic schemas for all endpoints

### Safety Guarantees

- **Deterministic Decisions** — Same inputs produce same outputs (in MOCK mode)
- **Hard Limits** — Configurable thresholds cannot be bypassed
- **Structured Rejection** — Machine-readable codes for all blocked trades
- **No Strategy Logic** — Pure risk management, no trading signals

### Limitations

- **No Database Layer** — API keys are in-memory (config file)
- **No Broker Integration** — Simulation-only, no live trading
- **Single-Asset Focus** — Limited to single-asset evaluation (no portfolio-level)
- **Basic Monitoring** — No advanced alerting or dashboards

---

## Licensing

**Commercial / Proprietary License**

This software is proprietary and protected by copyright. All rights reserved.

### Evaluation License

- **Allowed**: Local/internal testing and development
- **Not Allowed**: Production deployment, public hosting, redistribution, resale

### Production License

**Commercial licensing required** for:
- Production deployment
- Public hosting
- Redistribution
- Resale
- Multi-system / organization-wide use

### How to Obtain a License

Contact **info@boonmind.io** for licensing inquiries.

**License Types**:
- **Evaluation** — Internal testing and development
- **Production** — Single deployment license
- **Enterprise** — Multi-system / organization-wide

### Disclaimer

**No Financial Advice**: This is infrastructure software, not investment advice. No guarantees of profits or returns. Use at your own risk.

---

## Documentation

See `boonmindx_capital_shield/docs/DOCS_INDEX.md` for complete documentation index.

**Key Documents**:
- `QUICKSTART.md` — Quick start guide
- `INFRASTRUCTURE_INVENTORY.md` — Technical inventory
- `PRODUCT_PITCH_ONEPAGER.md` — Product overview
- `TECH_OVERVIEW_MASTER.md` — Technical overview

---

## Contact

- **Email**: info@boonmind.io
- **Website**: [Landing Page](index.html) (local) / [Netlify](https://capital-shield.netlify.app) (when deployed)
- **Contact Form**: Available on landing page

For beta access, licensing inquiries, or technical questions, please contact us.

---

## Disclaimer

**No Financial Advice**: This is infrastructure software, not investment advice.

**No Performance Guarantees**: Capital Shield reduces risk but does not guarantee profits or returns.

**Use at Your Own Risk**: Users are responsible for their own trading decisions.

**No Implied Warranties**: This software is provided "as is" without warranty of any kind.

---

## Copyright

© 2025 Carl Boon. All rights reserved.

**BoonMindX Capital Shield** is proprietary software. Unauthorized use, reproduction, or distribution is prohibited.

See `LICENSE.md` for full licensing terms.

---

**Status**: Controlled Beta | **Public Release**: Q1 2026 | **Version**: 1.0.0
