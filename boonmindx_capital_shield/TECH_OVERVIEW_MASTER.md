# BoonMindX Capital Shield — Technical Walkthrough (Master Reference)

> **Purpose:** Single document that captures what Capital Shield is, how it works end-to-end, which artifacts already exist (300+), and the current status of validation, staging, and investor readiness. Designed so an AI model or new engineer can “load” the entire context quickly without trawling the entire tree.

---

## 1. System Overview

- **What it is:** Observer-coupled risk guardrail that wraps any algorithmic trading stack. It ingests live telemetry (prices, equity curves, risk signals), simulates interventions in real time, and enforces guardrails (block, throttle, alert) before catastrophic drawdowns occur.
- **Core pillars:**
  1. **Quantitative engine** — live simulation + Monte Carlo harness + FP/OC/Execution cost suites.
  2. **API & dashboard** — FastAPI service with public endpoints (`/healthz`, `/dashboard/metrics`) and protected strategy endpoints (`/signal`, `/filter`) behind API key + rate limits.
  3. **Infrastructure** — staging-ready deployment guides (systemd, Nginx, SSL, logging, rate limiting, SSH hardening) with redaction policies.
  4. **Investor / DD package** — scaffolding for decks, FAQs, one-pagers, compliance, and benchmarking narratives.

---

## 2. Repository Structure Highlights

| Area | Key Paths | Notes |
|------|-----------|-------|
| FastAPI app | `app/main.py`, `app/routes/*.py`, `app/models/*.py` | Implements REST endpoints, API key auth, and telemetry serialization. |
| Simulation & quant | `live_sim/*.py`, `run_day10_fp_tests.py`, `run_day11_opportunity_cost.py`, `run_day12_14_execution_costs.py`, `quant/run_monte_carlo_validation.py`, `quant/run_monte_carlo_round2.py` | Covers live sim runner, opportunity-cost + execution-cost harness, and Monte Carlo drivers (Round 1 & Round 2). |
| Load testing | `load_tests/api_load_benchmark.py`, `load_tests/run_local_server.sh`, `scripts/local_mini_loadtest.sh` | Async httpx benchmarker with API-key support; shell helpers for smoke + mini load tests. |
| Operational scripts | `scripts/*.sh`, `scripts/README.md` | `local_api_smoke_test.sh`, `run_quant_sanity_suite.sh`, `local_mini_loadtest.sh`, `prelaunch_validation_suite.sh`, `run_monte_carlo_round2.sh`. |
| Infra & security | `infra/**/*.md`, `infra/providers/CHOSEN_PROVIDER/*` | Staging plan, provider selection, SSH hardening, firewall templates, systemd + Nginx configs, secrets policy, redaction guide. |
| Reports & docs | `reports/**`, `SCALABILITY_BENCHMARKS*.md`, `INVESTOR_*`, `PHASE*_*.md` | Each phase/day log, benchmark templates, investor messaging, technical DD index, etc. |

---

## 3. API Surface (FastAPI)

Public endpoints:
- `GET /api/v1/healthz` — health probe (used by smoke + load tests).
- `GET /api/v1/dashboard/metrics` — aggregated telemetry for dashboard.

Protected endpoints (require `X-API-Key` + rate limits defined in `infra/RATE_LIMIT_PROFILES.md`):
- `POST /api/v1/signal` — per-asset guardrail evaluation (takes `asset`, `price_history`, `volume_history`, etc.).
- `POST /api/v1/filter` — filters strategy outputs by Capital Shield policies.
- Additional strategy/risk endpoints exist under `app/routes/*.py` (e.g., `/risk`, `/regime`, etc.) but remain under API-key enforcement + IP rate limits (~10 req/s per IP per protected endpoint).

Supporting modules:
- `app/core/*` — config, auth, rate limiting, logging middleware.
- `app/models/*` — Pydantic models for signals, filters, risk metrics.

---

## 4. Quantitative Validation Pipeline

1. **False-Positive Regression (`run_day10_fp_tests.py`)**
   - Validates that guardrails do not over-react to benign volatility across multiple presets (conservative / balanced / aggressive). Outputs under `reports/fp_test_day10/`.

2. **Opportunity Cost Analysis (`run_day11_opportunity_cost.py`)**
   - Ensures interventions do not materially degrade strategy PnL when conditions are favorable. Produces JSON/CSV in `reports/opportunity_cost/`.

3. **Execution Cost Modeling (`run_day12_14_execution_costs.py` + `live_sim/slippage_model.py`)**
   - Quantifies latency penalties, slippage (fixed + volatility scaled), and execution costs. Reports under `reports/execution_costs/`.

4. **Monte Carlo Harness**
   - **Round 1 (`quant/run_monte_carlo_validation.py`)** — template driver (100 runs) tied to placeholder scenarios; outputs `reports/monte_carlo/`.
   - **Round 2 (`quant/run_monte_carlo_round2.py`)** — uses `MontyCarloTest15Nov.txt`, 30 m candles, 5 % leverage, 10 K capital, currently processes 4 synthetic assets (placeholder for 300). Outputs stored in `reports/monte_carlo_round2/` with human summary + investor template.
   - **Operational wrapper** — `scripts/run_monte_carlo_round2.sh` (python3), also referenced in `scripts/prelaunch_validation_suite.sh`.

5. **Pre-Launch Validation Suite (`scripts/prelaunch_validation_suite.sh`)**
   - Sequences smoke test → mini load → quant sanity suite → local benchmark (`load_tests/api_load_benchmark.py`) → Monte Carlo driver. Produces logs and artifacts across `/tmp`, `reports/perf/prelaunch/`, and `reports/monte_carlo/`.

---

## 5. Load & Performance Benchmarks

- `load_tests/api_load_benchmark.py` supports async scenarios, concurrency, duration, endpoint selection, API-key headers, and JSON payload injection.
- `SCALABILITY_BENCHMARKS.md` — documents local benchmark results (public endpoints) with placeholders for staging runs.
- `SCALABILITY_BENCHMARKS_STAGING_TEMPLATE.md` + staging report templates (`reports/perf/staging/**`) cover distributed load design, rate-limit notes, and redacted result formats.
- Known behavior:
  - Public endpoints: low latency (single-digit ms) with zero errors locally.
  - Protected endpoints: intentionally rate-limited (≈10 req/s/IP). Load tests document 429 behavior instead of weakening limits.
- `scripts/local_mini_loadtest.sh` (healthz + dashboard, concurrency=1, duration=5s) and `scripts/local_api_smoke_test.sh` for quick validation.

---

## 6. Infrastructure & Security

- **Staging plan & provider selection:** `infra/STAGING_PLAN.md`, `PHASE3_PROVIDER_DECISION.md`, `infra/STAGING_PROVIDER_OPTIONS.md`.
- **Server creation & hardening:** Day 5–9 docs (`infra/STAGING_DAY5_SERVER_CREATION_PLAN.md`, `infra/STAGING_SSH_HARDENING.md`, `infra/STAGING_DAY9_*`). Includes SSH key setup, disable password/root login, UFW rules, firewall templates, Fail2ban notes.
- **Deployment runbooks:** Day 10–11 templates (`infra/STAGING_DAY10_DEPLOYMENT_LOG_TEMPLATE.md`, `infra/STAGING_DAY10_SYSTEMD_SERVICE_TEMPLATE.md`, `infra/STAGING_DAY10_NGINX_CONFIG_TEMPLATE.md`, `infra/providers/CHOSEN_PROVIDER/DAY10_*`, `DAY11_*`).
- **Logging & secrets:** `infra/LOGGING_PIPELINE.md`, `infra/SECURITY_SECRETS_POLICY.md`, `infra/REDACTION_GUIDE.md`, `infra/ENVIRONMENT_VARIABLES_TEMPLATE.env`, `infra/ENV_AND_GITIGNORE_POLICY.md`.
- **Rate limits:** `infra/RATE_LIMIT_PROFILES.md` enumerates local/staging/prod per-endpoint thresholds.
- **Redaction commitments:** all staging execution logs use `<REDACTED_*>` placeholders; real metrics/IPs remain private.

---

## 7. Documentation & Phase Tracking

- **Phase summaries:** `PHASE1_COMPLETE_SUMMARY.md`, `PHASE2_COMPLETE_SUMMARY.md`, `PHASE3_COMPLETE_SUMMARY.md`, `PHASE4_COMPLETE_SUMMARY.md`.
- **Daily logs:** `PHASE*_DAY*_STATUS.md` (Phase 1–4).
- **Roadmaps & progress:** `PHASE1_PROGRESS.md` … `PHASE4_PROGRESS.md`, `PHASE4_ROADMAP.md`. Phase 4 currently marked 100% (templates + scripts complete; real investor content private).
- **Benchmark notes:** `BENCHMARK_EXECUTION_NOTES.md` (chronological log of load tests, Monte Carlo rounds, staging plans).
- **Investor / partner pack:**
  - Entry point: `INVESTOR_README.md`.
  - Deck/FAQ/messaging: `docs/INVESTOR_DECK_OUTLINE.md`, `docs/INVESTOR_FAQ_TEMPLATE.md`, `INVESTOR_DECK_PLACEHOLDER_SECTIONS.md`, `INVESTOR_MESSAGING_GUIDE_TEMPLATE.md`, `INVESTOR_EMAIL_TEMPLATES.md`.
  - One-pagers: `docs/CAPITAL_SHIELD_ONEPAGER_TEMPLATE.md`, `INVESTOR_BENCHMARKS_ONEPAGER_TEMPLATE.md`.
  - Technical DD: `docs/TECHNICAL_DD_INDEX.md`, `TECHNICAL_DD_OVERVIEW_TEMPLATE.md`, `TECHNICAL_DD_ARCHITECTURE_DIAGRAMS.md`, `TECHNICAL_DD_CHECKLIST_TEMPLATE.md`, `TECHNICAL_BENCHMARKS_DD_CHECKLIST.md`, `TECHNICAL_DD_PACKAGE_README.md`.

---

## 8. Current Quant & Monte Carlo Status

- **Round 1 Monte Carlo:** Template driver ready; awaiting real scenario feeds. Outputs stored in `reports/monte_carlo/`.
- **Round 2 Monte Carlo:** Completed on placeholder dataset (4 assets, 30m, 5% leverage). Summaries:
  - `ROUND2_AGGREGATE.json` — min/max/mean/median final equity, drawdown bounds.
  - `R2_HUMAN_SUMMARY.md` — narrative summary + per-asset table.
  - `R2_ASSET_SELECTION_NOTES.md` — explains 4-asset limit and schema for scaling to 300 assets.
  - `INVESTOR_SUMMARY_TEMPLATE.md` — redacted template for investor-facing narratives (fill offline).
- **FP / OC / Execution** harnesses last run successfully (see `reports/fp_test_day10/`, `reports/opportunity_cost/`, `reports/execution_costs/`).
- **Prelaunch suite** is ready; run `scripts/prelaunch_validation_suite.sh` locally to chain all tests (note: sandbox cannot bind to `localhost:8000`).

---

## 9. Outstanding Work / Next Steps

1. **Data scaling:** Inject full 300-asset dataset into `MontyCarloTest15Nov.txt` (or new files) and re-run Round 2 (or Round 3) outside Cursor; keep summaries redacted in Git.
2. **Staging distributed load tests:** Use `reports/perf/staging/` templates once staging IPs + load agents are approved; commit only redacted summaries.
3. **Investor pack population:** Fill templates privately (deck, one-pager, benchmarks, pricing) and share under NDA.
4. **Outreach readiness:** Use `INVESTOR_PACK_INTEGRATION_TEMPLATE.md` to assemble deliverables for investors/partners; verify scripts + docs selected match sharing level (public vs NDA).
5. **Automation hooks:** Optionally integrate scripts into CI (smoke, quant, Monte Carlo) once private infrastructure is configured.

---

## 10. Quick Entry Points for AI Agents / New Contributors

- **Start here:** `README.md` → “Where to Start (Phase 1–4 Snapshot)” + `INVESTOR_README.md`.
- **API details:** `app/` folder + `SCALABILITY_BENCHMARKS.md`.
- **Simulation logic:** `live_sim/runner.py`, `live_sim/slippage_model.py`, `run_day10_fp_tests.py`.
- **Load testing:** `load_tests/api_load_benchmark.py`, `scripts/local_mini_loadtest.sh`.
- **Security/infra:** `infra/` directory, especially `SECURITY_SECRETS_POLICY.md` & `REDACTION_GUIDE.md`.
- **Operational scripts:** `scripts/README.md` summarises every helper (smoke, quant, load, Monte Carlo).
- **Benchmarks & notes:** `BENCHMARK_EXECUTION_NOTES.md`, `reports/monte_carlo_round2/`.

---

**TL;DR:** Capital Shield’s entire lifecycle—design → quant validation → staging infrastructure → investor readiness—is documented in the repo. FastAPI endpoints are production-ready (public endpoints proven locally; protected ones rate-limited), quant harnesses are templated with placeholder datasets, infrastructure is fully scripted with redaction safeguards, and investor/DD packs exist for quick population under NDA. This document ties the 300+ files, Monte Carlo runs, load tests, and security policies into one map for rapid mental loading. 

