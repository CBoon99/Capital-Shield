#!/usr/bin/env bash
set -euo pipefail

echo "[Smoke] BoonMindX Capital Shield API — local dev check"

if [[ ! -f "load_tests/run_local_server.sh" ]]; then
  echo "[Smoke] ERROR: load_tests/run_local_server.sh not found. Run this script from repo root." >&2
  exit 1
fi

echo "[Smoke] Starting API server..."
./load_tests/run_local_server.sh > /tmp/bmx_local_smoke.log 2>&1 &
SERVER_PID=$!

cleanup() {
  echo "[Smoke] Stopping API server (pid=$SERVER_PID)..."
  if ps -p "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" || true
  fi
}
trap cleanup EXIT

echo "[Smoke] Waiting for server startup..."
sleep 5

BASE_URL="http://localhost:8000"

check_endpoint() {
  local endpoint="$1"
  local label="$2"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" || echo "000")
  if [[ "$code" == "200" ]]; then
    echo "[Smoke] PASS $label ($endpoint) -> HTTP $code"
  else
    echo "[Smoke] FAIL $label ($endpoint) -> HTTP $code" >&2
    return 1
  fi
}

echo "[Smoke] Checking /healthz..."
check_endpoint "/api/v1/healthz" "healthz"

echo "[Smoke] Checking /dashboard/metrics..."
check_endpoint "/api/v1/dashboard/metrics" "dashboard metrics"

echo "[Smoke] Smoke test complete. See /tmp/bmx_local_smoke.log for server output."

echo "[Smoke] Local API smoke test finished successfully."

