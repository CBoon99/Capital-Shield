#!/usr/bin/env bash
set -euo pipefail

echo "[Mini Loadtest] BoonMindX Capital Shield — healthz/dashboard burst"

if [[ ! -f "load_tests/api_load_benchmark.py" ]]; then
  echo "[Mini Loadtest] ERROR: load_tests/api_load_benchmark.py not found. Run this from repo root." >&2
  exit 1
fi

CMD=(python3 -m load_tests.api_load_benchmark
  --base-url http://localhost:8000
  --concurrency 1
  --duration-seconds 5
  --endpoints healthz dashboard
  --output-dir reports/perf)

echo "[Mini Loadtest] Command: ${CMD[*]}"
"${CMD[@]}"

last_report=$(ls -t reports/perf/LOAD_TEST_SUMMARY_*.json 2>/dev/null | head -n 1 || true)
if [[ -n "$last_report" ]]; then
  echo "[Mini Loadtest] Latest report: $last_report"
else
  echo "[Mini Loadtest] No reports found in reports/perf/"
fi

echo "[Mini Loadtest] Complete (check public endpoints only)."

