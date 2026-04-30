"""
API Load & Latency Benchmarks - BoonMindX Capital Shield (v1)

Purpose:
- Measure basic throughput and latency for key endpoints
- Provide reproducible, scriptable benchmarks
- Generate JSON + Markdown reports for investors

This is NOT a formal SLO/SLA test framework. It is a first-pass benchmark.
"""
import asyncio
import time
import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import argparse
import httpx
from collections import defaultdict


class LoadTestResult:
    """Container for load test results"""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.response_times: List[float] = []
        self.status_codes: Dict[int, int] = defaultdict(int)
        self.errors: List[str] = []
        self.total_requests = 0
        self.successful_requests = 0
        self.error_requests = 0
    
    def add_result(self, response_time_ms: float, status_code: Optional[int] = None, error: Optional[str] = None):
        """Add a single request result"""
        self.total_requests += 1
        self.response_times.append(response_time_ms)
        
        if error:
            self.error_requests += 1
            self.errors.append(error)
        elif status_code:
            self.status_codes[status_code] += 1
            if 200 <= status_code < 300:
                self.successful_requests += 1
            else:
                self.error_requests += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Calculate aggregated metrics"""
        if not self.response_times:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'error_requests': 0,
                'requests_per_second': 0.0,
                'latency_ms': {
                    'p50': 0.0,
                    'p90': 0.0,
                    'p95': 0.0,
                    'p99': 0.0,
                    'max': 0.0,
                    'min': 0.0,
                    'mean': 0.0
                },
                'status_codes': dict(self.status_codes),
                'error_rate': 0.0
            }
        
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        def percentile(data: List[float], p: float) -> float:
            """Calculate percentile"""
            if not data:
                return 0.0
            k = (n - 1) * p
            f = int(k)
            c = k - f
            if f + 1 < n:
                return data[f] + c * (data[f + 1] - data[f])
            return data[f]
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'error_requests': self.error_requests,
            'requests_per_second': self.total_requests / (max(self.response_times) - min(self.response_times)) * 1000 if len(self.response_times) > 1 else 0.0,
            'latency_ms': {
                'p50': percentile(sorted_times, 0.50),
                'p90': percentile(sorted_times, 0.90),
                'p95': percentile(sorted_times, 0.95),
                'p99': percentile(sorted_times, 0.99),
                'max': max(sorted_times),
                'min': min(sorted_times),
                'mean': statistics.mean(sorted_times)
            },
            'status_codes': dict(self.status_codes),
            'error_rate': (self.error_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
        }


async def make_request(
    client: httpx.AsyncClient,
    endpoint: str,
    base_url: str,
    payload: Optional[Dict[str, Any]] = None
) -> tuple[float, Optional[int], Optional[str]]:
    """
    Make a single HTTP request and return timing/metrics
    
    Returns:
        (response_time_ms, status_code, error_message)
    """
    url = f"{base_url}{endpoint}"
    start_time = time.time()
    
    try:
        if payload:
            response = await client.post(url, json=payload, timeout=10.0)
        else:
            response = await client.get(url, timeout=10.0)
        
        response_time_ms = (time.time() - start_time) * 1000
        return response_time_ms, response.status_code, None
    
    except httpx.TimeoutException:
        response_time_ms = (time.time() - start_time) * 1000
        return response_time_ms, None, "Timeout"
    
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        return response_time_ms, None, str(e)


def get_endpoint_payload(endpoint: str) -> Optional[Dict[str, Any]]:
    """Get default payload for endpoint if needed"""
    if endpoint == "/api/v1/signal":
        return {
            "asset": "BTC",
            "price_history": [100.0, 101.0, 102.0, 103.0, 104.0],
            "volume_history": [1000000, 1100000, 1200000, 1300000, 1400000]
        }
    elif endpoint == "/api/v1/filter":
        return {
            "asset": "BTC",
            "action": "BUY",
            "price_history": [100.0, 101.0, 102.0, 103.0, 104.0],
            "volume_history": [1000000, 1100000, 1200000, 1300000, 1400000]
        }
    return None


async def worker(
    client: httpx.AsyncClient,
    endpoint: str,
    base_url: str,
    duration_seconds: float,
    result: LoadTestResult
):
    """Worker coroutine that fires requests for duration_seconds"""
    end_time = time.time() + duration_seconds
    payload = get_endpoint_payload(endpoint)
    
    while time.time() < end_time:
        response_time_ms, status_code, error = await make_request(client, endpoint, base_url, payload)
        result.add_result(response_time_ms, status_code, error)
        
        # Small delay to avoid overwhelming the server
        await asyncio.sleep(0.001)


async def run_load_test(
    base_url: str,
    endpoints: List[str],
    concurrency: int,
    duration_seconds: float,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run load test against multiple endpoints
    
    Args:
        base_url: Base URL of the API (e.g., "http://localhost:8000")
        endpoints: List of endpoint paths (e.g., ["/api/v1/healthz"])
        concurrency: Number of concurrent workers per endpoint
        duration_seconds: How long to run the test
        
    Returns:
        Dict with aggregated results
    """
    # Normalize endpoints to include leading slash
    normalized_endpoints = []
    for ep in endpoints:
        if ep == "healthz":
            normalized_endpoints.append("/api/v1/healthz")
        elif ep == "signal":
            normalized_endpoints.append("/api/v1/signal")
        elif ep == "filter":
            normalized_endpoints.append("/api/v1/filter")
        elif ep == "dashboard":
            normalized_endpoints.append("/api/v1/dashboard/metrics")
        elif ep.startswith("/"):
            normalized_endpoints.append(ep)
        else:
            normalized_endpoints.append(f"/api/v1/{ep}")
    
    results_by_endpoint: Dict[str, LoadTestResult] = {}
    
    # Prepare headers if API key is provided
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    async with httpx.AsyncClient(headers=headers) as client:
        # Run tests for each endpoint
        for endpoint in normalized_endpoints:
            print(f"Testing endpoint: {endpoint} (concurrency={concurrency}, duration={duration_seconds}s)")
            result = LoadTestResult(endpoint)
            results_by_endpoint[endpoint] = result
            
            # Create workers
            workers = [
                worker(client, endpoint, base_url, duration_seconds, result)
                for _ in range(concurrency)
            ]
            
            # Run all workers concurrently
            start_time = time.time()
            await asyncio.gather(*workers)
            elapsed_time = time.time() - start_time
            
            print(f"  Completed: {result.total_requests} requests in {elapsed_time:.2f}s")
            print(f"  Success: {result.successful_requests}, Errors: {result.error_requests}")
    
    # Aggregate metrics
    all_response_times: List[float] = []
    total_requests = 0
    total_successful = 0
    total_errors = 0
    
    for result in results_by_endpoint.values():
        all_response_times.extend(result.response_times)
        total_requests += result.total_requests
        total_successful += result.successful_requests
        total_errors += result.error_requests
    
    # Calculate global percentiles
    sorted_all_times = sorted(all_response_times) if all_response_times else []
    n_all = len(sorted_all_times)
    
    def percentile(data: List[float], p: float) -> float:
        if not data:
            return 0.0
        k = (n_all - 1) * p
        f = int(k)
        c = k - f
        if f + 1 < n_all:
            return data[f] + c * (data[f + 1] - data[f])
        return data[f]
    
    global_latency = {
        'p50': percentile(sorted_all_times, 0.50),
        'p90': percentile(sorted_all_times, 0.90),
        'p95': percentile(sorted_all_times, 0.95),
        'p99': percentile(sorted_all_times, 0.99),
        'max': max(sorted_all_times) if sorted_all_times else 0.0,
        'min': min(sorted_all_times) if sorted_all_times else 0.0,
        'mean': statistics.mean(sorted_all_times) if sorted_all_times else 0.0
    }
    
    # Build results dict
    results = {
        'base_url': base_url,
        'concurrency': concurrency,
        'duration_seconds': duration_seconds,
        'endpoints_tested': normalized_endpoints,
        'total_requests': total_requests,
        'successful_requests': total_successful,
        'error_requests': total_errors,
        'error_rate': (total_errors / total_requests * 100) if total_requests > 0 else 0.0,
        'latency_ms': global_latency,
        'by_endpoint': {
            endpoint: result.get_metrics()
            for endpoint, result in results_by_endpoint.items()
        },
        'timestamp': datetime.now().isoformat(),
        'notes': 'Local single-node benchmark, not a production SLA'
    }
    
    return results


def generate_markdown_report(results: Dict[str, Any], output_path: str):
    """Generate Markdown report from results"""
    lines = [
        "# API Load & Latency Benchmarks - BoonMindX Capital Shield",
        "",
        f"**Date**: {results['timestamp']}",
        "",
        "## Test Configuration",
        "",
        f"- **Base URL**: {results['base_url']}",
        f"- **Concurrency**: {results['concurrency']} workers per endpoint",
        f"- **Duration**: {results['duration_seconds']} seconds",
        f"- **Endpoints Tested**: {', '.join(results['endpoints_tested'])}",
        "",
        "## Global Metrics",
        "",
        f"- **Total Requests**: {results['total_requests']:,}",
        f"- **Successful Requests**: {results['successful_requests']:,}",
        f"- **Error Requests**: {results['error_requests']:,}",
        f"- **Error Rate**: {results['error_rate']:.2f}%",
        "",
        "### Global Latency (All Endpoints Combined)",
        "",
        "| Percentile | Latency (ms) |",
        "|------------|--------------:|",
        f"| p50        | {results['latency_ms']['p50']:.2f} |",
        f"| p90        | {results['latency_ms']['p90']:.2f} |",
        f"| p95        | {results['latency_ms']['p95']:.2f} |",
        f"| p99        | {results['latency_ms']['p99']:.2f} |",
        f"| Max        | {results['latency_ms']['max']:.2f} |",
        f"| Mean       | {results['latency_ms']['mean']:.2f} |",
        "",
        "## Per-Endpoint Results",
        "",
        "| Endpoint | Req/s | p50 (ms) | p95 (ms) | p99 (ms) | Error % |",
        "|----------|------:|---------:|---------:|---------:|--------:|"
    ]
    
    for endpoint, metrics in results['by_endpoint'].items():
        req_per_sec = metrics.get('requests_per_second', 0.0)
        latency = metrics.get('latency_ms', {})
        error_rate = metrics.get('error_rate', 0.0)
        
        lines.append(
            f"| {endpoint} | {req_per_sec:.1f} | "
            f"{latency.get('p50', 0.0):.2f} | "
            f"{latency.get('p95', 0.0):.2f} | "
            f"{latency.get('p99', 0.0):.2f} | "
            f"{error_rate:.2f}% |"
        )
    
    lines.extend([
        "",
        "## Notes",
        "",
        results['notes'],
        "",
        "**Important**: This is a local single-node benchmark, not a production SLA test.",
        "Results will vary based on hardware, network conditions, and system load.",
        "",
        "---",
        "",
        f"*Report generated: {results['timestamp']}*"
    ])
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Run load tests against BoonMindX Capital Shield API"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=25,
        help="Number of concurrent workers per endpoint"
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=30.0,
        help="Duration of the test in seconds"
    )
    parser.add_argument(
        "--endpoints",
        nargs="+",
        default=["healthz", "signal", "filter", "dashboard"],
        help="Endpoints to test (healthz, signal, filter, dashboard)"
    )
    parser.add_argument(
        "--output-dir",
        default="reports/perf",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--api-key",
        help="Optional API key to send as X-API-Key header"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("BoonMindX Capital Shield - API Load Test")
    print("="*60)
    print(f"Base URL: {args.base_url}")
    print(f"Concurrency: {args.concurrency} workers per endpoint")
    print(f"Duration: {args.duration_seconds} seconds")
    print(f"Endpoints: {', '.join(args.endpoints)}")
    print("="*60)
    print()
    
    # Run load test
    results = asyncio.run(run_load_test(
        base_url=args.base_url,
        endpoints=args.endpoints,
        concurrency=args.concurrency,
        duration_seconds=args.duration_seconds,
        api_key=args.api_key
    ))
    
    # Save results
    os.makedirs(args.output_dir, exist_ok=True)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(args.output_dir, f"LOAD_TEST_SUMMARY_{timestamp_str}.json")
    md_path = os.path.join(args.output_dir, f"LOAD_TEST_SUMMARY_{timestamp_str}.md")
    
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    generate_markdown_report(results, md_path)
    
    print()
    print("="*60)
    print("Load Test Complete")
    print("="*60)
    print(f"Total Requests: {results['total_requests']:,}")
    print(f"Successful: {results['successful_requests']:,}")
    print(f"Errors: {results['error_requests']:,}")
    print(f"Error Rate: {results['error_rate']:.2f}%")
    print()
    print(f"Global Latency:")
    print(f"  p50: {results['latency_ms']['p50']:.2f} ms")
    print(f"  p95: {results['latency_ms']['p95']:.2f} ms")
    print(f"  p99: {results['latency_ms']['p99']:.2f} ms")
    print()
    print(f"Reports saved:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")
    print("="*60)


if __name__ == "__main__":
    main()


