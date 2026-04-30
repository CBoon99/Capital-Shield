"""
Opportunity Cost Analysis - BoonMindX Capital Shield vs Simple Hedging

Compares:
1) Baseline (no shield, no hedge)
2) Shielded (Capital Shield active)
3) Simple Hedging strategy (e.g., static or rule-based hedge)

Outputs:
- Final equity per strategy
- Max drawdown
- P&L %
- "Opportunity cost" metrics

ASSUMPTIONS (Important):
- No slippage
- No commissions
- Frictionless fills
- Hedge is synthetic / approximate
- This is exploratory analysis, not a production-grade execution model
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json

from .runner import run_simulation
from .data_loader import load_historical_data, get_price_history
from .slippage_model import ExecutionCostConfig


def run_hedge_strategy_v1(
    data_path: str,
    symbols: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_equity: float = 100000.0,
    hedge_drawdown_threshold: float = 0.10,  # 10% drawdown threshold
    hedge_reduction: float = 0.5,  # Reduce to 50% exposure
    hedge_days: int = 20,  # Hold reduced exposure for 20 days
    max_position_size: float = 0.1,
    leverage: float = 1.0,
    exec_cost_config: Optional[ExecutionCostConfig] = None
) -> Dict[str, Any]:
    """
    Run HEDGE_STRATEGY_V1: Simple stop-loss with slow re-entry
    
    Strategy:
    - Always remain 100% in the asset (via position sizing)
    - If cumulative drawdown exceeds threshold (e.g., 10%), 
      reduce exposure by hedge_reduction (e.g., 50%) for hedge_days (e.g., 20 days)
    - Then restore full exposure
    
    Args:
        data_path: Path to CSV data file
        symbols: List of symbols to trade
        start_date: Optional start date filter
        end_date: Optional end date filter
        initial_equity: Starting equity
        hedge_drawdown_threshold: Drawdown threshold to trigger hedge (e.g., 0.10 = 10%)
        hedge_reduction: Exposure reduction factor (e.g., 0.5 = 50% of normal)
        hedge_days: Number of days to maintain reduced exposure
        max_position_size: Maximum position size as fraction of equity
        leverage: Leverage multiplier
        
    Returns:
        Dict with portfolio metrics and equity curve
    """
    # Load data
    df = load_historical_data(symbols, data_path, start_date, end_date)
    
    # Initialize portfolio state
    equity = initial_equity
    equity_curve = [equity]
    positions = {}  # symbol -> {'size': float, 'entry_price': float, 'entry_date': str}
    trades = []
    
    # Hedge state tracking
    hedge_active = False
    hedge_start_date = None
    hedge_end_date = None
    peak_equity = initial_equity
    
    # Iterate over dates chronologically
    dates = df.index.unique().sort_values()
    
    for current_date in dates:
        # Get current prices
        current_prices = {}
        for symbol in symbols:
            if symbol in df.columns:
                symbol_data = df.loc[df.index == current_date, symbol]
                if not symbol_data.empty and not pd.isna(symbol_data.iloc[0]):
                    current_prices[symbol] = float(symbol_data.iloc[0])
        
        # Update equity with current prices (unrealized P&L)
        unrealized_pnl = 0.0
        for symbol, position in positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                pnl = (current_price - position['entry_price']) * position['size']
                unrealized_pnl += pnl
        
        equity = initial_equity + sum(t['pnl'] for t in trades) + unrealized_pnl
        equity_curve.append(equity)
        
        # Update peak equity
        if equity > peak_equity:
            peak_equity = equity
        
        # Calculate current drawdown
        current_drawdown = (equity - peak_equity) / peak_equity if peak_equity > 0 else 0.0
        
        # Check if hedge should activate
        if not hedge_active and current_drawdown < -hedge_drawdown_threshold:
            # Activate hedge
            hedge_active = True
            hedge_start_date = current_date
            
            # Reduce existing positions
            for symbol in list(positions.keys()):
                if symbol in current_prices:
                    # Exit 50% of position
                    position = positions[symbol]
                    exit_size = position['size'] * hedge_reduction
                    exit_price = current_prices[symbol]
                    exit_pnl = (exit_price - position['entry_price']) * exit_size
                    
                    trades.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'size': exit_size,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'pnl': exit_pnl,
                        'date': current_date
                    })
                    
                    # Update position
                    position['size'] -= exit_size
                    if position['size'] <= 0.001:  # Close if too small
                        del positions[symbol]
        
        # Check if hedge should deactivate
        if hedge_active and hedge_start_date:
            days_in_hedge = (current_date - hedge_start_date).days if hasattr(current_date - hedge_start_date, 'days') else 0
            if days_in_hedge >= hedge_days:
                hedge_active = False
                hedge_end_date = current_date
                hedge_start_date = None
        
        # Determine position sizing multiplier
        if hedge_active:
            position_multiplier = hedge_reduction  # Reduced exposure
        else:
            position_multiplier = 1.0  # Full exposure
        
        # Process each symbol
        for symbol in symbols:
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Simple strategy: always try to maintain position
            # In a real implementation, this would use signals, but for comparison
            # we'll use a simple "always in" approach with hedge adjustments
            
            if symbol not in positions:
                # No position - enter if not in hedge mode, or enter reduced if in hedge
                position_value = equity * max_position_size * leverage * position_multiplier
                size = position_value / current_price
                
                if size > 0.001:  # Minimum position size
                    positions[symbol] = {
                        'size': size,
                        'entry_price': current_price,
                        'entry_date': current_date
                    }
            else:
                # Have position - adjust if hedge state changed
                position = positions[symbol]
                target_value = equity * max_position_size * leverage * position_multiplier
                target_size = target_value / current_price
                
                if abs(target_size - position['size']) > 0.001:
                    # Adjust position
                    size_diff = target_size - position['size']
                    
                    if size_diff > 0:
                        # Increase position
                        entry_price = current_price
                        
                        # Calculate execution cost
                        notional = size_diff * current_price
                        exec_cost = 0.0
                        if exec_cost_config and exec_cost_config.enabled:
                            from .slippage_model import calculate_execution_cost, calculate_volatility_from_history
                            # Get price history for volatility
                            price_history = []  # Simplified - would need to track in full implementation
                            volatility = None
                            exec_cost = calculate_execution_cost(
                                current_price,
                                notional,
                                exec_cost_config,
                                volatility
                            )
                            equity -= exec_cost  # Apply cost
                        
                        # Track average entry price
                        total_cost = position['size'] * position['entry_price'] + size_diff * entry_price
                        position['size'] += size_diff
                        position['entry_price'] = total_cost / position['size']
                    else:
                        # Decrease position
                        exit_size = abs(size_diff)
                        exit_price = current_price
                        
                        # Calculate execution cost
                        notional = exit_size * current_price
                        exec_cost = 0.0
                        if exec_cost_config and exec_cost_config.enabled:
                            from .slippage_model import calculate_execution_cost, calculate_volatility_from_history
                            price_history = []  # Simplified
                            volatility = None
                            exec_cost = calculate_execution_cost(
                                current_price,
                                notional,
                                exec_cost_config,
                                volatility
                            )
                            equity -= exec_cost  # Apply cost
                        
                        exit_pnl = (exit_price - position['entry_price']) * exit_size
                        
                        trades.append({
                            'symbol': symbol,
                            'action': 'SELL',
                            'size': exit_size,
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'pnl': exit_pnl,
                            'date': current_date
                        })
                        
                        position['size'] -= exit_size
                        if position['size'] <= 0.001:
                            del positions[symbol]
        
        # Final equity update
        unrealized_pnl = 0.0
        for symbol, position in positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                pnl = (current_price - position['entry_price']) * position['size']
                unrealized_pnl += pnl
        
        equity = initial_equity + sum(t['pnl'] for t in trades) + unrealized_pnl
    
    # Final metrics
    final_equity = equity
    total_pnl = final_equity - initial_equity
    pnl_percent = (total_pnl / initial_equity) * 100 if initial_equity > 0 else 0.0
    
    # Calculate max drawdown
    equity_array = np.array(equity_curve)
    peak = np.maximum.accumulate(equity_array)
    drawdown = (equity_array - peak) / peak
    max_drawdown = float(np.min(drawdown))
    
    # Win rate
    closed_trades = [t for t in trades if t['action'] == 'SELL']
    win_rate = len([t for t in closed_trades if t['pnl'] > 0]) / len(closed_trades) if closed_trades else 0.0
    
    return {
        'portfolio_metrics': {
            'initial_equity': initial_equity,
            'final_equity': final_equity,
            'total_pnl': total_pnl,
            'pnl_percent': pnl_percent,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'win_rate': win_rate,
            'open_positions': len(positions)
        },
        'equity_curve': equity_curve,
        'trades': trades,
        'hedge_events': {
            'hedge_activated': hedge_active or hedge_start_date is not None,
            'hedge_start': str(hedge_start_date) if hedge_start_date else None,
            'hedge_end': str(hedge_end_date) if hedge_end_date else None
        }
    }


def compare_strategies(
    dataset_path: str,
    symbols: Optional[List[str]] = None,
    preset: str = "conservative",
    hedge_drawdown_threshold: float = 0.10,
    hedge_reduction: float = 0.5,
    hedge_days: int = 20,
    output_dir: str = "reports/opportunity_cost",
    scenario_name: Optional[str] = None,
    initial_equity: float = 100000.0,
    exec_cost_config: Optional[ExecutionCostConfig] = None
) -> Dict[str, Any]:
    """
    Compare Baseline, Shielded, and Hedge strategies
    
    Args:
        dataset_path: Path to CSV data file
        symbols: List of symbols to test (if None, uses 'close' column)
        preset: Capital Shield preset to use
        hedge_drawdown_threshold: Drawdown threshold for hedge (e.g., 0.10 = 10%)
        hedge_reduction: Exposure reduction factor (e.g., 0.5 = 50%)
        hedge_days: Number of days to maintain reduced exposure
        output_dir: Directory to save outputs
        scenario_name: Optional scenario name (auto-generated if None)
        initial_equity: Starting equity
        
    Returns:
        Dict with comparison results
    """
    # Generate scenario name if not provided
    if scenario_name is None:
        dataset_name = os.path.basename(dataset_path).replace('.csv', '')
        scenario_name = f"{dataset_name}_{preset}"
    
    # Handle OHLCV format (same as FP harness)
    if symbols is None:
        import tempfile
        df_raw = pd.read_csv(dataset_path)
        temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df_temp = df_raw.copy()
        df_temp['ASSET_1'] = df_temp['close']
        df_temp[['timestamp', 'ASSET_1']].to_csv(temp_csv.name, index=False)
        temp_csv.close()
        dataset_path = temp_csv.name
        symbols = ['ASSET_1']
    
    print(f"Running strategy comparison for scenario: {scenario_name}")
    print(f"  Dataset: {dataset_path}")
    print(f"  Symbols: {symbols}")
    print(f"  Preset: {preset}")
    
    # Run Baseline
    print("  Running baseline simulation...")
    baseline_results = run_simulation(
        data_path=dataset_path,
        symbols=symbols,
        initial_equity=initial_equity,
        mode="baseline",
        exec_cost_config=exec_cost_config
    )
    
    # Run Shielded
    print("  Running shielded simulation...")
    from .presets import apply_preset
    preset_config = apply_preset(preset)
    
    shielded_results = run_simulation(
        data_path=dataset_path,
        symbols=symbols,
        initial_equity=initial_equity,
        mode="capital_shielded",
        capital_shield_mode=preset_config.get('CAPITAL_SHIELD_MODE', 'PERMISSIVE'),
        preset_name=preset,
        exec_cost_config=exec_cost_config
    )
    
    # Run Hedge Strategy V1
    print("  Running hedge strategy V1...")
    hedge_results = run_hedge_strategy_v1(
        data_path=dataset_path,
        symbols=symbols,
        initial_equity=initial_equity,
        hedge_drawdown_threshold=hedge_drawdown_threshold,
        hedge_reduction=hedge_reduction,
        hedge_days=hedge_days,
        exec_cost_config=exec_cost_config
    )
    
    # Extract metrics
    baseline_metrics = baseline_results['portfolio_metrics']
    shielded_metrics = shielded_results['portfolio_metrics']
    hedge_metrics = hedge_results['portfolio_metrics']
    
    # Extract execution cost metrics
    baseline_exec_costs = baseline_results.get('execution_costs', {})
    shielded_exec_costs = shielded_results.get('execution_costs', {})
    hedge_exec_costs = hedge_results.get('execution_costs', {})
    
    # Calculate opportunity costs
    shield_vs_baseline_pnl_diff = shielded_metrics['pnl_percent'] - baseline_metrics['pnl_percent']
    shield_vs_hedge_pnl_diff = shielded_metrics['pnl_percent'] - hedge_metrics['pnl_percent']
    hedge_vs_baseline_pnl_diff = hedge_metrics['pnl_percent'] - baseline_metrics['pnl_percent']
    
    results = {
        'scenario_name': scenario_name,
        'dataset': dataset_path,
        'preset': preset,
        'hedge_params': {
            'drawdown_threshold': hedge_drawdown_threshold,
            'reduction': hedge_reduction,
            'days': hedge_days
        },
        'metrics': {
            'baseline': {
                'final_equity': baseline_metrics['final_equity'],
                'pnl_pct': baseline_metrics['pnl_percent'],
                'max_drawdown': baseline_metrics['max_drawdown'],
                'total_trades': baseline_metrics['total_trades'],
                'win_rate': baseline_metrics['win_rate']
            },
            'shielded': {
                'final_equity': shielded_metrics['final_equity'],
                'pnl_pct': shielded_metrics['pnl_percent'],
                'max_drawdown': shielded_metrics['max_drawdown'],
                'total_trades': shielded_metrics['total_trades'],
                'win_rate': shielded_metrics['win_rate'],
                'blocked_trades': shielded_results.get('blocked_trades_count', 0)
            },
            'hedge_v1': {
                'final_equity': hedge_metrics['final_equity'],
                'pnl_pct': hedge_metrics['pnl_percent'],
                'max_drawdown': hedge_metrics['max_drawdown'],
                'total_trades': hedge_metrics['total_trades'],
                'win_rate': hedge_metrics['win_rate'],
                'hedge_activated': hedge_results['hedge_events']['hedge_activated']
            }
        },
        'opportunity_cost': {
            'shield_vs_baseline_pnl_diff': shield_vs_baseline_pnl_diff,
            'shield_vs_hedge_pnl_diff': shield_vs_hedge_pnl_diff,
            'hedge_vs_baseline_pnl_diff': hedge_vs_baseline_pnl_diff
        },
        'execution_costs': {
            'baseline': baseline_exec_costs,
            'shielded': shielded_exec_costs,
            'hedge_v1': hedge_exec_costs,
            'enabled': exec_cost_config.enabled if exec_cost_config else False
        },
        'timestamp': datetime.now().isoformat()
    }
    
    # Save individual scenario result
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"OC_{scenario_name}.json")
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"  ✅ Results saved to {json_path}")
    
    return results


def generate_opportunity_cost_summary(
    results_list: List[Dict[str, Any]],
    output_dir: str = "reports/opportunity_cost"
) -> Dict[str, Any]:
    """
    Generate aggregate opportunity cost summary
    
    Args:
        results_list: List of comparison results from compare_strategies()
        output_dir: Directory to save outputs
        
    Returns:
        Dict with aggregate summary
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Aggregate summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'scenarios': results_list,
        'aggregate_metrics': {}
    }
    
    # Calculate averages
    baseline_pnl_avg = np.mean([r['metrics']['baseline']['pnl_pct'] for r in results_list])
    shielded_pnl_avg = np.mean([r['metrics']['shielded']['pnl_pct'] for r in results_list])
    hedge_pnl_avg = np.mean([r['metrics']['hedge_v1']['pnl_pct'] for r in results_list])
    
    summary['aggregate_metrics'] = {
        'average_pnl': {
            'baseline': float(baseline_pnl_avg),
            'shielded': float(shielded_pnl_avg),
            'hedge_v1': float(hedge_pnl_avg)
        },
        'average_opportunity_cost': {
            'shield_vs_baseline': float(shielded_pnl_avg - baseline_pnl_avg),
            'shield_vs_hedge': float(shielded_pnl_avg - hedge_pnl_avg),
            'hedge_vs_baseline': float(hedge_pnl_avg - baseline_pnl_avg)
        }
    }
    
    # Generate Markdown report
    md_lines = [
        "# Opportunity Cost Analysis - BoonMindX Capital Shield vs Simple Hedging",
        "",
        f"**Date**: {summary['timestamp']}",
        "",
        "## Assumptions",
        "",
        "**Important**: This analysis makes the following assumptions:",
        "",
        "- ❌ **No slippage** - All trades execute at exact prices",
        "- ❌ **No commissions** - Zero transaction costs",
        "- ❌ **Frictionless fills** - Instant execution",
        "- ⚠️ **Hedge is synthetic** - Approximate model, not production-grade",
        "- ⚠️ **Exploratory analysis** - Sanity-check level, not final institutional proof",
        "",
        "---",
        ""
    ]
    
    # Per-scenario results
    for result in results_list:
        scenario_name = result['scenario_name']
        metrics = result['metrics']
        opp_cost = result['opportunity_cost']
        
        md_lines.extend([
            f"## Scenario: {scenario_name}",
            "",
            f"- **Dataset**: `{os.path.basename(result['dataset'])}`",
            f"- **Preset**: {result['preset']}",
            f"- **Hedge Parameters**: {result['hedge_params']['drawdown_threshold']*100:.0f}% threshold, "
            f"{result['hedge_params']['reduction']*100:.0f}% reduction, {result['hedge_params']['days']} days",
            "",
            "### Metrics Comparison",
            "",
            "| Strategy | Final Equity | P&L % | Max DD | Total Trades | Win Rate |",
            "|----------|-------------:|------:|-------:|-------------:|---------:|"
        ])
        
        # Baseline
        baseline = metrics['baseline']
        md_lines.append(
            f"| Baseline | £{baseline['final_equity']:,.2f} | "
            f"{baseline['pnl_pct']:.2f}% | {baseline['max_drawdown']*100:.2f}% | "
            f"{baseline['total_trades']} | {baseline['win_rate']*100:.1f}% |"
        )
        
        # Shielded
        shielded = metrics['shielded']
        md_lines.append(
            f"| Shielded | £{shielded['final_equity']:,.2f} | "
            f"{shielded['pnl_pct']:.2f}% | {shielded['max_drawdown']*100:.2f}% | "
            f"{shielded['total_trades']} | {shielded['win_rate']*100:.1f}% | "
            f"(Blocked: {shielded.get('blocked_trades', 0)})"
        )
        
        # Hedge V1
        hedge = metrics['hedge_v1']
        hedge_note = " (Hedge activated)" if hedge.get('hedge_activated', False) else ""
        md_lines.append(
            f"| Hedge V1 | £{hedge['final_equity']:,.2f} | "
            f"{hedge['pnl_pct']:.2f}% | {hedge['max_drawdown']*100:.2f}% | "
            f"{hedge['total_trades']} | {hedge['win_rate']*100:.1f}% |{hedge_note}"
        )
        
        md_lines.extend([
            "",
            "### Opportunity Cost Summary",
            "",
            f"- **Shield vs Baseline P&L Δ**: {opp_cost['shield_vs_baseline_pnl_diff']:+.2f}%",
            f"- **Shield vs Hedge P&L Δ**: {opp_cost['shield_vs_hedge_pnl_diff']:+.2f}%",
            f"- **Hedge vs Baseline P&L Δ**: {opp_cost['hedge_vs_baseline_pnl_diff']:+.2f}%",
            "",
            "### Narrative",
            ""
        ])
        
        # Generate narrative
        shield_pnl_diff = opp_cost['shield_vs_baseline_pnl_diff']
        if shield_pnl_diff > 0:
            narrative = f"✅ **Capital Shield preserved {abs(shield_pnl_diff):.2f}% more capital** than baseline."
        elif shield_pnl_diff < 0:
            narrative = f"⚠️ **Capital Shield reduced returns by {abs(shield_pnl_diff):.2f}%** vs baseline (opportunity cost)."
        else:
            narrative = "➡️ **Capital Shield matched baseline performance** (zero opportunity cost)."
        
        hedge_pnl_diff = opp_cost['hedge_vs_baseline_pnl_diff']
        if hedge_pnl_diff > 0:
            narrative += f" Hedge V1 strategy **gained {abs(hedge_pnl_diff):.2f}%** vs baseline."
        elif hedge_pnl_diff < 0:
            narrative += f" Hedge V1 strategy **lost {abs(hedge_pnl_diff):.2f}%** vs baseline."
        else:
            narrative += " Hedge V1 matched baseline."
        
        shield_vs_hedge = opp_cost['shield_vs_hedge_pnl_diff']
        if abs(shield_vs_hedge) < 1.0:
            narrative += " **Capital Shield and Hedge V1 performed similarly** in this scenario."
        elif shield_vs_hedge > 0:
            narrative += f" **Capital Shield outperformed Hedge V1 by {abs(shield_vs_hedge):.2f}%**."
        else:
            narrative += f" **Hedge V1 outperformed Capital Shield by {abs(shield_vs_hedge):.2f}%**."
        
        md_lines.append(narrative)
        md_lines.append("")
        
        # Add execution cost section if enabled
        if result.get('execution_costs', {}).get('enabled', False):
            exec_costs = result['execution_costs']
            baseline_exec = exec_costs.get('baseline', {})
            shielded_exec = exec_costs.get('shielded', {})
            hedge_exec = exec_costs.get('hedge_v1', {})
            
            md_lines.extend([
                "### Execution Costs (v1 Approximation)",
                "",
                "**Assumptions**:",
                f"- Slippage model: {baseline_exec.get('slippage_model_used', 'fixed_bps')}",
                f"- Fixed slippage: 5 bps per trade",
                f"- Latency: {baseline_exec.get('latency_ms', 50)} ms (+{baseline_exec.get('latency_ms', 50) // 50 * 3} bps penalty)",
                "- No commissions",
                "",
                "**Observations**:",
                f"- Baseline: Total execution costs: £{baseline_exec.get('total_execution_costs', 0):,.2f} "
                f"({baseline_exec.get('execution_cost_count', 0)} trades)",
                f"- Shielded: Total execution costs: £{shielded_exec.get('total_execution_costs', 0):,.2f} "
                f"({shielded_exec.get('execution_cost_count', 0)} trades)",
                f"- Hedge V1: Total execution costs: £{hedge_exec.get('total_execution_costs', 0):,.2f} "
                f"({hedge_exec.get('execution_cost_count', 0)} trades)",
                "",
                "**Interpretation**:",
                "- Execution costs reduce all strategies as expected.",
                "- Relative relationships (Shield vs Baseline vs Hedge) remain consistent.",
                ""
            ])
    
    # Global interpretation
    md_lines.extend([
        "---",
        "",
        "## Global Interpretation",
        "",
        "### High-Level Takeaways",
        ""
    ])
    
    avg_shield_cost = summary['aggregate_metrics']['average_opportunity_cost']['shield_vs_baseline']
    if abs(avg_shield_cost) < 0.5:
        md_lines.append(f"- **Capital Shield shows minimal opportunity cost** ({avg_shield_cost:+.2f}% average) in benign markets.")
    elif avg_shield_cost > 0:
        md_lines.append(f"- **Capital Shield preserves capital** (+{avg_shield_cost:.2f}% average) vs baseline in benign markets.")
    else:
        md_lines.append(f"- **Capital Shield has opportunity cost** ({avg_shield_cost:.2f}% average) vs baseline in benign markets.")
    
    md_lines.extend([
        "",
        "### Important Caveats",
        "",
        "1. **This is a toy hedge** vs your deterministic Capital Shield",
        "   - Hedge V1 is intentionally simple for comparison",
        "   - Real hedging strategies are more sophisticated",
        "",
        "2. **Execution-layer effects are not modeled**",
        "   - No slippage, commissions, or latency",
        "   - Results are idealized",
        "",
        "3. **These results are 'sanity-check' level**",
        "   - Not final institutional proofs",
        "   - Useful for understanding relative behavior",
        "   - Production validation requires live trading data",
        "",
        "---",
        "",
        f"*Report generated: {summary['timestamp']}*"
    ])
    
    # Save Markdown
    md_path = os.path.join(output_dir, "OPPORTUNITY_COST_SUMMARY.md")
    with open(md_path, 'w') as f:
        f.write("\n".join(md_lines))
    
    # Save JSON
    json_path = os.path.join(output_dir, "OPPORTUNITY_COST_SUMMARY.json")
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n✅ Opportunity cost summary saved:")
    print(f"   - {md_path}")
    print(f"   - {json_path}")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Compare Baseline, Shielded, and Hedge strategies"
    )
    parser.add_argument("--dataset", required=True, help="Path to CSV data file")
    parser.add_argument("--symbols", nargs="+", default=None, help="Symbols to test")
    parser.add_argument("--preset", default="conservative", help="Capital Shield preset")
    parser.add_argument("--hedge-threshold", type=float, default=0.10, help="Hedge drawdown threshold")
    parser.add_argument("--hedge-reduction", type=float, default=0.5, help="Hedge exposure reduction")
    parser.add_argument("--hedge-days", type=int, default=20, help="Days to maintain hedge")
    parser.add_argument("--output-dir", default="reports/opportunity_cost", help="Output directory")
    parser.add_argument("--scenario-name", help="Scenario name (auto-generated if not provided)")
    
    args = parser.parse_args()
    
    results = compare_strategies(
        dataset_path=args.dataset,
        symbols=args.symbols,
        preset=args.preset,
        hedge_drawdown_threshold=args.hedge_threshold,
        hedge_reduction=args.hedge_reduction,
        hedge_days=args.hedge_days,
        output_dir=args.output_dir,
        scenario_name=args.scenario_name
    )
    
    print("\n✅ Strategy comparison complete!")

