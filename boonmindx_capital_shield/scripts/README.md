# Scripts — BoonMindX Capital Shield (Template)

---

## local_api_smoke_test.sh

- Purpose: Start the FastAPI server locally, check `/api/v1/healthz` and `/api/v1/dashboard/metrics`.
- Usage: Run from repo root (`bash scripts/local_api_smoke_test.sh`).
- Expected: Both endpoints return HTTP 200. Logs saved to `/tmp/bmx_local_smoke.log`.
- Notes: Designed for local machines; sandboxed environments may not allow binding to `localhost:8000`.

---

## run_quant_sanity_suite.sh

- Purpose: Run the three core quantitative validation scripts.
- Steps executed:
  1. `python3 run_day10_fp_tests.py`
  2. `python3 run_day11_opportunity_cost.py`
  3. `python3 run_day12_14_execution_costs.py`
- Expected: Each script completes without error, regenerating the reports under `reports/`.

---

## local_mini_loadtest.sh

- Purpose: Run a tiny load-test against public endpoints (`healthz`, `dashboard`) to confirm the stack responds.
- Command executed: `python3 -m load_tests.api_load_benchmark --concurrency 1 --duration-seconds 5 ...`
- Output: A new `LOAD_TEST_SUMMARY_*.json` in `reports/perf/`.
- Notes: Only hits public endpoints; protected endpoints require API keys and rate-limit coordination.

---

## prelaunch_validation_suite.sh

- Purpose: Full pre-launch guardrail wrapper (smoke → mini load-test → quant suite → local benchmark → Monte Carlo driver).
- Order of operations:
  1. `scripts/local_api_smoke_test.sh` (if present)
  2. `scripts/local_mini_loadtest.sh` (if present)
  3. `scripts/run_quant_sanity_suite.sh` (if present)
  4. `python3 -m load_tests.api_load_benchmark --base-url http://localhost:8000 --concurrency 5 --duration-seconds 10 --endpoints healthz dashboard --output-dir reports/perf/prelaunch`
  5. `python3 quant/run_monte_carlo_validation.py`
- Usage:
  ```bash
  chmod +x scripts/prelaunch_validation_suite.sh
  ./scripts/prelaunch_validation_suite.sh
  ```
- Outputs: API logs in `/tmp`, load-test summaries in `reports/perf/prelaunch/`, quant reports under `reports/`, Monte Carlo artifacts under `reports/monte_carlo/`.
- Notes: Monte Carlo results remain placeholders until wired to real scenarios.

---

## run_monte_carlo_round2.sh

- Purpose: Runs the custom Monte Carlo Round 2 stress test using `MontyCarloTest15Nov.txt`.
- Configuration: 30-minute candles, 5% leverage, 6-month horizon (full dataset), 10,000 starting capital.
- Usage:
  ```bash
  chmod +x scripts/run_monte_carlo_round2.sh
  ./scripts/run_monte_carlo_round2.sh
  ```
- Output: Per-asset JSON files + aggregate summary under `reports/monte_carlo_round2/ROUND2_*`.
- Notes: Uses the same Monte Carlo harness as the prelaunch suite; dataset is placeholders only.

---

## Sandbox Limitations

- Cursor’s sandbox may block binding to `localhost:8000`. This does **not** indicate a problem with the scripts.
- For accurate results, run these scripts on your local development machine or staging environment. 

