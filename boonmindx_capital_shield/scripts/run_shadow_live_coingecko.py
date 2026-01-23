#!/usr/bin/env python3
"""
Shadow-Live Runner for Capital Shield + BearHunter (CoinGecko)

Polls CoinGecko for live cryptocurrency prices, feeds them into the Capital Shield
risk evaluation pipeline, and logs decisions without executing any trades.

This is a "shadow mode" validation tool:
- Pulls real market data
- Runs real risk logic
- Logs what trades would be blocked/allowed
- Does NOT place any actual trades

Default preset: BALANCED (survival-first, but allows normal-regime trading)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.coin_gecko_client import CoinGeckoClient, get_default_watchlist
from live_sim.rsa import calculate_rsa


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Shadow-live runner for Capital Shield (CoinGecko data source)"
    )
    parser.add_argument(
        "--watchlist",
        nargs="+",
        default=None,
        help="List of CoinGecko coin IDs (default: bitcoin, ethereum, cardano, solana, polkadot)"
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=300,
        help="Seconds between polls (default 300 = 5 minutes)"
    )
    parser.add_argument(
        "--history-days",
        type=int,
        default=7,
        help="Days of historical data to fetch per poll (default 7)"
    )
    parser.add_argument(
        "--preset",
        type=str,
        default="BALANCED",
        choices=["CONSERVATIVE", "BALANCED", "AGGRESSIVE"],
        help="Capital Shield preset (default BALANCED)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/shadow_live"),
        help="Output directory for logs"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Max polling iterations (0 = run indefinitely)"
    )
    return parser.parse_args()


def evaluate_risk_simple(
    ohlcv: Dict[str, Any],
    preset: str
) -> Dict[str, Any]:
    """
    Simple risk evaluation using Capital Shield logic.
    
    Args:
        ohlcv: OHLCV data dictionary
        preset: Risk preset (CONSERVATIVE, BALANCED, AGGRESSIVE)
    
    Returns:
        Dictionary with:
            - decision: "ALLOW" or "BLOCK"
            - reason_code: Machine-readable code
            - reason_message: Human-readable explanation
            - risk_score: Float 0.0-1.0
            - rsa: Relative Survival Alpha (if applicable)
    """
    prices = ohlcv.get("prices", [])
    
    if len(prices) < 2:
        return {
            "decision": "BLOCK",
            "reason_code": "INSUFFICIENT_DATA",
            "reason_message": "Insufficient price history for risk evaluation",
            "risk_score": 1.0,
        }
    
    # Calculate simple volatility (std dev of returns)
    returns = [(prices[i+1] - prices[i]) / prices[i] for i in range(len(prices) - 1)]
    volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5
    
    # Calculate drawdown from recent peak
    recent_peak = max(prices[-min(len(prices), 20):])
    current_price = prices[-1]
    drawdown = (current_price - recent_peak) / recent_peak if recent_peak > 0 else 0.0
    
    # Preset-based thresholds
    thresholds = {
        "CONSERVATIVE": {"vol": 0.03, "dd": -0.10},
        "BALANCED": {"vol": 0.05, "dd": -0.20},
        "AGGRESSIVE": {"vol": 0.10, "dd": -0.35},
    }
    
    thresh = thresholds.get(preset, thresholds["BALANCED"])
    
    # Decision logic
    if volatility > thresh["vol"]:
        return {
            "decision": "BLOCK",
            "reason_code": "VOL_BREACH",
            "reason_message": f"Volatility {volatility:.3f} exceeds {preset} threshold {thresh['vol']:.3f}",
            "risk_score": min(1.0, volatility / thresh["vol"]),
            "volatility": volatility,
            "drawdown": drawdown,
        }
    
    if drawdown < thresh["dd"]:
        return {
            "decision": "BLOCK",
            "reason_code": "DD_BREACH",
            "reason_message": f"Drawdown {drawdown:.2%} exceeds {preset} threshold {thresh['dd']:.2%}",
            "risk_score": min(1.0, abs(drawdown) / abs(thresh["dd"])),
            "volatility": volatility,
            "drawdown": drawdown,
        }
    
    # Calculate RSA if we have enough data
    rsa = None
    if len(prices) >= 7:
        try:
            initial = prices[0]
            terminal = prices[-1]
            max_dd = min(0.0, drawdown)
            rsa = calculate_rsa(terminal, initial, abs(max_dd))
        except Exception:
            pass
    
    return {
        "decision": "ALLOW",
        "reason_code": "NORMAL_REGIME",
        "reason_message": f"Normal regime: vol={volatility:.3f}, dd={drawdown:.2%}",
        "risk_score": max(volatility / thresh["vol"], abs(drawdown) / abs(thresh["dd"])),
        "volatility": volatility,
        "drawdown": drawdown,
        "rsa": rsa,
    }


def run_shadow_live(args: argparse.Namespace) -> None:
    """
    Main shadow-live loop.
    
    Args:
        args: Parsed command-line arguments
    """
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    watchlist = args.watchlist or get_default_watchlist()
    client = CoinGeckoClient()
    
    print(f"[ShadowLive] Starting Capital Shield shadow-live mode")
    print(f"[ShadowLive] Preset: {args.preset}")
    print(f"[ShadowLive] Watchlist: {', '.join(watchlist)}")
    print(f"[ShadowLive] Poll interval: {args.poll_interval}s")
    print(f"[ShadowLive] Output: {args.output_dir}")
    print()
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            print(f"[ShadowLive] Iteration {iteration} @ {timestamp}")
            
            # Fetch OHLCV data
            ohlcv_data = client.get_watchlist_ohlcv(
                watchlist,
                days=args.history_days
            )
            
            # Evaluate risk for each asset
            results = []
            for ohlcv in ohlcv_data:
                asset = ohlcv["asset"]
                evaluation = evaluate_risk_simple(ohlcv, args.preset)
                
                result = {
                    "timestamp": timestamp,
                    "asset": asset,
                    "current_price": ohlcv["prices"][-1] if ohlcv["prices"] else None,
                    "evaluation": evaluation,
                }
                results.append(result)
                
                # Log to console
                decision = evaluation["decision"]
                reason = evaluation["reason_message"]
                rsa = evaluation.get("rsa")
                rsa_str = f", RSA={rsa:.3f}" if rsa is not None else ""
                print(f"  {asset:12s} | {decision:5s} | {reason}{rsa_str}")
            
            # Save iteration results
            output_file = args.output_dir / f"shadow_live_{iteration:04d}.json"
            output_file.write_text(json.dumps({
                "iteration": iteration,
                "timestamp": timestamp,
                "preset": args.preset,
                "results": results,
            }, indent=2))
            
            print()
            
            # Check exit condition
            if args.max_iterations > 0 and iteration >= args.max_iterations:
                print(f"[ShadowLive] Reached max iterations ({args.max_iterations}), exiting")
                break
            
            # Sleep until next poll
            if args.max_iterations == 0 or iteration < args.max_iterations:
                print(f"[ShadowLive] Sleeping {args.poll_interval}s until next poll...")
                print()
                time.sleep(args.poll_interval)
    
    except KeyboardInterrupt:
        print()
        print("[ShadowLive] Interrupted by user, exiting gracefully")
    
    print(f"[ShadowLive] Completed {iteration} iterations")
    print(f"[ShadowLive] Results saved to {args.output_dir}")


if __name__ == "__main__":
    args = parse_args()
    run_shadow_live(args)

