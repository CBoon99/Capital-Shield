"""
Monte Carlo Round 2 Driver — BoonMindX Capital Shield

Loads a custom dataset (JSON or CSV) and runs a 30m / 5% leverage /
6‑month style validation across all assets using existing Monte Carlo
utilities. Outputs per-asset JSON results plus aggregate summaries.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, List, Sequence

from quant import run_monte_carlo_validation as base_mc
from live_sim.rsa import calculate_rsa


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monte Carlo Round 2 driver (30m, 5% leverage, 6-month horizon)."
    )
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=Path("MontyCarloTest15Nov.txt"),
        help="Path to dataset file (JSON or CSV).",
    )
    parser.add_argument(
        "--starting-capital",
        type=float,
        default=10_000.0,
        help="Starting capital for each run (default 10,000).",
    )
    parser.add_argument(
        "--leverage",
        type=float,
        default=0.05,
        help="Leverage / risk per position (default 0.05).",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default="30m",
        help="Timeframe label for logs (default '30m').",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/monte_carlo_round2"),
        help="Output directory for results.",
    )
    return parser.parse_args()


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    try:
        raw = json.loads(path.read_text())
        if isinstance(raw, dict) and "assets" in raw:
            raw = raw["assets"]
        if isinstance(raw, list):
            return [
                {
                    "asset": entry.get("asset", f"ASSET_{idx:03d}"),
                    "price_history": entry.get("price_history", []),
                    "volume_history": entry.get("volume_history", []),
                }
                for idx, entry in enumerate(raw)
            ]
    except json.JSONDecodeError:
        pass

    # CSV fallback (asset, price_history, volume_history)
    assets: List[Dict[str, Any]] = []
    with path.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            assets.append(
                {
                    "asset": row.get("asset", f"ASSET_{idx:03d}"),
                    "price_history": json.loads(row.get("price_history", "[]")),
                    "volume_history": json.loads(row.get("volume_history", "[]")),
                }
            )
    return assets


def compute_metrics(
    prices: Sequence[float], starting_capital: float, leverage: float
) -> Dict[str, float]:
    if len(prices) < 2:
        return {
            "final_equity": starting_capital,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "num_trades": 0,
        }

    returns = [(prices[i + 1] - prices[i]) / prices[i] for i in range(len(prices) - 1)]
    cumulative_return = (prices[-1] - prices[0]) / prices[0]
    final_equity = starting_capital * (1 + leverage * cumulative_return)

    peak = prices[0]
    max_dd = 0.0
    for p in prices:
        peak = max(peak, p)
        drawdown = (p - peak) / peak
        max_dd = min(max_dd, drawdown)

    wins = sum(1 for r in returns if r > 0)
    
    # Calculate RSA
    rsa_score = calculate_rsa(
        terminal_equity=final_equity,
        initial_equity=starting_capital,
        max_drawdown_fraction=abs(max_dd)
    )
    
    return {
        "final_equity": final_equity,
        "max_drawdown": max_dd,
        "win_rate": wins / len(returns),
        "num_trades": len(returns),
        "rsa": rsa_score,
    }


def main() -> None:
    args = parse_args()
    base_mc.ensure_output_dir(args.output_dir)
    dataset = load_dataset(args.dataset_path)

    per_asset_results: List[Dict[str, Any]] = []

    for entry in dataset:
        asset = entry["asset"]
        scenario = {
            "id": asset,
            "seed": 0,
            "market_regime": "ROUND2_PLACEHOLDER",
            "notes": f"Round 2 scenario for {asset}",
            "timeframe": args.timeframe,
        }
        base_result = base_mc.run_live_sim_placeholder(scenario)
        metrics = compute_metrics(entry.get("price_history", []), args.starting_capital, args.leverage)
        base_result.update(
            {
                "status": base_result.get("status", "COMPLETE"),
                "metrics": metrics,
                "starting_capital": args.starting_capital,
                "leverage": args.leverage,
            }
        )
        per_asset_results.append(base_result)
        outfile = args.output_dir / f"ROUND2_{asset}.json"
        outfile.write_text(json.dumps(base_result, indent=2))

    aggregate = {
        "total_assets": len(per_asset_results),
        "starting_capital": args.starting_capital,
        "leverage": args.leverage,
        "timeframe": args.timeframe,
    }

    equities = [res["metrics"]["final_equity"] for res in per_asset_results]
    drawdowns = [res["metrics"]["max_drawdown"] for res in per_asset_results]

    if equities:
        aggregate.update(
            {
                "final_equity_min": min(equities),
                "final_equity_max": max(equities),
                "final_equity_mean": statistics.mean(equities),
                "final_equity_median": statistics.median(equities),
            }
        )
    if drawdowns:
        aggregate["max_drawdown_min"] = min(drawdowns)
        aggregate["max_drawdown_max"] = max(drawdowns)
    
    # Add RSA stats
    rsa_scores = [res["metrics"].get("rsa", 0.0) for res in per_asset_results]
    if rsa_scores:
        aggregate.update({
            "rsa_min": min(rsa_scores),
            "rsa_max": max(rsa_scores),
            "rsa_mean": statistics.mean(rsa_scores),
            "rsa_median": statistics.median(rsa_scores),
        })

    (args.output_dir / "ROUND2_AGGREGATE.json").write_text(json.dumps(aggregate, indent=2))

    top = sorted(per_asset_results, key=lambda x: x["metrics"]["final_equity"], reverse=True)
    bottom = list(reversed(top))

    summary_lines = [
        "# Monte Carlo Round 2 Summary",
        "",
        f"- Total assets: {aggregate['total_assets']}",
        f"- Starting capital: {args.starting_capital}",
        f"- Leverage: {args.leverage}",
        f"- Timeframe: {args.timeframe}",
        "",
        "## Final Equity Distribution",
        f"- Min: {aggregate.get('final_equity_min')}",
        f"- Max: {aggregate.get('final_equity_max')}",
        f"- Mean: {aggregate.get('final_equity_mean')}",
        f"- Median: {aggregate.get('final_equity_median')}",
        "",
        "## RSA (Relative Survival Alpha) Distribution",
        f"- Min: {aggregate.get('rsa_min', 0.0):.3f}",
        f"- Max: {aggregate.get('rsa_max', 0.0):.3f}",
        f"- Mean: {aggregate.get('rsa_mean', 0.0):.3f}",
        f"- Median: {aggregate.get('rsa_median', 0.0):.3f}",
        "",
        "## Top 10 Assets (by Final Equity)",
    ]
    for res in top[:10]:
        summary_lines.append(f"- {res['scenario']['id']}: {res['metrics']['final_equity']:.2f}")
    summary_lines.append("")
    summary_lines.append("## Bottom 10 Assets")
    for res in bottom[:10]:
        summary_lines.append(f"- {res['scenario']['id']}: {res['metrics']['final_equity']:.2f}")

    summary_path = args.output_dir / "ROUND2_SUMMARY.md"
    summary_path.write_text("\n".join(summary_lines))

    print(f"[Round2] Processed {len(per_asset_results)} assets; results in {args.output_dir}/")


if __name__ == "__main__":
    main()

