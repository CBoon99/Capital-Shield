# Documentation Index — BoonMindX Capital Shield

**Complete documentation for developers, buyers, and integrators.**

---

## Quick Start

### Getting Started
- **[QUICKSTART.md](../QUICKSTART.md)** — Quick start guide with installation, API setup, testing, and simulation commands

### Product Overview
- **[PRODUCT_PITCH_ONEPAGER.md](../PRODUCT_PITCH_ONEPAGER.md)** — Product overview: what it is, what it isn't, who it's for, core features, limitations

---

## Technical Documentation

### Infrastructure & Architecture
- **[INFRASTRUCTURE_INVENTORY.md](../INFRASTRUCTURE_INVENTORY.md)** — Detailed technical inventory of all subsystems, maturity ratings, and buyer notes

### Technical Overview
- **[TECH_OVERVIEW_MASTER.md](../TECH_OVERVIEW_MASTER.md)** — Comprehensive technical overview for AI models and developers

### Infrastructure Notes
- **[INFRA_NOTES_V1.md](INFRA_NOTES_V1.md)** — V1 infrastructure decisions (VPS, Nginx, TLS, systemd)

---

## Product State & Decisions

### Current State
- **[CURRENT_PRODUCT_STATE_2025-11-16.md](CURRENT_PRODUCT_STATE_2025-11-16.md)** — Honest assessment of current reality vs. aspirational state

### V1 Decisions
- **[V1_DECISIONS_LOCKED_2025-11-16.md](../V1_DECISIONS_LOCKED_2025-11-16.md)** — Locked v1 decisions (RSA formula, presets, business model, hosting)

---

## Testing & Validation

### Readiness
- **[READY_TO_TEST_V1.md](../READY_TO_TEST_V1.md)** — Comprehensive testing guide for v1

### Code Audit
- **[CODE_AUDIT_V1_2025-11-16.md](../CODE_AUDIT_V1_2025-11-16.md)** — Code audit findings and readiness check

---

## Templates & Planning

### Investor Templates
- Templates moved to root during cleanup (see `CLEANUP_PLAN.md` for details)
- Commercial models, partner models, enterprise requirements, licensing FAQ, technical DD templates available on request

### Technical Due Diligence
- **[TECHNICAL_DD_INDEX.md](TECHNICAL_DD_INDEX.md)** — Index for technical due-diligence reviewers

---

## API Documentation

### Interactive Docs
- **Live API Docs**: `http://localhost:8000/docs` (when API is running)
- **OpenAPI Schema**: Auto-generated at `/docs` endpoint

### API Endpoints

1. **Signal Evaluation**
   - `POST /api/v1/signal` — Get trading signal (BUY/SELL/HOLD)
   - `POST /api/v1/risk` — Assess risk level
   - `POST /api/v1/filter` — **Core endpoint**: Binary allow/block decision

2. **Market Regime**
   - `POST /api/v1/regime` — Detect market regime (BULL/BEAR/SIDEWAYS)

3. **Health & Metrics**
   - `GET /api/v1/healthz` — Health check (public, no auth)
   - `POST /api/v1/metrics` — Calculate performance metrics
   - `GET /api/v1/dashboard/metrics` — Dashboard data (public, no auth)

**Authentication**: API key via `X-API-Key` header (tiered: free/pro/professional/enterprise)

**Rate Limiting**: 10 requests/second per IP (configurable)

---

## Simulation & Validation

### Quick Demo
```bash
python -m live_sim.quick_demo
```

### Multi-Dataset Validation
```bash
python -m live_sim.multi_validation \
  --datasets datasets/benign/bull_2017_synthetic.csv \
  --symbols BEAR_000 BEAR_001 \
  --presets conservative balanced aggressive \
  --output-json validation_summary.json
```

### Crash Tests
```bash
python -m live_sim.crash_tests --test all --output-dir crash_test_results
```

### Monte Carlo Validation
```bash
bash scripts/run_monte_carlo_round2.sh
```

---

## Testing

### Run All Tests
```bash
pytest tests/
```

### Test Coverage
- **81 tests** — Comprehensive test suite
- **Modules**: Safety rails, API endpoints, simulation engine, data adapters

### Operational Scripts
- `scripts/local_api_smoke_test.sh` — API smoke test
- `scripts/run_quant_sanity_suite.sh` — Quantitative validation suite
- `scripts/local_mini_loadtest.sh` — Mini load test

See `scripts/README.md` for details.

---

## Configuration

### Environment Variables
See `infra/ENVIRONMENT_VARIABLES_TEMPLATE.env` for all configuration options.

**Key Settings**:
- `ENGINE_MODE` — MOCK or LIVE
- `CAPITAL_SHIELD_MODE` — STRICT or PERMISSIVE
- `MAX_DRAWDOWN_THRESHOLD` — Drawdown limit (e.g., -0.10 for -10%)
- `BLOCK_BEAR_BUYS` — Enable/disable regime guard

### Presets
- **CONSERVATIVE**: -5% drawdown, strict regime guard
- **BALANCED**: -10% drawdown, strict regime guard (default)
- **AGGRESSIVE**: -15% drawdown, permissive regime guard

---

## Deployment

### Local Development
- See `QUICKSTART.md` for local setup
- API runs on `http://localhost:8000`
- Dashboard at `http://localhost:8000/dashboard/`

### Production Deployment
- **Status**: Deployment runbooks under refinement
- **Infrastructure**: VPS with Nginx, systemd, TLS (see `INFRA_NOTES_V1.md`)
- **Templates**: See `infra/` directory for deployment templates

---

## Support & Contact

- **Email**: info@boonmind.io
- **Landing Page**: See root `index.html` for contact form
- **Licensing**: See root `LICENSE.md` for commercial licensing terms

---

## Status

**Current Version**: 1.0.0  
**Status**: Controlled Beta  
**Public Release**: Q1 2026

---

**Last Updated**: 2025-11-16
