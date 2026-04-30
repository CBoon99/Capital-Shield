# v1 Decisions Locked — 16 November 2025

**Status**: ✅ All core v1 decisions finalized and implemented  
**Purpose**: Single source of truth for Capital Shield + BearHunter v1 configuration

---

## 1. RSA Formula (LOCKED)

**Formula**:
```
TE_norm  = clamp(terminal_equity / initial_equity, 0.0, 2.0) / 2.0
MDD_norm = max_drawdown_fraction (0.0 to 1.0)
RSA = 0.5 * TE_norm + 0.5 * (1.0 - MDD_norm)
```

**Implementation**:
- Module: `live_sim/rsa.py`
- Integrated into:
  - Monte Carlo Round 2 (`quant/run_monte_carlo_round2.py`)
  - Shadow-live runner (`scripts/run_shadow_live_coingecko.py`)
  - All future FP/OC/Execution reports

**Interpretation**:
- RSA near 1.0: Excellent survival (high equity + low drawdown)
- RSA near 0.5: Neutral (break-even + moderate drawdown)
- RSA near 0.0: Poor survival (low equity or catastrophic drawdown)

---

## 2. Default Preset (LOCKED)

**Preset**: BALANCED

**Philosophy**: Survival-first, but allows normal-regime trading

**Thresholds** (v1):
- Volatility: 5% (blocks if exceeded)
- Max Drawdown: -20% (blocks if exceeded)

**Rejection Reasons** (structured):
- Machine-readable codes: `VOL_BREACH`, `DD_BREACH`, `LIQ_STRESS`, `CORR_BREAKDOWN`, etc.
- Human-readable messages: "blocked: intraday volatility breach + correlation breakdown"

**Visibility**:
- Logged in API responses (where appropriate)
- Logged in internal telemetry
- Surfaced in investor reports

---

## 3. Data Source (LOCKED)

**Provider**: CoinGecko (free API)

**Mode**: Shadow-live (data-only, no execution)

**Implementation**:
- Client: `data/coin_gecko_client.py`
- Shadow-live runner: `scripts/run_shadow_live_coingecko.py`

**Default Watchlist**:
- bitcoin
- ethereum
- cardano
- solana
- polkadot

**Data Format**:
- Fetches historical OHLCV (approximated from CoinGecko snapshots)
- Normalizes into internal format used by Monte Carlo/FP/OC harnesses
- Polling interval: 5 minutes (configurable)

**Rate Limiting**:
- CoinGecko free tier: ~50 calls/minute
- Client enforces 1.2s between requests

---

## 4. Business Model (LOCKED)

**Model**: Hybrid SaaS + Optional Revenue Share

**Tiers** (v1):
1. **SaaS per Engine**
   - Monthly subscription for Capital Shield API access
   - Tiered by request volume
   
2. **Enterprise On-Prem**
   - Self-hosted deployment
   - Annual licensing fee

3. **Revenue Share** (Optional)
   - For select clients: % of AUM or % of alpha generated
   - Negotiated case-by-case

**Positioning**:
- Primary wedge: SaaS for small quant funds and prop desks
- Enterprise expansion after initial customer success stories

**Documentation Updated**:
- `INVESTOR_QA_COMPLETE.md` (Section A.9)
- `docs/CURRENT_PRODUCT_STATE_2025-11-16.md` (Section 5)
- `TODO_CURRENT_PRODUCT_STATE_2025-11-16.md` (removed from TODO)

---

## 5. Hosting (LOCKED)

**v1 Infrastructure**: Hardened VPS

**Stack**:
- **Application**: FastAPI + Uvicorn
- **Reverse Proxy**: Nginx with TLS (Let's Encrypt)
- **Process Manager**: systemd
- **Logging**: Local files + logrotate
- **Security**: SSH keys only, UFW firewall, API key auth, rate limiting

**Documentation**:
- `docs/INFRA_NOTES_V1.md` (comprehensive infrastructure guide)

**Future State** (post-raise):
- AWS ECS/Lambda
- Redis for distributed caching
- Prometheus/Grafana monitoring
- CloudWatch logging
- SOC2 Type II compliance

---

## 6. Integration Path (LOCKED)

**v1 Approach**: Shadow-live via CoinGecko

**Workflow**:
1. Poll CoinGecko for live prices (5-minute intervals)
2. Normalize to internal OHLCV format
3. Feed into Capital Shield + BearHunter evaluation pipeline
4. Log decisions (ALLOW/BLOCK) with structured reasons
5. Calculate RSA over time
6. **No actual trades executed** (shadow mode only)

**Next Steps** (post-v1):
- Broker integration (IBKR or crypto exchange)
- Real-time websocket feeds
- Order execution layer (with slippage/latency modeling)

---

## 7. Documentation Updates

**Updated Files**:
- ✅ `live_sim/rsa.py` (RSA formula implementation)
- ✅ `quant/run_monte_carlo_round2.py` (RSA integration)
- ✅ `data/coin_gecko_client.py` (CoinGecko client)
- ✅ `scripts/run_shadow_live_coingecko.py` (shadow-live runner)
- ✅ `docs/INFRA_NOTES_V1.md` (infrastructure documentation)
- ✅ `V1_DECISIONS_LOCKED_2025-11-16.md` (this file)

**Pending Updates** (to be completed):
- `docs/CURRENT_PRODUCT_STATE_2025-11-16.md` (add v1 decisions)
- `TODO_CURRENT_PRODUCT_STATE_2025-11-16.md` (remove resolved items)
- `INVESTOR_QA_COMPLETE.md` (add RSA formula, business model)
- `TECH_OVERVIEW_MASTER.md` (add CoinGecko, shadow-live, RSA)

---

## 8. How to Run v1

### Monte Carlo Round 2 (with RSA)
```bash
cd /Users/carlboon/Documents/capital-shield/boonmindx_capital_shield
python3 -m quant.run_monte_carlo_round2 \
  --dataset-path MontyCarloTest15Nov.txt \
  --starting-capital 10000 \
  --leverage 0.05 \
  --timeframe 30m
```

**Output**: `reports/monte_carlo_round2/` (includes RSA scores)

### Shadow-Live (CoinGecko)
```bash
cd /Users/carlboon/Documents/capital-shield/boonmindx_capital_shield
python3 scripts/run_shadow_live_coingecko.py \
  --preset BALANCED \
  --poll-interval 300 \
  --history-days 7 \
  --max-iterations 12  # Run for 1 hour (12 * 5 min)
```

**Output**: `reports/shadow_live/` (decision logs with RSA)

### Test CoinGecko Client
```bash
cd /Users/carlboon/Documents/capital-shield/boonmindx_capital_shield
python3 -m data.coin_gecko_client
```

**Output**: Console output showing fetched prices for default watchlist

---

## 9. What's NOT in v1

**Explicitly Out of Scope**:
- Real broker integration (IBKR, exchanges)
- Order execution
- Live capital deployment
- Slippage/latency modeling (frictionless assumptions)
- Multi-tenancy
- AWS infrastructure
- SOC2 compliance
- FCA licensing
- Team beyond Carl Boon + AI collaborators

**Timeline**: These are post-raise / Phase 5+ items

---

## 10. Next Steps (Post-v1)

1. **Run shadow-live for 7-14 days**
   - Collect decision logs
   - Validate RSA calculations
   - Identify any edge cases

2. **Extend Monte Carlo dataset**
   - Expand `MontyCarloTest15Nov.txt` to full 300 assets
   - Re-run Round 2 with RSA

3. **Broker integration planning**
   - Choose first broker (IBKR vs Kraken)
   - Design read-only integration
   - Add slippage/latency models

4. **Investor materials**
   - Fill templates with real (redacted) data
   - Prepare demo pack
   - Create pitch deck

5. **First pilot customer**
   - Identify 3-5 target prospects
   - Run controlled pilot with £100-1K
   - Collect feedback and iterate

---

**Last Updated**: 2025-11-16  
**Status**: ✅ v1 Configuration Locked and Implemented

