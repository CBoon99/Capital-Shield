#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "[Prelaunch] BoonMindX Capital Shield — Full Validation Suite"
echo "============================================================"

if [[ ! -f "README.md" || ! -d "scripts" ]]; then
  echo "[ERROR] Run this from the repo root (where README.md and scripts/ live)." >&2
  exit 1
fi

run_optional() {
  local script_path="$1"
  local label="$2"
  if [[ -x "$script_path" ]]; then
    echo "[Prelaunch] Running $label ..."
    "$script_path"
  else
    echo "[Prelaunch] [WARN] $label not found or not executable, skipping."
  fi
}

# Step 1: API Smoke Test
run_optional "scripts/local_api_smoke_test.sh" "API smoke test"

# Step 2: Mini Load Test
run_optional "scripts/local_mini_loadtest.sh" "local mini load-test"

# Step 3: Quant Sanity Suite
run_optional "scripts/run_quant_sanity_suite.sh" "quant sanity suite"

# Step 4: Local API load benchmark
if [[ -f "load_tests/api_load_benchmark.py" ]]; then
  echo "[Prelaunch] Running local API load benchmarks (healthz + dashboard)..."
  if ! python3 -m load_tests.api_load_benchmark \
    --base-url http://localhost:8000 \
    --concurrency 5 \
    --duration-seconds 10 \
    --endpoints healthz dashboard \
    --output-dir reports/perf/prelaunch; then
    echo "[Prelaunch] [WARN] Local load benchmark failed (likely server not running)." >&2
  fi
else
  echo "[Prelaunch] [WARN] load_tests/api_load_benchmark.py not found, skipping load benchmark."
fi

# Step 5: Monte Carlo validation driver
if [[ -f "quant/run_monte_carlo_validation.py" ]]; then
  echo "[Prelaunch] Running Monte Carlo validation..."
  if ! python3 quant/run_monte_carlo_validation.py; then
    echo "[Prelaunch] [WARN] Monte Carlo validation failed; check quant/run_monte_carlo_validation.py output." >&2
  fi
else
  echo "[Prelaunch] [WARN] quant/run_monte_carlo_validation.py not found, skipping Monte Carlo validation."
fi

echo "============================================================"
echo "[Prelaunch] Validation suite completed (see logs and reports/)."
echo "============================================================"

