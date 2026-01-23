# BoonMindX Capital Shield — Product One-Pager
**Framework for Risk Management in Trading Systems**

---

## What It Is

**BoonMindX Capital Shield** is a **risk management API framework** that sits between trading signal generators and execution. It provides deterministic safety rails, simulation/validation tooling, and monitoring infrastructure for quantitative trading systems.

**Core Value**: Prevents bad trades from reaching execution, with empirical validation to measure the cost of safety.

---

## What It Is NOT

- ❌ **Not a trading strategy** — It doesn't generate buy/sell signals
- ❌ **Not a profitable trading bot** — It's infrastructure, not alpha generation
- ❌ **Not a backtesting platform** — It's simulation/validation tooling, not a full backtesting suite
- ❌ **Not a guarantee of profits** — It reduces risk, doesn't guarantee returns
- ❌ **Not a live trading system** — No broker integration, simulation-only

---

## Who It's For

### Primary Customers

1. **Quant Funds** — Need risk management layer between signal generation and execution
2. **Signal Sellers** — Want to add risk filtering to their signal APIs
3. **Trading System Developers** — Building custom trading infrastructure and need safety rails
4. **Risk Managers** — Need deterministic risk controls with validation tooling

### Use Cases

- Add risk filtering to existing trading systems
- Validate risk management rules against historical crashes
- Compare performance with/without safety rails
- Monitor trading system health and metrics
- Integrate risk management into custom trading stacks

---

## Core Features

### 1. Deterministic Safety Rails
- **Max Drawdown Protection** — Blocks trades when drawdown exceeds threshold (e.g., -10%)
- **Health Check** — Blocks trades when system health is unhealthy
- **Regime Guard** — Blocks BUY orders in BEAR regime (configurable)
- **Structured Rejection Reasons** — Machine-readable codes for blocked trades

### 2. REST API
- **7 endpoints**: Signal, Risk, Filter, Regime, Health, Metrics, Dashboard
- **API key authentication** — Tiered (free/pro/professional/enterprise)
- **Rate limiting** — IP-based (10 req/s default, configurable)
- **Structured logging** — JSON logs for production monitoring
- **OpenAPI docs** — Auto-generated at `/docs`

### 3. Simulation/Validation Engine
- **Historical simulation** — Run safety rails against historical data
- **Baseline comparison** — Compare performance with/without safety rails
- **Crash tests** — Stress test scenarios (drawdown, health, regime)
- **Multi-dataset validation** — Test across multiple historical periods
- **RSA calculation** — Relative Survival Alpha metric (v1 formula locked)

### 4. Monitoring Dashboard
- **Real-time metrics** — Equity curve, drawdown, Sharpe ratio, win rate
- **System status** — Health check, uptime, version
- **Web-based UI** — Accessible at `/dashboard/` endpoint

### 5. Preset Configurations
- **CONSERVATIVE** — -5% drawdown threshold, strict regime guard
- **BALANCED** — -10% drawdown threshold, strict regime guard (default)
- **AGGRESSIVE** — -15% drawdown threshold, permissive regime guard

### 6. Testing & Validation
- **81 tests** — Comprehensive test suite (pytest)
- **Quantitative validation** — False Positives, Opportunity Cost, Execution Cost
- **Monte Carlo stress tests** — Batch evaluation of scenarios

---

## Technical Stack

- **API**: FastAPI (Python)
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic (data schemas)
- **Testing**: Pytest
- **Data**: Pandas/NumPy (simulation engine)
- **External APIs**: CoinGecko (cryptocurrency data)

---

## What's Missing / Roadmap

### Missing (Not Implemented)
- **Database layer** — API keys are in-memory (config file)
- **Real broker integration** — No execution adapters (simulation-only)
- **Advanced monitoring** — No Prometheus/Grafana integration
- **Deployment automation** — No Docker, Kubernetes, or Terraform
- **Multi-asset portfolio** — Limited to single-asset evaluation
- **Backtesting engine** — No built-in backtesting (only simulation)

### Roadmap (Honest Assessment)
- **Database integration** — Add PostgreSQL/MongoDB for API key persistence
- **Broker adapters** — Add execution adapters for major brokers
- **Advanced metrics** — Add more performance metrics (Sortino, Calmar, etc.)
- **Multi-asset portfolio** — Support portfolio-level risk management
- **Real-time data feeds** — Add WebSocket support for live data
- **Deployment automation** — Add Docker Compose, Kubernetes manifests

---

## Pricing Model (Suggested)

**Framework Licensing**:
- **SaaS per engine** — Monthly subscription per trading engine instance
- **Optional revenue share** — Percentage of AUM for performance-based pricing
- **Enterprise licensing** — On-premise deployment, custom integrations

**Not Included**:
- Trading strategy development
- Broker integration
- Deployment services
- Support/maintenance (unless purchased separately)

---

## Competitive Advantages

1. **Deterministic** — Same inputs produce same outputs (when in MOCK mode)
2. **Validated** — Can test safety rails against historical crashes before deploying
3. **API-First** — REST API that can be integrated into any trading stack
4. **Transparent** — Structured rejection reasons, no black-box decisions
5. **Preset Configurations** — Three risk profiles out of the box

---

## Limitations

1. **No live trading** — Simulation-only, no broker integration
2. **Single-asset focus** — Limited to single-asset evaluation (no portfolio-level)
3. **Basic monitoring** — No advanced alerting or dashboards
4. **No deployment automation** — Manual setup required
5. **Limited data sources** — Only CoinGecko implemented

---

## Getting Started

1. **Install**: `pip install -r requirements.txt`
2. **Run API**: `python -m app.main`
3. **Test**: `pytest tests/`
4. **Simulate**: `python -m live_sim.quick_demo`
5. **Dashboard**: `http://localhost:8000/dashboard/`

See `QUICKSTART.md` for detailed instructions.

---

## Support & Documentation

- **README.md** — Main documentation
- **TECH_OVERVIEW_MASTER.md** — Technical overview
- **INFRASTRUCTURE_INVENTORY.md** — Detailed component inventory
- **QUICKSTART.md** — Quick start guide
- **API Docs** — Auto-generated at `/docs` endpoint

---

## Legal & Compliance

- **No financial advice** — This is infrastructure software, not investment advice
- **No guarantees** — No guarantees of profits or risk reduction
- **Use at your own risk** — Users are responsible for their own trading decisions
- **License** — TBD (suggest: commercial license for framework)

---

**Product One-Pager Date**: 2025-11-16  
**Status**: Framework ready for licensing, missing deployment automation and broker integration
