"""
Staging Load Test Script Template (Phase 3 Day 12)

Purpose:
    - Provide a placeholder-only async load generator for staging benchmarks.
    - Replace placeholders with real values when running privately.

Rules:
    - Do NOT commit real domains, API keys, or payloads.
    - Use `<STAGING_DOMAIN>` and `<API_KEY_PLACEHOLDER>` consistently.
"""

import asyncio
import json
import random
from typing import Any, Dict, List

import httpx

BASE_URL = "https://<STAGING_DOMAIN>"
API_KEY_HEADER = {"X-API-Key": "<API_KEY_PLACEHOLDER>"}


def build_signal_payload() -> Dict[str, Any]:
    """Return a placeholder payload; replace with real values privately."""
    return {
        "asset": "<ASSET_SYMBOL>",
        "price_history": [random.uniform(90.0, 110.0) for _ in range(50)],
        "metadata": {
            "strategy_id": "<STRATEGY_ID>",
            "timestamp": "<ISO8601_TIMESTAMP>"
        }
    }


def build_filter_payload() -> Dict[str, Any]:
    return {
        "asset": "<ASSET_SYMBOL>",
        "action": "<BUY_OR_SELL>",
        "price_history": [random.uniform(90.0, 110.0) for _ in range(50)],
        "filters": {
            "max_drawdown": 0.05,
            "min_liquidity": 1_000_000
        }
    }


async def health_check(client: httpx.AsyncClient) -> httpx.Response:
    return await client.get(f"{BASE_URL}/api/v1/healthz")


async def dashboard_check(client: httpx.AsyncClient) -> httpx.Response:
    return await client.get(f"{BASE_URL}/api/v1/dashboard/metrics")


async def signal_test(client: httpx.AsyncClient) -> httpx.Response:
    return await client.post(
        f"{BASE_URL}/api/v1/signal",
        json=build_signal_payload(),
        headers=API_KEY_HEADER
    )


async def filter_test(client: httpx.AsyncClient) -> httpx.Response:
    return await client.post(
        f"{BASE_URL}/api/v1/filter",
        json=build_filter_payload(),
        headers=API_KEY_HEADER
    )


ENDPOINT_FUNCTIONS = {
    "healthz": health_check,
    "dashboard": dashboard_check,
    "signal": signal_test,
    "filter": filter_test,
}


async def worker(name: str, endpoint: str, duration: float) -> Dict[str, Any]:
    """Run a single endpoint test loop for `duration` seconds."""
    fn = ENDPOINT_FUNCTIONS[endpoint]
    stats = {"success": 0, "errors": 0, "responses": []}

    async with httpx.AsyncClient(timeout=10.0) as client:
        stop_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < stop_time:
            try:
                resp = await fn(client)
                stats["responses"].append(resp.status_code)
                if resp.is_success:
                    stats["success"] += 1
                else:
                    stats["errors"] += 1
            except Exception as exc:  # noqa: BLE001
                stats["errors"] += 1
                stats["responses"].append(f"EXC:{type(exc).__name__}")

    return {"worker": name, "endpoint": endpoint, **stats}


async def run_test_plan(concurrency: int, duration: float, endpoints: List[str]) -> List[Dict[str, Any]]:
    tasks = []
    for idx in range(concurrency):
        endpoint = endpoints[idx % len(endpoints)]
        tasks.append(
            asyncio.create_task(
                worker(name=f"worker-{idx}", endpoint=endpoint, duration=duration)
            )
        )
    return await asyncio.gather(*tasks)


def main() -> None:
    """Entry point placeholder — customize arguments privately."""
    concurrency = 10  # Replace with staging plan value
    duration = 30.0   # Seconds
    endpoints = ["healthz", "dashboard", "signal", "filter"]

    results = asyncio.run(run_test_plan(concurrency, duration, endpoints))
    print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()

