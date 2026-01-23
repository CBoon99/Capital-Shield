#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -d "venv" && -f "venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

echo "[Round2] Running Monte Carlo Round 2 (30m, 5% leverage, 10K capital)"

python3 -m quant.run_monte_carlo_round2 \
  --dataset-path "MontyCarloTest15Nov.txt" \
  --starting-capital 10000 \
  --leverage 0.05 \
  --timeframe "30m"

echo "[Round2] Results written to reports/monte_carlo_round2/"

