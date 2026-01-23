"""
Historical Validation - Run multiple scenarios and compare results

Runs baseline (BearHunter engine) + multiple BoonMindX Capital Shield configurations on historical data
and produces comprehensive comparison reports.
"""
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .runner import run_simulation
from .reporting import compare_runs, generate_markdown_summary


@dataclass
class Scenario:
    """Scenario configuration for historical validation"""
    name: str
    mode: str  # "baseline" or "capital_shielded"
    engine_mode: Optional[str] = None  # "MOCK" or "LIVE" (for capital_shielded)
    capital_shield_mode: Optional[str] = None  # "PERMISSIVE" or "STRICT" (for capital_shielded)
    extra_flags: Optional[Dict[str, Any]] = None


def run_scenario(
    data_path: str,
    symbols: List[str],
    scenario: Scenario,
    initial_equity: float = 100000.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a single scenario simulation
    
    Args:
        data_path: Path to CSV data file
        symbols: List of symbols to trade
        scenario: Scenario configuration
        initial_equity: Starting equity
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        output_dir: Optional directory to save individual scenario results
        
    Returns:
        Results dict from run_simulation()
    """
    # Prepare parameters based on scenario
    if scenario.mode == "baseline":
        mode = "baseline"
        engine_mode = "LIVE"  # Not used but set for consistency
        capital_shield_mode = None
    else:  # capital_shielded
        mode = "capital_shielded"
        engine_mode = scenario.engine_mode or "LIVE"
        capital_shield_mode = scenario.capital_shield_mode or "PERMISSIVE"
    
    # Run simulation
    results = run_simulation(
        data_path=data_path,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_equity=initial_equity,
        mode=mode,
        engine_mode=engine_mode,
        capital_shield_mode=capital_shield_mode
    )
    
    # Save individual scenario results if output_dir specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        scenario_file = os.path.join(output_dir, f"{scenario.name}.json")
        with open(scenario_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    return results


def run_historical_validation(
    data_path: str,
    symbols: List[str],
    initial_equity: float = 100000.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run historical validation with multiple scenarios
    
    Runs baseline + multiple capital_shielded configurations and compares results.
    
    Args:
        data_path: Path to CSV data file
        symbols: List of symbols to trade
        initial_equity: Starting equity
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        output_dir: Optional directory to save individual scenario results
        
    Returns:
        Dict with baseline results and comparisons for each capital_shielded scenario
    """
    # Define scenarios
    scenarios = [
        Scenario(
            name="baseline",
            mode="baseline"
        ),
        Scenario(
            name="capital_shielded_permissive",
            mode="capital_shielded",
            engine_mode="LIVE",
            capital_shield_mode="PERMISSIVE"
        ),
        Scenario(
            name="capital_shielded_strict",
            mode="capital_shielded",
            engine_mode="LIVE",
            capital_shield_mode="STRICT"
        )
    ]
    
    # Run baseline first
    print(f"Running baseline scenario...")
    baseline_scenario = scenarios[0]
    baseline_results = run_scenario(
        data_path=data_path,
        symbols=symbols,
        scenario=baseline_scenario,
        initial_equity=initial_equity,
        start_date=start_date,
        end_date=end_date,
        output_dir=output_dir
    )
    
    # Run capital_shielded scenarios and compare
    scenario_results = {}
    for scenario in scenarios[1:]:  # Skip baseline
        print(f"Running {scenario.name} scenario...")
        capital_shielded_results = run_scenario(
            data_path=data_path,
            symbols=symbols,
            scenario=scenario,
            initial_equity=initial_equity,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir
        )
        
        # Compare with baseline
        comparison = compare_runs(baseline_results, capital_shielded_results)
        
        scenario_results[scenario.name] = {
            'results': capital_shielded_results,
            'comparison': comparison
        }
    
    # Build summary
    summary = {
        'data_path': data_path,
        'symbols': symbols,
        'start_date': start_date,
        'end_date': end_date,
        'initial_equity': initial_equity,
        'baseline': baseline_results,
        'scenarios': scenario_results
    }
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run historical validation with baseline (BearHunter engine) + BoonMindX Capital Shield scenarios"
    )
    parser.add_argument("--data-path", required=True, help="Path to CSV data file")
    parser.add_argument("--symbols", nargs="+", required=True, help="Symbols to trade")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--initial-equity", type=float, default=100000.0)
    parser.add_argument("--output", required=True, help="Output JSON file for summary")
    parser.add_argument("--output-dir", help="Directory for individual scenario results")
    parser.add_argument("--markdown", help="Output Markdown report file")
    
    args = parser.parse_args()
    
    # Run validation
    print("=" * 80)
    print("HISTORICAL VALIDATION")
    print("=" * 80)
    print(f"Data: {args.data_path}")
    print(f"Symbols: {', '.join(args.symbols)}")
    print(f"Initial Equity: ${args.initial_equity:,.2f}")
    print("=" * 80)
    print()
    
    summary = run_historical_validation(
        data_path=args.data_path,
        symbols=args.symbols,
        initial_equity=args.initial_equity,
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir
    )
    
    # Save JSON summary
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary saved to: {args.output}")
    
    # Generate and save Markdown report
    markdown_report = generate_markdown_summary(summary)
    
    if args.markdown:
        with open(args.markdown, 'w') as f:
            f.write(markdown_report)
        print(f"Markdown report saved to: {args.markdown}")
    else:
        print("\n" + "=" * 80)
        print("MARKDOWN REPORT")
        print("=" * 80)
        print(markdown_report)

