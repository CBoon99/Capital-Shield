# BoonMindX Capital Shield

**Precision intelligence for a volatile world.**

---

BoonMindX Capital Shield is a safety-first layer on top of the BearHunter trading engine, providing capital protection, deterministic audits, and investor-grade validation.

---

## Where to Start (Phase 1–4 Snapshot)

- **Phase 1 – Design & Architecture**: `PHASE1_COMPLETE_SUMMARY.md`, `PHASE1_PROGRESS.md`
- **Phase 2 – Quantitative Validation**: `PHASE2_COMPLETE_SUMMARY.md`, `run_day10_fp_tests.py`, `run_day11_opportunity_cost.py`, `run_day12_14_execution_costs.py`
- **Phase 3 – Staging & Benchmarks**: `PHASE3_COMPLETE_SUMMARY.md`, `SCALABILITY_BENCHMARKS.md`, `infra/`
- **Phase 4 – Investor Readiness**: `INVESTOR_README.md`, `PHASE4_ROADMAP.md`, `PHASE4_PROGRESS.md`, `PHASE4_COMPLETE_SUMMARY.md`

**Tech entrypoints:**

- Live simulation engine: `live_sim/runner.py`, `live_sim/opportunity_cost_analysis.py`, `live_sim/slippage_model.py`
- Load testing: `load_tests/api_load_benchmark.py`, `load_tests/run_local_server.sh`
- Infrastructure & security: `infra/` (staging plans, security policies, rate limits, logging)
- Investor pack scaffolding: `docs/CAPITAL_SHIELD_ONEPAGER_TEMPLATE.md`, `docs/INVESTOR_DECK_OUTLINE.md`, `docs/INVESTOR_FAQ_TEMPLATE.md`, `INVESTOR_PACK_INTEGRATION_TEMPLATE.md`
- Operational scripts for local validation: `scripts/local_api_smoke_test.sh`, `scripts/run_quant_sanity_suite.sh`, `scripts/local_mini_loadtest.sh` (see `scripts/README.md`)

---

## 🎯 What is BoonMindX Capital Shield?

BoonMindX Capital Shield is a Capital Shield Class system that acts as a universal safety layer between trading engines and market execution. Unlike traditional trading systems that focus on generating alpha, BoonMindX Capital Shield focuses on **preventing catastrophic losses** through empirically validated safety rails.

**Core Philosophy**: We don't predict the future. We refuse to die with the past.

---

## ✨ Key Features

### Safety Rails
- **Max Drawdown Protection**: Automatically blocks trades when drawdown exceeds configured thresholds
- **Health Check**: System-wide health monitoring that can halt trading during infrastructure failures
- **Regime Guard**: Market regime detection (BULL/BEAR/SIDEWAYS) with configurable blocking rules

### Baseline vs Capital Shielded Comparison
- Run identical simulations with and without BoonMindX Capital Shield safety rails
- Measure impact on drawdown, P&L, trade counts, and blocked trades
- Generate comprehensive comparison reports

### Crash Test Lab
- Synthetic stress scenarios to validate BoonMindX Capital Shield safety rails under extreme conditions
- Three crash test scenarios:
  - Drawdown crash test (max drawdown rail triggers)
  - Health failure test (health rail blocks trades)
  - Bear regime strict block test (regime guard semantics)

### Multi-Dataset Investor Validation
- Run validation across multiple historical datasets
- Three BoonMindX Capital Shield presets:
  - **CONSERVATIVE**: Maximum protection (-5% drawdown threshold, strict regime guard)
  - **BALANCED**: Standard protection (-10% drawdown threshold, strict regime guard)
  - **AGGRESSIVE**: Minimal protection (-15% drawdown threshold, permissive regime guard)
- Generate investor-grade validation reports

---

## 📁 Repository Structure

```
boonmindx_capital_shield/
├── app/                    # FastAPI application (BoonMindX Capital Shield API endpoints)
│   ├── routes/            # API endpoints (signal, risk, filter, regime, etc.)
│   ├── core/              # Core logic (auth, config, safety_rails, engine_adapter)
│   ├── models/            # Pydantic models for request/response schemas
│   └── utils/             # Utility functions
├── strategies/            # Strategy plugin interface (Bring Your Own Strategy)
│   ├── strategy_base.py   # Strategy contract (Action enum, SignalDecision, Strategy protocol)
│   ├── registry.py        # Strategy registration and retrieval
│   ├── example_strategy.py # Demo strategy (DEMO ONLY)
│   └── integration.py     # Internal integration point
├── live_sim/              # Live simulation + historical & crash validation
│   ├── runner.py          # Main simulation orchestrator
│   ├── data_loader.py     # Historical data loading
│   ├── shield_client.py   # Capital Shield client for simulations
│   ├── bearhunter_bridge.py  # Direct BearHunter engine bridge
│   ├── historical_validation.py  # Multi-scenario historical validation
│   ├── crash_tests.py     # Crash test scenarios
│   ├── multi_validation.py  # Multi-dataset validation
│   ├── presets.py         # Capital Shield configuration presets
│   ├── reporting.py       # Report generation
│   └── quick_demo.py      # One-command demo runner
├── tests/                 # Test suite (pytest)
│   ├── test_signal.py
│   ├── test_safety_rails.py
│   ├── test_strategies.py # Strategy plugin interface tests
│   ├── test_live_sim_basic.py
│   ├── test_live_sim_crash_tests.py
│   ├── test_presets.py
│   ├── test_multi_validation.py
│   └── test_investor_summary.py
├── docs/                  # Investor & technical documentation
│   ├── INDEX.md
│   └── SHIELD_INVESTOR_OVERVIEW.md
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🚀 Quickstart

### Environment Setup

**Python Version**: Python 3.9+

**Install Dependencies**:
```bash
cd boonmindx_capital_shield
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/ -v
```

Expected output: `79 passed, 1 warning`

### Run the Demo

Run a complete end-to-end validation demo:

```bash
python -m live_sim.quick_demo
```

This will:
- Generate synthetic test data
- Run baseline vs Capital Shielded (Conservative/Balanced/Aggressive) comparisons
- Produce `demo_multi_validation_summary.json` and `DEMO_INVESTOR_VALIDATION_REPORT.md`

### Run Historical Validation

```bash
python -m live_sim.multi_validation \
  --datasets ../data/dataset1.csv ../data/dataset2.csv \
  --symbols BEAR_000 BEAR_001 BULL_150 BULL_151 \
  --presets conservative balanced aggressive \
  --output-json validation_summary.json \
  --output-markdown INVESTOR_VALIDATION_REPORT.md
```

### Run Crash Tests

```bash
python -m live_sim.crash_tests --test all --output-dir crash_test_results
```

---

## 📊 What This Is / Is Not

### ✅ What BoonMindX Capital Shield Is

- **A sandboxed risk engine**: Validates safety rails in a controlled environment
- **A validation lab**: Tests trading strategies against historical data and stress scenarios
- **A safety layer**: Can be integrated between trading engines and execution
- **Empirically validated**: All safety rails tested across multiple scenarios

### ❌ What BoonMindX Capital Shield Is Not

- **A guarantee of profits**: No system can guarantee trading profits
- **Financial advice**: This is research software, not investment advice
- **A live trading bot**: Requires integration with your trading infrastructure
- **A replacement for risk management**: Complements, doesn't replace, proper risk management

---

## 🎛️ BoonMindX Capital Shield Dashboard

A live control panel for monitoring BoonMindX Capital Shield API in real-time.

### Location

The dashboard is located at `dashboard/index.html` and can be accessed when the API is running.

### Running the Dashboard

**Option 1: Via FastAPI (Static Files)**

The dashboard is automatically mounted when running the FastAPI app:

```bash
python -m app.main
```

Then visit: `http://localhost:8000/dashboard/`

**Option 2: Standalone Static Server**

```bash
cd dashboard
python3 -m http.server 8080
```

Then visit: `http://localhost:8080/`

**Note**: When running standalone, update `API_BASE` in `dashboard/app.js` to point to your BoonMindX Capital Shield API instance.

### Dashboard Features

- **Live Metrics**: Real-time updates from `/healthz` and `/dashboard/metrics` endpoints
- **Equity Curve**: Chart showing equity over time
- **Drawdown Curve**: Chart showing max drawdown over time
- **Safety Rails Status**: Visual indicators for max drawdown, health, and regime guard
- **Recent Events Log**: Scrollable log of recent metrics snapshots

The dashboard polls the API every 10 seconds and updates all metrics automatically.

---

## 📚 Documentation

### For Investors & Executives

- **[Investor Overview](docs/SHIELD_INVESTOR_OVERVIEW.md)**: High-level explanation of BoonMindX Capital Shield's value proposition
- **[Investor Validation Report](INVESTOR_VALIDATION_REPORT.md)**: Example multi-dataset validation report

### For Developers

- **[Phase 1-2 Implementation](PHASE2_IMPLEMENTATION_COMPLETE.md)**: API scaffolding and safety rails
- **[Phase 3 Implementation](PHASE3_IMPLEMENTATION_SUMMARY.md)**: Live simulation harness
- **[Phase 4 Implementation](PHASE4_INVESTOR_PACK_COMPLETE.md)**: Multi-dataset validation and presets
- **[Crash Test Validation](CRASH_TEST_VALIDATION.md)**: Safety rail stress testing

### Documentation Index

See [docs/INDEX.md](docs/INDEX.md) for a complete documentation index.

---

## 🔧 API Endpoints

BoonMindX Capital Shield API provides the following endpoints:

- `POST /api/v1/signal` - Get trading signal
- `POST /api/v1/risk` - Assess trade risk
- `POST /api/v1/filter` - **Core BoonMindX Capital Shield endpoint** - Filter trades (applies safety rails)
- `GET /api/v1/regime` - Get market regime classification
- `GET /api/v1/healthz` - Health check
- `GET /api/v1/metrics` - Performance metrics

See [API documentation](README.md#api-endpoints) for details.

---

## 🧪 Validation & Testing

### Test Coverage

- **79 tests** covering all major functionality
- Unit tests for API endpoints, safety rails, presets
- Integration tests for simulations and validations
- Crash test scenarios for stress validation

### Validation Reports

The system generates three types of validation reports:

1. **Historical Validation**: Baseline vs BoonMindX Capital Shielded comparisons on historical data
2. **Crash Test Reports**: Safety rail behavior under stress
3. **Investor Validation Reports**: Multi-dataset, multi-preset analysis

---

## ⚠️ Risk & Legal Disclaimer

**Important**: This software is provided for research and validation purposes only. It is:

- **Not financial advice**: Results shown are based on historical simulations
- **Not a guarantee**: Past performance does not guarantee future results
- **Sandbox only**: All tests run in simulated environments with no real capital
- **Requires integration**: Real-world deployment requires proper integration and oversight

See [docs/SHIELD_INVESTOR_OVERVIEW.md](docs/SHIELD_INVESTOR_OVERVIEW.md) for detailed disclaimers (note: document name uses legacy "SHIELD" naming).

---

## 📝 License & Status

**Status**: ✅ Production-ready validation framework  
**Test Status**: 79/79 tests passing  
**Quality**: Fully tested, deterministic, sandbox-only

---

## 🤝 Contributing

This is a research and validation framework. For questions or issues, please refer to the documentation or create an issue in the repository.

---

**Built with**: Python 3.9+, FastAPI, Pydantic, Pandas, NumPy  
**Test Framework**: pytest  
**Documentation**: Markdown
