"""
Reporting for Live Simulation

Generate summaries, metrics, and export equity curves
"""
import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime


# RSA calculation moved to live_sim/rsa.py (v1 locked formula)
# Import the canonical v1 implementation
from .rsa import calculate_rsa as _calculate_rsa_v1


def calculate_rsa(equity_shield: float, equity_baseline: float) -> float:
    """
    Calculate Relative Survival Alpha (RSA) - Legacy wrapper for reporting.
    
    NOTE: This is a legacy interface. The canonical v1 RSA formula (locked 2025-11-16)
    is in live_sim/rsa.py and uses terminal_equity + max_drawdown.
    
    This wrapper maintains backward compatibility for old reporting code that
    expects a simple shield-vs-baseline comparison.
    
    Args:
        equity_shield: Final equity with Capital Shield enabled
        equity_baseline: Final equity with baseline (engine only)
        
    Returns:
        RSA as percentage (float). Returns 0.0 if baseline <= 0 (invalid comparison)
    """
    if equity_baseline <= 0:
        import warnings
        warnings.warn(f"Baseline equity ({equity_baseline}) <= 0. RSA set to 0.0 (invalid comparison).")
        return 0.0
    
    # Simple ratio for backward compatibility
    rsa = (equity_shield / equity_baseline - 1) * 100
    return rsa

# Import preset config function if available
try:
    from .presets import get_preset_config
except ImportError:
    def get_preset_config(name: str) -> Dict[str, Any]:
        """Fallback if presets module not available"""
        return {'name': name.upper(), 'description': ''}


def generate_summary(results: Dict[str, Any]) -> str:
    """
    Generate human-readable summary of simulation results
    
    Args:
        results: Results dict from run_simulation()
        
    Returns:
        Human-readable summary string
    """
    metrics = results['portfolio_metrics']
    config = results['simulation_config']
    
    summary_lines = [
        "=" * 80,
        "BOONMINDX CAPITAL SHIELD LIVE SIMULATION RESULTS",
        "=" * 80,
        "",
        "Configuration:",
        f"  Symbols: {', '.join(config['symbols'])}",
        f"  Start Date: {config.get('start_date', 'N/A')}",
        f"  End Date: {config.get('end_date', 'N/A')}",
        f"  Engine Mode: {config['engine_mode']}",
        f"  Capital Shield Mode: {config.get('capital_shield_mode', config.get('shield_mode', 'N/A'))}",
        "",
        "Portfolio Metrics:",
        f"  Initial Equity: ${metrics['initial_equity']:,.2f}",
        f"  Final Equity: ${metrics['final_equity']:,.2f}",
        f"  Total P&L: ${metrics['total_pnl']:,.2f} ({metrics['pnl_percent']:.2f}%)",
        f"  Max Drawdown: {metrics['max_drawdown']:.2%}",
        f"  Total Trades: {metrics['total_trades']}",
        f"  Win Rate: {metrics['win_rate']:.2%}",
        f"  Open Positions: {metrics['open_positions']}",
        "",
        "Safety Rails:",
        f"  Blocked Trades: {results['blocked_trades_count']}",
    ]
    
    if results['blocked_by_reason']:
        summary_lines.append("  Block Reasons:")
        for reason, count in results['blocked_by_reason'].items():
            summary_lines.append(f"    - {reason}: {count}")
    else:
        summary_lines.append("  No trades blocked")
    
    summary_lines.extend([
        "",
        "=" * 80
    ])
    
    return "\n".join(summary_lines)


def export_equity_curve(
    equity_curve: List[float],
    filename: str,
    dates: Optional[List] = None
):
    """
    Export equity curve to CSV
    
    Args:
        equity_curve: List of equity values over time
        filename: Output CSV filename
        dates: Optional list of dates (if None, uses step numbers)
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['step', 'date', 'equity'])
        
        for i, equity in enumerate(equity_curve):
            date = dates[i] if dates and i < len(dates) else i
            writer.writerow([i, date, equity])


def export_results_json(results: Dict[str, Any], filename: str):
    """
    Export full results to JSON
    
    Args:
        results: Results dict from run_simulation()
        filename: Output JSON filename
    """
    # Convert any non-serializable types
    def default_serializer(obj):
        if hasattr(obj, 'isoformat'):  # datetime
            return obj.isoformat()
        return str(obj)
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=default_serializer)


def compare_runs(
    baseline_results: Dict[str, Any],
    shielded_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare baseline vs shielded simulation results
    
    Args:
        baseline_results: Results from baseline run (engine only)
        shielded_results: Results from shielded run (engine + safety rails)
        
    Returns:
        Dict with comparison metrics and shield_effect summary
    """
    baseline_metrics = baseline_results['portfolio_metrics']
    shielded_metrics = shielded_results['portfolio_metrics']
    
    # Calculate differences
    equity_diff = shielded_metrics['final_equity'] - baseline_metrics['final_equity']
    equity_diff_pct = (equity_diff / baseline_metrics['final_equity'] * 100) if baseline_metrics['final_equity'] > 0 else 0.0
    
    pnl_diff = shielded_metrics['total_pnl'] - baseline_metrics['total_pnl']
    pnl_diff_pct = (pnl_diff / baseline_metrics['total_pnl'] * 100) if baseline_metrics['total_pnl'] != 0 else 0.0
    
    drawdown_diff = shielded_metrics['max_drawdown'] - baseline_metrics['max_drawdown']
    drawdown_improvement_pct = (abs(drawdown_diff) / abs(baseline_metrics['max_drawdown']) * 100) if baseline_metrics['max_drawdown'] < 0 else 0.0
    
    trades_diff = shielded_metrics['total_trades'] - baseline_metrics['total_trades']
    blocked_count = shielded_results.get('blocked_trades_count', 0)
    
    # Calculate RSA (Relative Survival Alpha)
    rsa = calculate_rsa(shielded_metrics['final_equity'], baseline_metrics['final_equity'])
    
    # Determine shield effect
    shield_effects = []
    if drawdown_diff > 0:  # Less negative = better
        shield_effects.append(f"Reduced max drawdown by {drawdown_improvement_pct:.1f}%")
    if blocked_count > 0:
        shield_effects.append(f"Blocked {blocked_count} trades via safety rails")
    if trades_diff < 0:
        shield_effects.append(f"Reduced trade count by {abs(trades_diff)} trades")
    if equity_diff > 0:
        shield_effects.append(f"Increased final equity by {equity_diff_pct:.2f}%")
    elif equity_diff < 0:
        shield_effects.append(f"Reduced final equity by {abs(equity_diff_pct):.2f}%")
    
    comparison = {
        'baseline': {
            'final_equity': baseline_metrics['final_equity'],
            'total_pnl': baseline_metrics['total_pnl'],
            'pnl_percent': baseline_metrics['pnl_percent'],
            'max_drawdown': baseline_metrics['max_drawdown'],
            'total_trades': baseline_metrics['total_trades'],
            'win_rate': baseline_metrics['win_rate']
        },
        'shielded': {
            'final_equity': shielded_metrics['final_equity'],
            'total_pnl': shielded_metrics['total_pnl'],
            'pnl_percent': shielded_metrics['pnl_percent'],
            'max_drawdown': shielded_metrics['max_drawdown'],
            'total_trades': shielded_metrics['total_trades'],
            'win_rate': shielded_metrics['win_rate'],
            'blocked_trades': blocked_count
        },
        'differences': {
            'equity_diff': equity_diff,
            'equity_diff_pct': equity_diff_pct,
            'pnl_diff': pnl_diff,
            'pnl_diff_pct': pnl_diff_pct,
            'drawdown_diff': drawdown_diff,
            'drawdown_improvement_pct': drawdown_improvement_pct,
            'trades_diff': trades_diff
        },
        'rsa': rsa,
        'shield_effect': shield_effects
    }
    
    return comparison


def generate_markdown_summary(summary: Dict[str, Any]) -> str:
    """
    Generate Markdown summary report from historical validation results
    
    Args:
        summary: Summary dict from run_historical_validation()
        
    Returns:
        Markdown string with comprehensive comparison report
    """
    baseline = summary['baseline']
    baseline_metrics = baseline['portfolio_metrics']
    scenarios = summary.get('scenarios', {})
    
    lines = [
        "# Historical Validation Report",
        "",
        f"**Dataset**: `{summary['data_path']}`",
        f"**Symbols**: {', '.join(summary['symbols'])}",
        f"**Initial Equity**: ${summary['initial_equity']:,.2f}",
    ]
    
    if summary.get('start_date'):
        lines.append(f"**Start Date**: {summary['start_date']}")
    if summary.get('end_date'):
        lines.append(f"**End Date**: {summary['end_date']}")
    
    lines.extend([
        "",
        "## Baseline Metrics (Engine Only)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Final Equity | ${baseline_metrics['final_equity']:,.2f} |",
        f"| Total P&L | ${baseline_metrics['total_pnl']:,.2f} ({baseline_metrics['pnl_percent']:.2f}%) |",
        f"| Max Drawdown | {baseline_metrics['max_drawdown']:.2%} |",
        f"| Total Trades | {baseline_metrics['total_trades']} |",
        f"| Win Rate | {baseline_metrics['win_rate']:.2%} |",
        "",
        "## Scenario Comparisons",
        "",
        "| Scenario | Final Equity | Δ vs Baseline | RSA | Max DD | Δ DD | Trades | Blocked | Notes |",
        "|----------|-------------:|---------------:|----:|-------:|-----:|-------:|--------:|-------|"
    ])
    
    # Add rows for each capital_shielded scenario
    for scenario_name, scenario_data in scenarios.items():
        comparison = scenario_data['comparison']
        shielded_key = 'capital_shielded' if 'capital_shielded' in comparison else 'shielded'
        shielded_metrics = comparison[shielded_key]
        differences = comparison['differences']
        
        # Format equity difference
        equity_diff_str = f"${differences['equity_diff']:+,.2f} ({differences['equity_diff_pct']:+.2f}%)"
        
        # Format RSA
        rsa = comparison.get('rsa', 0.0)
        rsa_str = f"{rsa:+.2f}%"
        
        # Format drawdown difference (improvement)
        dd_diff_str = f"{differences['drawdown_diff']:+.2%}"
        if differences['drawdown_improvement_pct'] > 0:
            dd_diff_str += f" ({differences['drawdown_improvement_pct']:.1f}% better)"
        
        # Format trades difference
        trades_diff_str = f"{differences['trades_diff']:+d}"
        
        # Blocked trades
        blocked = shielded_metrics.get('blocked_trades', 0)
        
        # Notes (shield effects)
        notes = ", ".join(comparison['shield_effect'][:2]) if comparison['shield_effect'] else "No significant effects"
        if len(notes) > 50:
            notes = notes[:47] + "..."
        
        lines.append(
            f"| {scenario_name} | "
            f"${shielded_metrics['final_equity']:,.2f} | "
            f"{equity_diff_str} | "
            f"{rsa_str} | "
            f"{shielded_metrics['max_drawdown']:.2%} | "
            f"{dd_diff_str} | "
            f"{shielded_metrics['total_trades']} | "
            f"{blocked} | "
            f"{notes} |"
        )
    
    lines.extend([
        "",
        "## Capital Shield Effects Summary",
        ""
    ])
    
    # Add detailed shield effects for each scenario
    for scenario_name, scenario_data in scenarios.items():
        comparison = scenario_data['comparison']
        if comparison['shield_effect']:
            lines.append(f"### {scenario_name.replace('_', ' ').title()}")
            lines.append("")
            for effect in comparison['shield_effect']:
                lines.append(f"- {effect}")
            lines.append("")
    
    lines.extend([
        "---",
        "",
        f"*Generated: {summary.get('timestamp', 'N/A')}*"
    ])
    
    return "\n".join(lines)


def generate_crash_test_summary(crash_test_results: Dict[str, Any]) -> str:
    """
    Generate Markdown summary for crash test results
    
    Args:
        crash_test_results: Dict from run_all_crash_tests() or individual crash test
        
    Returns:
        Markdown string with crash test summary
    """
    lines = [
        "# Crash Test Validation Report",
        "",
        "This report validates Capital Shield safety rails under stress conditions.",
        "",
        "## Test Scenarios",
        "",
        "1. **Drawdown Crash Test**: Max drawdown safety rail triggers",
        "2. **Health Failure Test**: Health rail blocks trades when system unhealthy",
        "3. **Bear Regime Strict Block Test**: Regime guard blocks BUYs in STRICT mode",
        "",
        "---",
        ""
    ]
    
    # Process each crash test
    if 'drawdown_crash' in crash_test_results:
        lines.extend(_format_crash_test_section(
            "Drawdown Crash Test",
            crash_test_results['drawdown_crash'],
            "Max drawdown safety rail should block trades when drawdown exceeds threshold"
        ))
    
    if 'health_failure' in crash_test_results:
        lines.extend(_format_crash_test_section(
            "Health Failure Test",
            crash_test_results['health_failure'],
            "Health rail should block trades when system health is False"
        ))
    
    if 'bear_regime' in crash_test_results:
        lines.extend(_format_crash_test_section(
            "Bear Regime Strict Block Test",
            crash_test_results['bear_regime'],
            "Regime guard should block BEAR+BUY trades in STRICT mode, allow in PERMISSIVE"
        ))
    
    # Handle individual crash test result (not wrapped in dict)
    if 'test_name' in crash_test_results:
        test_name_map = {
            'drawdown_crash_test': 'Drawdown Crash Test',
            'health_failure_test': 'Health Failure Test',
            'bear_regime_strict_block_test': 'Bear Regime Strict Block Test'
        }
        test_title = test_name_map.get(crash_test_results['test_name'], 'Crash Test')
        lines.extend(_format_crash_test_section(
            test_title,
            crash_test_results,
            "Safety rail validation"
        ))
    
    lines.extend([
        "",
        "---",
        "",
        "*Generated: Crash Test Validation*"
    ])
    
    return "\n".join(lines)


def _format_crash_test_section(title: str, result: Dict[str, Any], description: str) -> List[str]:
    """Format a single crash test section"""
    lines = [
        f"## {title}",
        "",
        description,
        ""
    ]
    
    shielded_key = 'capital_shielded' if 'capital_shielded' in result else 'shielded'
    if 'baseline' in result and shielded_key in result:
        # Single capital_shielded comparison
        baseline_metrics = result['baseline']['portfolio_metrics']
        shielded_metrics = result[shielded_key]['portfolio_metrics']
        comparison = result.get('comparison', {})
        
        lines.extend([
            "### Baseline vs Shielded",
            "",
            "| Metric | Baseline | Shielded | Difference |",
            "|--------|----------|----------|------------|",
            f"| Final Equity | ${baseline_metrics['final_equity']:,.2f} | ${shielded_metrics['final_equity']:,.2f} | ${shielded_metrics['final_equity'] - baseline_metrics['final_equity']:+,.2f} |",
            f"| Max Drawdown | {baseline_metrics['max_drawdown']:.2%} | {shielded_metrics['max_drawdown']:.2%} | {shielded_metrics['max_drawdown'] - baseline_metrics['max_drawdown']:+.2%} |",
            f"| Total Trades | {baseline_metrics['total_trades']} | {shielded_metrics['total_trades']} | {shielded_metrics['total_trades'] - baseline_metrics['total_trades']:+d} |",
            f"| Blocked Trades | - | {result[shielded_key].get('blocked_trades_count', 0)} | - |",
            ""
        ])
        
        if comparison.get('shield_effect'):
            lines.append("### Capital Shield Effects")
            lines.append("")
            for effect in comparison['shield_effect']:
                lines.append(f"- {effect}")
            lines.append("")
    
    elif 'baseline' in result and ('capital_shielded_strict' in result or 'shielded_strict' in result):
        # Multiple capital_shielded comparisons
        baseline_metrics = result['baseline']['portfolio_metrics']
        strict_key = 'capital_shielded_strict' if 'capital_shielded_strict' in result else 'shielded_strict'
        permissive_key = 'capital_shielded_permissive' if 'capital_shielded_permissive' in result else 'shielded_permissive'
        strict_metrics = result[strict_key]['portfolio_metrics']
        permissive_metrics = result[permissive_key]['portfolio_metrics']
        
        lines.extend([
            "### Baseline vs Capital Shielded (STRICT) vs Capital Shielded (PERMISSIVE)",
            "",
            "| Metric | Baseline | STRICT | PERMISSIVE |",
            "|--------|----------|--------|------------|",
            f"| Final Equity | ${baseline_metrics['final_equity']:,.2f} | ${strict_metrics['final_equity']:,.2f} | ${permissive_metrics['final_equity']:,.2f} |",
            f"| Max Drawdown | {baseline_metrics['max_drawdown']:.2%} | {strict_metrics['max_drawdown']:.2%} | {permissive_metrics['max_drawdown']:.2%} |",
            f"| Total Trades | {baseline_metrics['total_trades']} | {strict_metrics['total_trades']} | {permissive_metrics['total_trades']} |",
            f"| Blocked Trades | - | {result[strict_key].get('blocked_trades_count', 0)} | {result[permissive_key].get('blocked_trades_count', 0)} |",
            ""
        ])
        
        # Add shield effects for STRICT
        if 'comparison_strict' in result:
            comparison = result['comparison_strict']
            if comparison.get('shield_effect'):
                lines.append("### Capital Shield Effects (STRICT)")
                lines.append("")
                for effect in comparison['shield_effect']:
                    lines.append(f"- {effect}")
                lines.append("")
        
        # Add shield effects for PERMISSIVE
        if 'comparison_permissive' in result:
            comparison = result['comparison_permissive']
            if comparison.get('shield_effect'):
                lines.append("### Capital Shield Effects (PERMISSIVE)")
                lines.append("")
                for effect in comparison['shield_effect']:
                    lines.append(f"- {effect}")
                lines.append("")
    
    return lines


def generate_investor_summary(multi_results: Dict[str, Any]) -> str:
    """
    Generate investor-grade Markdown summary from multi-dataset validation
    
    Args:
        multi_results: Summary dict from run_multi_validation()
        
    Returns:
        Markdown string with comprehensive investor report
    """
    datasets = multi_results.get('datasets', [])
    presets_tested = multi_results.get('presets_tested', [])
    total_datasets = multi_results.get('total_datasets', len(datasets))
    
    lines = [
        "# BoonMindX Capital Shield – Investor Validation Report",
        "",
        "**Precision intelligence for a volatile world.**",
        "",
        "",
        "## Executive Summary",
        "",
        f"We tested BoonMindX Capital Shield vs baseline across **{total_datasets} datasets** and **{len(presets_tested)} BoonMindX Capital Shield configurations**.",
        "",
        "### Key Takeaways",
        ""
    ]
    
    # Calculate aggregate statistics
    preset_stats = {}
    for preset_name in presets_tested:
        preset_stats[preset_name] = {
            'dd_improvements': [],
            'pnl_changes': [],
            'datasets_tested': 0
        }
    
    for dataset_result in datasets:
        baseline_metrics = dataset_result['baseline']['portfolio_metrics']
        
        for preset_name, scenario_data in dataset_result.get('preset_scenarios', {}).items():
            if preset_name in preset_stats:
                comparison = scenario_data.get('comparison', {})
                differences = comparison.get('differences', {})
                
                preset_stats[preset_name]['dd_improvements'].append(
                    differences.get('drawdown_improvement_pct', 0.0)
                )
                preset_stats[preset_name]['pnl_changes'].append(
                    differences.get('pnl_diff_pct', 0.0)
                )
                preset_stats[preset_name]['datasets_tested'] += 1
    
    # Generate key takeaways
    for preset_name in presets_tested:
        if preset_name in preset_stats:
            stats = preset_stats[preset_name]
            if stats['dd_improvements']:
                avg_dd_improvement = sum(stats['dd_improvements']) / len(stats['dd_improvements'])
                avg_pnl_change = sum(stats['pnl_changes']) / len(stats['pnl_changes']) if stats['pnl_changes'] else 0.0
                
                preset_config = get_preset_config(preset_name)
                preset_display = preset_config.get('name', preset_name.upper())
                
                if avg_dd_improvement > 0:
                    lines.append(f"- **{preset_display}**: Reduced max drawdown by an average of {avg_dd_improvement:.1f}% across {stats['datasets_tested']} datasets")
                if avg_pnl_change != 0:
                    lines.append(f"  - P&L impact: {avg_pnl_change:+.2f}% average change vs baseline")
    
    lines.extend([
        "",
        "---",
        "",
        "## Methodology",
        "",
        "- **Backtest Period**: Historical data from provided datasets",
        "- **No Real Capital**: All simulations are 100% sandbox, no real capital deployed",
        "- **Baseline**: Raw BearHunter engine only (no BoonMindX Capital Shield safety rails)",
        "- **Capital Shielded**: BearHunter engine + BoonMindX Capital Shield safety rails (configurable presets)",
        "- **Engine Mode**: " + multi_results.get('engine_mode', 'MOCK') + " (simulated)",
        "",
        "---",
        ""
    ])
    
    # Per-Dataset Summary Tables
    lines.append("## Per-Dataset Summary")
    lines.append("")
    
    for dataset_result in datasets:
        dataset_name = dataset_result['dataset_name']
        baseline_metrics = dataset_result['baseline']['portfolio_metrics']
        
        lines.append(f"### Dataset: {dataset_name}")
        lines.append("")
        
        # Baseline metrics
        lines.append("**Baseline Metrics:**")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Final Equity | ${baseline_metrics['final_equity']:,.2f} |")
        lines.append(f"| P&L % | {baseline_metrics['pnl_percent']:.2f}% |")
        lines.append(f"| Max Drawdown | {baseline_metrics['max_drawdown']:.2%} |")
        lines.append(f"| Total Trades | {baseline_metrics['total_trades']} |")
        lines.append("")
        
        # Preset comparison table
        lines.append("**Preset Comparison:**")
        lines.append("")
        lines.append("| Preset | P&L % | Max DD | RSA | Trades | Blocked | Δ P&L | Δ DD |")
        lines.append("|--------|------:|-------:|----:|-------:|--------:|------:|-----:|")
        
        for preset_name in presets_tested:
            if preset_name in dataset_result.get('preset_scenarios', {}):
                scenario_data = dataset_result['preset_scenarios'][preset_name]
                preset_metrics = scenario_data['results']['portfolio_metrics']
                comparison = scenario_data.get('comparison', {})
                differences = comparison.get('differences', {})
                
                preset_config = scenario_data.get('preset_config', {})
                preset_display = preset_config.get('name', preset_name.upper())
                
                blocked = scenario_data['results'].get('blocked_trades_count', 0)
                pnl_diff_pct = differences.get('pnl_diff_pct', 0.0)
                dd_diff = differences.get('drawdown_diff', 0.0)
                rsa = comparison.get('rsa', 0.0)
                
                lines.append(
                    f"| {preset_display} | "
                    f"{preset_metrics['pnl_percent']:.2f}% | "
                    f"{preset_metrics['max_drawdown']:.2%} | "
                    f"{rsa:+.2f}% | "
                    f"{preset_metrics['total_trades']} | "
                    f"{blocked} | "
                    f"{pnl_diff_pct:+.2f}% | "
                    f"{dd_diff:+.2%} |"
                )
        
        lines.append("")
    
    # Preset Comparison Section
    lines.append("---")
    lines.append("")
    lines.append("## Preset Comparison")
    lines.append("")
    
    for preset_name in presets_tested:
        if preset_name in preset_stats:
            stats = preset_stats[preset_name]
            
            try:
                preset_config = get_preset_config(preset_name)
                preset_display = preset_config['name']
                preset_desc = preset_config.get('description', '')
            except:
                preset_display = preset_name.upper()
                preset_desc = ''
            
            lines.append(f"### {preset_display}")
            lines.append("")
            
            if preset_desc:
                lines.append(f"*{preset_desc}*")
                lines.append("")
            
            if stats['dd_improvements']:
                avg_dd_improvement = sum(stats['dd_improvements']) / len(stats['dd_improvements'])
                avg_pnl_change = sum(stats['pnl_changes']) / len(stats['pnl_changes']) if stats['pnl_changes'] else 0.0
                
                lines.append("**Aggregate Performance vs Baseline:**")
                lines.append("")
                lines.append(f"- Average Max Drawdown Improvement: {avg_dd_improvement:.1f}%")
                lines.append(f"- Average P&L Change: {avg_pnl_change:+.2f}%")
                lines.append(f"- Datasets Tested: {stats['datasets_tested']}")
                lines.append("")
                
                # Interpretation
                if avg_dd_improvement > 20:
                    interpretation = f"{preset_display} significantly reduces drawdowns, providing strong capital protection."
                elif avg_dd_improvement > 10:
                    interpretation = f"{preset_display} provides moderate drawdown reduction while maintaining trading flexibility."
                elif avg_dd_improvement > 0:
                    interpretation = f"{preset_display} offers light drawdown protection with minimal impact on trading activity."
                else:
                    interpretation = f"{preset_display} maintains baseline performance characteristics."
                
                if avg_pnl_change < -5:
                    interpretation += " Some upside may be sacrificed for protection."
                elif avg_pnl_change > 5:
                    interpretation += " Shows potential for improved returns."
                
                lines.append(f"**Interpretation**: {interpretation}")
                lines.append("")
    
    # Risk & Limitations
    lines.extend([
        "---",
        "",
        "## Risk & Limitations",
        "",
        "⚠️ **Important Disclaimers:**",
        "",
        "- **Historical Performance**: Results shown are based on historical data and do not guarantee future performance.",
        "- **Simulated Environment**: All tests run in a sandbox environment with no real capital at risk.",
        "- **Engine Mode**: Tests may use simulated (MOCK) engine responses; live trading behavior may differ.",
        "- **Data Limitations**: Results depend on the quality and representativeness of historical datasets used.",
        "- **No Guarantees**: Past performance does not guarantee future results. Trading involves risk of loss.",
        "",
        "---",
        "",
        f"*Report generated: {multi_results.get('timestamp', 'N/A')}*"
    ])
    
    return "\n".join(lines)


def compare_with_baseline(
    sim_results: Dict[str, Any],
    baseline_results: Optional[Dict[str, Any]] = None
) -> str:
    """
    Compare simulation results with baseline (e.g., BearHunter engine baseline vs BoonMindX Capital Shield)
    
    Args:
        sim_results: Results from BoonMindX Capital Shield simulation
        baseline_results: Optional baseline results for comparison
        
    Returns:
        Comparison report string
    """
    if not baseline_results:
        return "No baseline provided for comparison"
    
    comparison = compare_runs(baseline_results, sim_results)
    
    lines = [
        "=" * 80,
        "COMPARISON: Baseline (BearHunter engine) vs BoonMindX Capital Shield",
        "=" * 80,
        "",
        "Baseline (Engine Only):",
        f"  Final Equity: ${comparison['baseline']['final_equity']:,.2f}",
        f"  Total P&L: ${comparison['baseline']['total_pnl']:,.2f} ({comparison['baseline']['pnl_percent']:.2f}%)",
        f"  Max Drawdown: {comparison['baseline']['max_drawdown']:.2%}",
        f"  Total Trades: {comparison['baseline']['total_trades']}",
        f"  Win Rate: {comparison['baseline']['win_rate']:.2%}",
        "",
        "BoonMindX Capital Shielded (Engine + Safety Rails):",
        f"  Final Equity: ${comparison['shielded']['final_equity']:,.2f}",
        f"  Total P&L: ${comparison['shielded']['total_pnl']:,.2f} ({comparison['shielded']['pnl_percent']:.2f}%)",
        f"  Max Drawdown: {comparison['shielded']['max_drawdown']:.2%}",
        f"  Total Trades: {comparison['shielded']['total_trades']}",
        f"  Win Rate: {comparison['shielded']['win_rate']:.2%}",
        f"  Blocked Trades: {comparison['shielded']['blocked_trades']}",
        "",
        "Differences:",
        f"  Equity: ${comparison['differences']['equity_diff']:,.2f} ({comparison['differences']['equity_diff_pct']:+.2f}%)",
        f"  P&L: ${comparison['differences']['pnl_diff']:,.2f} ({comparison['differences']['pnl_diff_pct']:+.2f}%)",
        f"  Drawdown: {comparison['differences']['drawdown_diff']:.2%} (improvement: {comparison['differences']['drawdown_improvement_pct']:.1f}%)",
        f"  Trades: {comparison['differences']['trades_diff']:+d}",
        "",
        "Relative Survival Alpha (RSA):",
        f"  RSA: {comparison.get('rsa', 0):+.2f}%",
        f"  Interpretation: Capital Shield {'preserved' if comparison.get('rsa', 0) > 0 else 'reduced'} {abs(comparison.get('rsa', 0)):.2f}% {'more' if comparison.get('rsa', 0) > 0 else 'less'} capital than baseline",
        "",
        "BoonMindX Capital Shield Effect:",
    ]
    
    if comparison['shield_effect']:
        for effect in comparison['shield_effect']:
            lines.append(f"  • {effect}")
    else:
        lines.append("  • No significant shield effects detected")
    
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)

