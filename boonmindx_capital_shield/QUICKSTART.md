# Quick Start Guide — BoonMindX Capital Shield
**For Buyers & Developers**

---

## Prerequisites

- Python 3.8+
- pip
- curl (for testing)

---

## 1. Install

```bash
cd boonmindx_capital_shield
pip install -r requirements.txt
```

**Dependencies**:
- FastAPI, Uvicorn (API server)
- Pydantic (data validation)
- Pytest (testing)

**Note**: Some modules use `pandas` and `numpy` but they're not in requirements.txt. Install separately if needed:
```bash
pip install pandas numpy
```

---

## 2. Run API

**Start the API server**:
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

**Expected response**:
```json
{
  "status": "ok",
  "uptime": 5,
  "version": "1.0.0",
  "timestamp": "2025-11-16T12:00:00Z"
}
```

**API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs.

---

## 3. Run Tests

**Run all tests**:
```bash
pytest tests/
```

**Run specific test file**:
```bash
pytest tests/test_safety_rails.py
```

**Run with verbose output**:
```bash
pytest tests/ -v
```

**Expected**: All tests should pass (~81 tests).

---

## 4. Run Simulation

**Quick demo** (single simulation):
```bash
python -m live_sim.quick_demo
```

**Multi-dataset validation**:
```bash
python -m live_sim.multi_validation \
  --datasets datasets/benign/bull_2017_synthetic.csv \
  --symbols BEAR_000 BEAR_001 \
  --presets conservative balanced aggressive \
  --output-json validation_summary.json
```

**Crash tests** (stress scenarios):
```bash
python -m live_sim.crash_tests --test all --output-dir crash_test_results
```

**Note**: Requires historical data files in CSV format (OHLCV columns).

---

## 5. Open Dashboard

**Start API** (if not already running):
```bash
python -m app.main
```

**Open in browser**:
```
http://localhost:8000/dashboard/
```

**What you'll see**:
- System status (up/down)
- Uptime
- Equity curve chart (if metrics available)
- Drawdown chart (if metrics available)
- Current metrics (Sharpe, drawdown, win rate)

**Note**: Dashboard polls `/api/v1/healthz` and `/api/v1/dashboard/metrics` every 10 seconds.

---

## 6. Test API Endpoints

**Health check** (no auth required):
```bash
curl http://localhost:8000/api/v1/healthz
```

**Get signal** (requires API key):
```bash
curl -X POST http://localhost:8000/api/v1/signal \
  -H "X-API-Key: test_free_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "BTC",
    "price_history": [100, 102, 101, 105, 103],
    "volume_history": [1000, 1200, 1100, 1300, 1250]
  }'
```

**Filter trade** (core endpoint):
```bash
curl -X POST http://localhost:8000/api/v1/filter \
  -H "X-API-Key: test_free_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "BTC",
    "action": "BUY",
    "price_history": [100, 102, 101, 105, 103],
    "volume_history": [1000, 1200, 1100, 1300, 1250]
  }'
```

**Get metrics**:
```bash
curl -X POST http://localhost:8000/api/v1/metrics \
  -H "X-API-Key: test_free_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "trades": [
      {"pnl": 100, "entry_price": 100, "exit_price": 110},
      {"pnl": -50, "entry_price": 110, "exit_price": 105}
    ],
    "equity_curve": [10000, 10100, 10050]
  }'
```

**Test API keys** (from `app/core/config.py`):
- `test_free_key_12345` — Free tier (100 req/day)
- `test_pro_key_67890` — Pro tier (10,000 req/day)
- `test_professional_key_abcde` — Professional tier (100,000 req/day)
- `test_enterprise_key_fghij` — Enterprise tier (unlimited)

---

## 7. Configuration

**Environment variables** (see `infra/ENVIRONMENT_VARIABLES_TEMPLATE.env`):

```bash
# API Configuration
SHIELD_API_HOST=0.0.0.0
SHIELD_API_PORT=8000
SHIELD_API_DEBUG=false

# Engine Mode
ENGINE_MODE=MOCK  # or LIVE

# Capital Shield Mode
CAPITAL_SHIELD_MODE=STRICT  # or PERMISSIVE

# Safety Rails
MAX_DRAWDOWN_THRESHOLD=-0.10  # -10%
BLOCK_BEAR_BUYS=true
HEALTH_CHECK_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

**Create `.env` file** (optional):
```bash
cp infra/ENVIRONMENT_VARIABLES_TEMPLATE.env .env
# Edit .env with your settings
```

---

## 8. Operational Scripts

**API smoke test**:
```bash
bash scripts/local_api_smoke_test.sh
```

**Quantitative validation suite**:
```bash
bash scripts/run_quant_sanity_suite.sh
```

**Mini load test**:
```bash
bash scripts/local_mini_loadtest.sh
```

**Shadow-live mode** (CoinGecko):
```bash
python scripts/run_shadow_live_coingecko.py --max-iterations 3
```

**Note**: Some scripts may require additional setup or data files.

---

## 9. Troubleshooting

**Port already in use**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

**Import errors**:
```bash
# Make sure you're in the right directory
cd boonmindx_capital_shield
# Install missing dependencies
pip install pandas numpy requests
```

**API key errors**:
- Check that `X-API-Key` header is set
- Use one of the test keys from `app/core/config.py`
- Check API key format (no spaces, exact match)

**Dashboard not loading**:
- Make sure API is running
- Check browser console for errors
- Verify `/api/v1/dashboard/metrics` endpoint is accessible

---

## 10. Next Steps

1. **Read documentation**: See `README.md` and `TECH_OVERVIEW_MASTER.md`
2. **Explore API**: Visit `http://localhost:8000/docs` for interactive docs
3. **Run tests**: Verify everything works with `pytest tests/`
4. **Try simulations**: Run `python -m live_sim.quick_demo`
5. **Customize**: Modify `app/core/config.py` for your API keys and settings

---

**Quick Start Date**: 2025-11-16  
**Status**: All commands verified (may need pandas/numpy installed separately)
