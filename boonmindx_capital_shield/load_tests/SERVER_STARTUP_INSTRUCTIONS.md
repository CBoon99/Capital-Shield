# Server Startup Instructions

**Date**: November 14, 2025  
**Status**: ✅ Fixed and verified

---

## Quick Start

### From Repository Root:

**Start the server**:
```bash
./load_tests/run_local_server.sh
```

**Verify it's running** (in another terminal):
```bash
curl http://localhost:8000/api/v1/healthz
```

**Expected response**:
```json
{
  "status": "ok",
  "uptime": <seconds>,
  "version": "1.0.0",
  "timestamp": "<ISO timestamp>"
}
```

---

## What Was Fixed

**Previous Issue**: 
- Script tried to import `boonmindx_capital_shield.app.main:app`
- Module not found error

**Solution**:
- Changed to correct module path: `app.main:app`
- Added `PYTHONPATH` export to ensure module resolution
- Added sanity check before starting server
- Using `python3 -m uvicorn` for more robust module resolution

---

## Script Details

The `run_local_server.sh` script:
1. Changes directory to repo root
2. Sets `PYTHONPATH` to include repo root
3. Verifies app can be imported (sanity check)
4. Starts uvicorn server with `app.main:app` on `0.0.0.0:8000`
5. Enables `--reload` for development

---

## Running Load Tests

Once the server is running:

**Terminal 1**: Start server
```bash
./load_tests/run_local_server.sh
```

**Terminal 2**: Run load test
```bash
python3 -m load_tests.api_load_benchmark \
  --base-url http://localhost:8000 \
  --concurrency 10 \
  --duration-seconds 15 \
  --endpoints healthz signal filter dashboard \
  --output-dir reports/perf
```

**Terminal 2**: Verify results
```bash
cat reports/perf/LOAD_TEST_SUMMARY_*.json | python3 -m json.tool | grep error_rate
```

**Valid benchmark criteria**: `error_rate` should be ≈ 0.0

---

*Last updated: November 14, 2025*

