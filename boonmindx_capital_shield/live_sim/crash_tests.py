"""
Crash Test Scenarios - Validate BoonMindX Capital Shield safety rails under stress

Three scenarios:
1. Drawdown crash test - max drawdown rail fires
2. Health failure test - health rail blocks trades
3. Bear regime strict block test - regime guard blocks BUYs in STRICT mode
"""
import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .runner import run_simulation
from .reporting import compare_runs, generate_markdown_summary
from .data_loader import create_synthetic_data


def create_drawdown_crash_data(
    symbol: str = "CRASH_TEST",
    num_candles: int = 50,
    initial_price: float = 100.0,
    crash_start: int = 20,
    crash_severity: float = 0.30  # 30% drop
) -> pd.DataFrame:
    """
    Create synthetic data that triggers drawdown crash
    
    Price rises initially, then crashes to trigger max drawdown threshold
    
    Args:
        symbol: Symbol name
        num_candles: Number of candles
        initial_price: Starting price
        crash_start: Candle index where crash begins
        crash_severity: Percentage drop (0.30 = 30% drop)
        
    Returns:
        DataFrame with date index and price column
    """
    dates = pd.date_range(start='2024-01-01', periods=num_candles, freq='D')
    prices = []
    
    current_price = initial_price
    
    for i in range(num_candles):
        if i < crash_start:
            # Rising phase - small positive moves
            change = np.random.uniform(0.01, 0.03)
            current_price *= (1 + change)
        elif i == crash_start:
            # Crash begins
            current_price *= (1 - crash_severity)
        else:
            # Continue decline or stabilize
            change = np.random.uniform(-0.02, 0.01)
            current_price *= (1 + change)
        
        prices.append(current_price)
    
    df = pd.DataFrame({
        symbol: prices
    }, index=dates)
    
    return df


def create_bear_regime_data(
    symbol: str = "BEAR_REGIME",
    num_candles: int = 30,
    initial_price: float = 100.0
) -> pd.DataFrame:
    """
    Create synthetic data that produces BEAR regime signals
    
    Consistent downward trend to trigger BEAR regime detection
    
    Args:
        symbol: Symbol name
        num_candles: Number of candles
        initial_price: Starting price
        
    Returns:
        DataFrame with date index and price column
    """
    dates = pd.date_range(start='2024-01-01', periods=num_candles, freq='D')
    prices = []
    
    current_price = initial_price
    
    for i in range(num_candles):
        # Consistent decline to trigger BEAR regime
        change = np.random.uniform(-0.03, -0.01)
        current_price *= (1 + change)
        prices.append(current_price)
    
    df = pd.DataFrame({
        symbol: prices
    }, index=dates)
    
    return df


def run_drawdown_crash_test(
    output_dir: Optional[str] = None,
    max_drawdown_threshold: float = -0.10
) -> Dict[str, Any]:
    """
    Run drawdown crash test scenario
    
    Creates synthetic data that triggers max drawdown safety rail
    
    Args:
        output_dir: Optional directory to save results
        max_drawdown_threshold: Drawdown threshold for safety rail
        
    Returns:
        Summary dict with baseline and shielded results
    """
    # Create crash test data
    df = create_drawdown_crash_data(
        symbol="CRASH_TEST",
        num_candles=50,
        crash_severity=0.30  # 30% crash
    )
    
    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name)
        data_path = f.name
    
    try:
        symbols = ["CRASH_TEST"]
        initial_equity = 100000.0
        
        # Set environment variable for max drawdown threshold
        import os
        original_threshold = os.environ.get('MAX_DRAWDOWN_THRESHOLD')
        os.environ['MAX_DRAWDOWN_THRESHOLD'] = str(max_drawdown_threshold)
        
        try:
            # Run baseline
            print("Running baseline (drawdown crash test)...")
            baseline_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                initial_equity=initial_equity,
                mode="baseline"
            )
            
            # Run capital_shielded STRICT
            print("Running capital_shielded STRICT (drawdown crash test)...")
            capital_shielded_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                initial_equity=initial_equity,
                mode="capital_shielded",
                engine_mode="MOCK",  # Use MOCK for deterministic testing
                capital_shield_mode="STRICT"
            )
            
            # Compare
            comparison = compare_runs(baseline_results, capital_shielded_results)
            
        finally:
            # Restore original threshold
            if original_threshold:
                os.environ['MAX_DRAWDOWN_THRESHOLD'] = original_threshold
            elif 'MAX_DRAWDOWN_THRESHOLD' in os.environ:
                del os.environ['MAX_DRAWDOWN_THRESHOLD']
        
        summary = {
            'test_name': 'drawdown_crash_test',
            'data_path': data_path,
            'symbols': symbols,
            'initial_equity': initial_equity,
            'max_drawdown_threshold': max_drawdown_threshold,
            'baseline': baseline_results,
            'capital_shielded': capital_shielded_results,
            'comparison': comparison
        }
        
        # Save if output_dir specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'drawdown_crash_test.json')
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        
        return summary
        
    finally:
        # Clean up temp file
        if os.path.exists(data_path):
            os.unlink(data_path)


def run_health_failure_test(
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run health failure test scenario
    
    Sets system health to False and verifies trades are blocked
    
    Args:
        output_dir: Optional directory to save results
        
    Returns:
        Summary dict with baseline and shielded results
    """
    # Create minimal test data
    df = create_synthetic_data(["HEALTH_TEST"], num_candles=20)
    
    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name)
        data_path = f.name
    
    try:
        symbols = ["HEALTH_TEST"]
        initial_equity = 100000.0
        
        # Run baseline (health check ignored)
        print("Running baseline (health failure test)...")
        baseline_results = run_simulation(
            data_path=data_path,
            symbols=symbols,
            initial_equity=initial_equity,
            mode="baseline"
        )
        
        # Set health to False before running shielded scenarios
        from app.core.safety_rails import set_system_health
        
        # Run capital_shielded STRICT with health=False
        print("Running capital_shielded STRICT with health=False...")
        set_system_health(False)
        
        try:
            capital_shielded_strict_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                initial_equity=initial_equity,
                mode="capital_shielded",
                engine_mode="MOCK",
                capital_shield_mode="STRICT"
            )
        finally:
            # Restore health
            set_system_health(True)
        
        # Run capital_shielded PERMISSIVE with health=False
        print("Running capital_shielded PERMISSIVE with health=False...")
        set_system_health(False)
        
        try:
            capital_shielded_permissive_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                initial_equity=initial_equity,
                mode="capital_shielded",
                engine_mode="MOCK",
                capital_shield_mode="PERMISSIVE"
            )
        finally:
            # Restore health
            set_system_health(True)
        
        # Compare
        comparison_strict = compare_runs(baseline_results, capital_shielded_strict_results)
        comparison_permissive = compare_runs(baseline_results, capital_shielded_permissive_results)
        
        summary = {
            'test_name': 'health_failure_test',
            'data_path': data_path,
            'symbols': symbols,
            'initial_equity': initial_equity,
            'baseline': baseline_results,
            'capital_shielded_strict': capital_shielded_strict_results,
            'capital_shielded_permissive': capital_shielded_permissive_results,
            'comparison_strict': comparison_strict,
            'comparison_permissive': comparison_permissive
        }
        
        # Save if output_dir specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'health_failure_test.json')
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        
        return summary
        
    finally:
        # Clean up temp file
        if os.path.exists(data_path):
            os.unlink(data_path)


def run_bear_regime_strict_block_test(
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run bear regime strict block test scenario
    
    Creates BEAR regime data and verifies STRICT blocks BUYs but PERMISSIVE allows
    
    Args:
        output_dir: Optional directory to save results
        
    Returns:
        Summary dict with baseline, PERMISSIVE, and STRICT results
    """
    # Create bear regime data
    df = create_bear_regime_data(
        symbol="BEAR_REGIME",
        num_candles=30
    )
    
    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name)
        data_path = f.name
    
    try:
        symbols = ["BEAR_REGIME"]
        initial_equity = 100000.0
        
        # Set BLOCK_BEAR_BUYS for STRICT mode
        import os
        original_block_bear = os.environ.get('BLOCK_BEAR_BUYS')
        os.environ['BLOCK_BEAR_BUYS'] = 'true'
        
        try:
            # Run baseline
            print("Running baseline (bear regime test)...")
            baseline_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                initial_equity=initial_equity,
                mode="baseline"
            )
            
            # Run capital_shielded PERMISSIVE
            print("Running capital_shielded PERMISSIVE (bear regime test)...")
            capital_shielded_permissive_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                initial_equity=initial_equity,
                mode="capital_shielded",
                engine_mode="MOCK",
                capital_shield_mode="PERMISSIVE"
            )
            
            # Run capital_shielded STRICT
            print("Running capital_shielded STRICT (bear regime test)...")
            capital_shielded_strict_results = run_simulation(
                data_path=data_path,
                symbols=symbols,
                initial_equity=initial_equity,
                mode="capital_shielded",
                engine_mode="MOCK",
                capital_shield_mode="STRICT"
            )
            
            # Compare
            comparison_permissive = compare_runs(baseline_results, capital_shielded_permissive_results)
            comparison_strict = compare_runs(baseline_results, capital_shielded_strict_results)
            
        finally:
            # Restore original setting
            if original_block_bear:
                os.environ['BLOCK_BEAR_BUYS'] = original_block_bear
            elif 'BLOCK_BEAR_BUYS' in os.environ:
                del os.environ['BLOCK_BEAR_BUYS']
        
        summary = {
            'test_name': 'bear_regime_strict_block_test',
            'data_path': data_path,
            'symbols': symbols,
            'initial_equity': initial_equity,
            'baseline': baseline_results,
            'capital_shielded_permissive': capital_shielded_permissive_results,
            'capital_shielded_strict': capital_shielded_strict_results,
            'comparison_permissive': comparison_permissive,
            'comparison_strict': comparison_strict
        }
        
        # Save if output_dir specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'bear_regime_strict_block_test.json')
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        
        return summary
        
    finally:
        # Clean up temp file
        if os.path.exists(data_path):
            os.unlink(data_path)


def run_all_crash_tests(
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run all three crash test scenarios
    
    Args:
        output_dir: Optional directory to save results
        
    Returns:
        Dict with all crash test results
    """
    results = {}
    
    # Run drawdown crash test
    print("=" * 80)
    print("CRASH TEST 1: Drawdown Crash Test")
    print("=" * 80)
    results['drawdown_crash'] = run_drawdown_crash_test(output_dir)
    
    # Run health failure test
    print("\n" + "=" * 80)
    print("CRASH TEST 2: Health Failure Test")
    print("=" * 80)
    results['health_failure'] = run_health_failure_test(output_dir)
    
    # Run bear regime strict block test
    print("\n" + "=" * 80)
    print("CRASH TEST 3: Bear Regime Strict Block Test")
    print("=" * 80)
    results['bear_regime'] = run_bear_regime_strict_block_test(output_dir)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run crash test scenarios to validate BoonMindX Capital Shield safety rails"
    )
    parser.add_argument("--test", choices=["drawdown", "health", "bear", "all"], 
                       default="all", help="Which crash test to run")
    parser.add_argument("--output-dir", help="Directory to save results")
    
    args = parser.parse_args()
    
    if args.test == "drawdown":
        result = run_drawdown_crash_test(args.output_dir)
    elif args.test == "health":
        result = run_health_failure_test(args.output_dir)
    elif args.test == "bear":
        result = run_bear_regime_strict_block_test(args.output_dir)
    else:
        results = run_all_crash_tests(args.output_dir)
        print("\n" + "=" * 80)
        print("ALL CRASH TESTS COMPLETE")
        print("=" * 80)

