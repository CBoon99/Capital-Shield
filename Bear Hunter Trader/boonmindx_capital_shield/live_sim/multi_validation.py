"""
Multi-Dataset Historical Validation

Run validation across multiple datasets and BoonMindX Capital Shield presets,
producing investor-grade reports.
"""
import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .runner import run_simulation
from .reporting import compare_runs
from .presets import get_preset_config, apply_preset, list_presets


def run_dataset_validation(
    data_path: str,
    symbols: List[str],
    presets: List[str],
    initial_equity: float = 100000.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    engine_mode: str = "MOCK"  # Use MOCK for deterministic testing
) -> Dict[str, Any]:
    """
    Run validation for a single dataset across baseline + multiple presets
    
    Args:
        data_path: Path to CSV data file
        symbols: List of symbols to trade
        presets: List of preset names to test
        initial_equity: Starting equity
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        engine_mode: Engine mode (MOCK or LIVE)
        
    Returns:
        Dict with baseline results and preset scenario results
    """
    dataset_name = Path(data_path).stem
    
    # Run baseline
    print(f"  Running baseline for {dataset_name}...")
    baseline_results = run_simulation(
        data_path=data_path,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_equity=initial_equity,
        mode="baseline"
    )
    
    # Run each preset
    preset_scenarios = {}
    
    for preset_name in presets:
        preset_config = get_preset_config(preset_name)
        
        print(f"  Running {preset_config['name']} preset for {dataset_name}...")
        
        # Store original env values
        original_env = {}
        env_keys = ['CAPITAL_SHIELD_MODE', 'SHIELD_MODE', 'MAX_DRAWDOWN_THRESHOLD', 'BLOCK_BEAR_BUYS', 'HEALTH_CHECK_ENABLED']
        for key in env_keys:
            original_env[key] = os.environ.get(key)
        
        try:
            # Apply preset
            apply_preset(preset_name)
            
            # Override engine_mode if needed (for testing)
            if engine_mode != "LIVE":
                os.environ['ENGINE_MODE'] = engine_mode
            
            # Run capital_shielded simulation
            capital_shielded_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                initial_equity=initial_equity,
                mode="capital_shielded",
                engine_mode=engine_mode,
                capital_shield_mode=preset_config['capital_shield_mode']
            )
            
            # Compare with baseline
            comparison = compare_runs(baseline_results, capital_shielded_results)
            
            preset_scenarios[preset_name] = {
                'preset_name': preset_config['name'],
                'preset_config': preset_config,
                'results': capital_shielded_results,
                'comparison': comparison
            }
            
        finally:
            # Restore original env values
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    
    return {
        'dataset_name': dataset_name,
        'data_path': data_path,
        'symbols': symbols,
        'start_date': start_date,
        'end_date': end_date,
        'initial_equity': initial_equity,
        'baseline': baseline_results,
        'preset_scenarios': preset_scenarios
    }


def run_multi_validation(
    datasets: List[str],
    symbols: List[str],
    presets: List[str],
    initial_equity: float = 100000.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    engine_mode: str = "MOCK",
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run validation across multiple datasets and presets
    
    Args:
        datasets: List of CSV file paths
        symbols: List of symbols to trade
        presets: List of preset names to test
        initial_equity: Starting equity
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        engine_mode: Engine mode (MOCK or LIVE)
        output_dir: Optional directory to save individual dataset results
        
    Returns:
        Dict with all dataset results
    """
    print("=" * 80)
    print("MULTI-DATASET VALIDATION")
    print("=" * 80)
    print(f"Datasets: {len(datasets)}")
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Presets: {', '.join(presets)}")
    print(f"Initial Equity: ${initial_equity:,.2f}")
    print("=" * 80)
    print()
    
    dataset_results = []
    
    for i, dataset_path in enumerate(datasets, 1):
        print(f"[{i}/{len(datasets)}] Processing {Path(dataset_path).name}...")
        
        try:
            result = run_dataset_validation(
                data_path=dataset_path,
                symbols=symbols,
                presets=presets,
                initial_equity=initial_equity,
                start_date=start_date,
                end_date=end_date,
                engine_mode=engine_mode
            )
            
            dataset_results.append(result)
            
            # Save individual dataset result if output_dir specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                dataset_file = os.path.join(output_dir, f"{result['dataset_name']}.json")
                with open(dataset_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
            
        except Exception as e:
            print(f"  ERROR: Failed to process {dataset_path}: {e}")
            continue
        
        print()
    
    summary = {
        'datasets': dataset_results,
        'total_datasets': len(dataset_results),
        'symbols': symbols,
        'presets_tested': presets,
        'initial_equity': initial_equity,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run multi-dataset historical validation with Shield presets"
    )
    parser.add_argument("--datasets", nargs="+", required=True, 
                       help="Paths to CSV data files")
    parser.add_argument("--symbols", nargs="+", required=True,
                       help="Symbols to trade")
    parser.add_argument("--presets", nargs="+", 
                       choices=["conservative", "balanced", "aggressive"],
                       default=["conservative", "balanced", "aggressive"],
                       help="Shield presets to test")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--initial-equity", type=float, default=100000.0)
    parser.add_argument("--engine-mode", default="MOCK", choices=["MOCK", "LIVE"],
                       help="Engine mode (MOCK for testing, LIVE for production)")
    parser.add_argument("--output-dir", help="Directory to save results")
    parser.add_argument("--output-json", help="Output JSON file for summary")
    parser.add_argument("--output-markdown", help="Output Markdown report file")
    
    args = parser.parse_args()
    
    # Run validation
    summary = run_multi_validation(
        datasets=args.datasets,
        symbols=args.symbols,
        presets=args.presets,
        initial_equity=args.initial_equity,
        start_date=args.start_date,
        end_date=args.end_date,
        engine_mode=args.engine_mode,
        output_dir=args.output_dir
    )
    
    # Save JSON summary
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"JSON summary saved to: {args.output_json}")
    
    # Generate and save Markdown report
    from .reporting import generate_investor_summary
    markdown_report = generate_investor_summary(summary)
    
    if args.output_markdown:
        with open(args.output_markdown, 'w') as f:
            f.write(markdown_report)
        print(f"Markdown report saved to: {args.output_markdown}")
    else:
        print("\n" + "=" * 80)
        print("INVESTOR VALIDATION REPORT")
        print("=" * 80)
        print(markdown_report)
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Processed {summary['total_datasets']} datasets")
    print(f"Tested {len(args.presets)} presets per dataset")

