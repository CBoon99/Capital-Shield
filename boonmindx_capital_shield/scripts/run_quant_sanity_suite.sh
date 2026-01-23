#!/usr/bin/env bash
set -euo pipefail

echo "[Quant Sanity] BoonMindX Capital Shield — core validation suite"

scripts=(run_day10_fp_tests.py run_day11_opportunity_cost.py run_day12_14_execution_costs.py)

for script in "${scripts[@]}"; do
  if [[ ! -f "$script" ]]; then
    echo "[Quant Sanity] ERROR: $script not found. Run this from repo root." >&2
    exit 1
  fi
done

run_script() {
  local script="$1"
  echo ""
  echo "============================================================"
  echo "[Quant Sanity] Running $script"
  echo "============================================================"
  python3 "$script"
}

run_script run_day10_fp_tests.py
run_script run_day11_opportunity_cost.py
run_script run_day12_14_execution_costs.py

echo ""
echo "[Quant Sanity] ✅ All scripts completed without error"

