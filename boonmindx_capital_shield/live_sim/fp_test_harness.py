"""
False Positive Rate (FPR) Test Harness

Implements the FP_TEST_PROTOCOL.md methodology for measuring false positive rates
across different market regimes and safety rails.
"""
import pandas as pd
import numpy as np
import json
import csv
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from .runner import run_simulation
from .presets import PRESETS, apply_preset, get_preset_config
from .data_loader import load_historical_data


class MarketRegime(Enum):
    """Market regime classification for FP testing"""
    STRONG_BULL = "strong_bull"
    MILD_BULL = "mild_bull"
    SIDEWAYS_LOW_VOL = "sideways_low_vol"
    SIDEWAYS_HIGH_VOL = "sideways_high_vol"
    MILD_BEAR = "mild_bear"


class BlockClassification(Enum):
    """Classification of blocked trades"""
    FP = "false_positive"  # Block in benign conditions
    TP = "true_positive"    # Block during valid early-risk signals
    NA = "not_applicable"   # Rail inactive or not triggered


@dataclass
class BlockEvent:
    """Record of a blocked trade event"""
    timestamp: str
    asset: str
    rail_triggered: str  # "drawdown", "regime", "health", "preset"
    preset_used: str
    shield_action: str  # "block" or "warn"
    market_condition: str  # MarketRegime value
    classification: str  # BlockClassification value
    reason: str
    price_at_block: float
    equity_at_block: float


class MarketRegimeClassifier:
    """
    Classify market regimes based on price action
    
    Implements the 5 controlled regimes from FP_TEST_PROTOCOL.md:
    - Strong Bull (low volatility, strong uptrend)
    - Mild Bull (steady upward drift, mild pullbacks)
    - Sideways Low-Vol (tight range, no clear direction)
    - Sideways High-Vol (whipsaw behavior, no trend)
    - Mild Bear (orderly decline without panic spikes)
    """
    
    @staticmethod
    def classify_regime(price_history: List[float], lookback: int = 50) -> MarketRegime:
        """
        Classify market regime from price history
        
        Args:
            price_history: List of close prices (oldest to newest)
            lookback: Number of periods to analyze
            
        Returns:
            MarketRegime classification
        """
        if len(price_history) < lookback:
            lookback = len(price_history)
        
        if lookback < 20:
            return MarketRegime.SIDEWAYS_LOW_VOL  # Default for insufficient data
        
        recent_prices = price_history[-lookback:]
        prices_array = np.array(recent_prices)
        
        # Calculate metrics
        returns = np.diff(prices_array) / prices_array[:-1]
        volatility = np.std(returns)
        trend = (prices_array[-1] - prices_array[0]) / prices_array[0]
        
        # Calculate range (high - low) relative to mean
        price_range = (np.max(prices_array) - np.min(prices_array)) / np.mean(prices_array)
        
        # Classify based on trend and volatility
        if trend > 0.15 and volatility < 0.02:
            # Strong uptrend, low volatility
            return MarketRegime.STRONG_BULL
        elif trend > 0.05 and volatility < 0.03:
            # Moderate uptrend, low volatility
            return MarketRegime.MILD_BULL
        elif trend < -0.05 and volatility < 0.03:
            # Moderate decline, low volatility (orderly)
            return MarketRegime.MILD_BEAR
        elif abs(trend) < 0.05 and volatility < 0.02:
            # No clear trend, low volatility
            return MarketRegime.SIDEWAYS_LOW_VOL
        else:
            # High volatility, no clear trend
            return MarketRegime.SIDEWAYS_HIGH_VOL


def validate_dataset(data_path: str) -> str:
    """
    Validate dataset meets FP test requirements
    
    Checks:
    - Required columns exist (timestamp, close or open/high/low/close)
    - No missing timestamps
    - All close values are numeric
    - Dataset length ≥ 200 rows
    
    Args:
        data_path: Path to CSV dataset
        
    Returns:
        "VALID" if dataset passes all checks
        
    Raises:
        ValueError: If dataset fails validation
    """
    if not os.path.exists(data_path):
        raise ValueError(f"Dataset file not found: {data_path}")
    
    # Load dataset
    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        raise ValueError(f"Failed to load dataset: {e}")
    
    # Check required columns
    required_cols = ['timestamp']
    if 'close' not in df.columns:
        # Check for OHLC format
        if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError(f"Dataset must have 'close' column or OHLC columns. Found: {df.columns.tolist()}")
    
    # Check timestamp column
    if 'timestamp' not in df.columns:
        raise ValueError(f"Dataset must have 'timestamp' column. Found: {df.columns.tolist()}")
    
    # Check for missing timestamps
    if df['timestamp'].isna().any():
        raise ValueError("Dataset contains missing timestamps")
    
    # Check close values are numeric
    if 'close' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['close']):
            raise ValueError("'close' column must be numeric")
        if df['close'].isna().any():
            raise ValueError("Dataset contains missing close prices")
        if (df['close'] <= 0).any():
            raise ValueError("Dataset contains non-positive close prices")
    
    # Check dataset length
    if len(df) < 200:
        raise ValueError(f"Dataset must have ≥ 200 rows. Found: {len(df)}")
    
    return "VALID"


class FPClassifier:
    """
    Classify blocked trades as FP (False Positive) or TP (True Positive)
    
    Based on FP_TEST_PROTOCOL.md:
    - FP: Block occurred in benign conditions
    - TP: Block occurred during valid early-risk signals
    """
    
    @staticmethod
    def classify_block(
        block_event: BlockEvent,
        market_regime: MarketRegime,
        price_history: List[float],
        equity_history: List[float]
    ) -> BlockClassification:
        """
        Classify a block event as FP, TP, or NA
        
        Args:
            block_event: The block event to classify
            market_regime: Current market regime
            price_history: Price history around the block
            equity_history: Equity history around the block
            
        Returns:
            BlockClassification
        """
        rail = block_event.rail_triggered
        
        # Health rail blocks are always TP (system failure is real risk)
        if rail == "health":
            return BlockClassification.TP
        
        # Regime guard blocks
        if rail == "regime":
            # In benign regimes (bull, sideways), regime blocks are FP
            if market_regime in [MarketRegime.STRONG_BULL, MarketRegime.MILD_BULL, 
                                MarketRegime.SIDEWAYS_LOW_VOL, MarketRegime.SIDEWAYS_HIGH_VOL]:
                return BlockClassification.FP
            # In bear regimes, regime blocks are TP
            elif market_regime == MarketRegime.MILD_BEAR:
                return BlockClassification.TP
            else:
                return BlockClassification.NA
        
        # Drawdown rail blocks
        if rail == "drawdown":
            # Calculate recent drawdown
            if len(equity_history) < 20:
                return BlockClassification.NA
            
            recent_equity = equity_history[-20:]
            peak_equity = max(recent_equity)
            current_equity = recent_equity[-1]
            drawdown = (current_equity - peak_equity) / peak_equity
            
            # If drawdown > 5% in benign regime, it's TP (real risk)
            # If drawdown < 2% in benign regime, it's FP (too sensitive)
            if market_regime in [MarketRegime.STRONG_BULL, MarketRegime.MILD_BULL]:
                if drawdown < -0.02:  # Less than 2% drawdown
                    return BlockClassification.FP
                else:
                    return BlockClassification.TP
            else:
                # In sideways/bear, drawdown blocks are more likely TP
                return BlockClassification.TP
        
        # Preset threshold blocks (depends on preset)
        if rail == "preset":
            # Conservative preset blocks in benign conditions are FP
            if block_event.preset_used == "conservative":
                if market_regime in [MarketRegime.STRONG_BULL, MarketRegime.MILD_BULL]:
                    return BlockClassification.FP
            return BlockClassification.TP
        
        return BlockClassification.NA


def run_fp_test(
    data_path: str,
    symbols: Optional[List[str]] = None,
    presets: List[str] = ["conservative", "balanced", "aggressive"],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_equity: float = 100000.0
) -> Dict[str, Any]:
    """
    Run False Positive Rate test according to FP_TEST_PROTOCOL.md
    
    Args:
        data_path: Path to historical data CSV (OHLCV format or symbol columns)
        symbols: List of symbols to test (if None, will use 'close' column as single symbol)
        presets: List of preset names to test
        start_date: Optional start date filter
        end_date: Optional end date filter
        initial_equity: Starting equity
        
    Returns:
        Dict with FP test results
    """
    # Validate dataset first
    validation_result = validate_dataset(data_path)
    if validation_result != "VALID":
        raise ValueError(f"Dataset validation failed: {validation_result}")
    
    # Load data
    # If symbols not provided, treat as single-asset OHLCV format
    if symbols is None:
        # Load OHLCV format and convert to symbol-column format
        df_raw = pd.read_csv(data_path)
        
        # Create a temporary CSV with 'close' column renamed to a symbol
        # Save to temp file for compatibility with load_historical_data
        import tempfile
        temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df_temp = df_raw.copy()
        df_temp['ASSET_1'] = df_temp['close']
        # Keep timestamp as column (don't set as index yet)
        df_temp[['timestamp', 'ASSET_1']].to_csv(temp_csv.name, index=False)
        temp_csv.close()
        
        # Use the temp file path
        data_path = temp_csv.name
        symbols = ['ASSET_1']
        df = load_historical_data(symbols, data_path, start_date, end_date)
    else:
        df = load_historical_data(symbols, data_path, start_date, end_date)
    
    # Initialize results
    block_events: List[BlockEvent] = []
    regime_classifier = MarketRegimeClassifier()
    fp_classifier = FPClassifier()
    
    # Run baseline (no Shield)
    print("Running baseline simulation...")
    baseline_results = run_simulation(
        data_path=data_path,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_equity=initial_equity,
        mode="baseline"
    )
    
    # Run Capital Shield for each preset
    preset_results = {}
    for preset_name in presets:
        print(f"Running Capital Shield with {preset_name} preset...")
        
        # Apply preset
        preset_config = apply_preset(preset_name)
        
        # Note: preset_name will be tracked via shield_client.set_preset_name()
        # This needs to be done inside run_simulation, but for now we'll
        # add it to the simulation config for tracking
        
        # Run simulation
        shield_results = run_simulation(
            data_path=data_path,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_equity=initial_equity,
            mode="capital_shielded",
            capital_shield_mode=preset_config.get('CAPITAL_SHIELD_MODE', 'PERMISSIVE'),
            preset_name=preset_name  # Pass preset name for tracking
        )
        
        # Extract blocked trades (if available in results)
        blocked_trades = shield_results.get('blocked_trades', [])
        
        # Get equity curve for regime classification
        equity_curve = shield_results.get('equity_curve', [])
        
        # Classify each block
        for trade in blocked_trades:
            # Get price history at block time
            asset = trade.get('asset', 'UNKNOWN')
            block_time = trade.get('timestamp', datetime.now().isoformat())
            block_price = trade.get('price', 0.0)
            block_equity = trade.get('equity', initial_equity)
            
            # Get price history up to block time for regime classification
            # We need to reconstruct this from the simulation state
            # For now, use a simplified approach: classify regime from overall dataset
            try:
                block_timestamp = pd.to_datetime(block_time)
                # Get price history up to block time
                if symbols and len(symbols) > 0:
                    symbol = symbols[0]
                    if symbol in df.columns:
                        price_data = df.loc[df.index <= block_timestamp, symbol].dropna()
                        price_history = price_data.tail(50).tolist() if len(price_data) >= 50 else price_data.tolist()
                    else:
                        price_history = []
                else:
                    price_history = []
                
                # Classify market regime from price history
                if len(price_history) >= 20:
                    market_regime = regime_classifier.classify_regime(price_history)
                else:
                    market_regime = MarketRegime.SIDEWAYS_LOW_VOL  # Default
            except Exception:
                # Fallback to default if classification fails
                market_regime = MarketRegime.STRONG_BULL  # Assume benign for FP testing
            
            # Create block event
            block_event = BlockEvent(
                timestamp=block_time,
                asset=asset,
                rail_triggered=trade.get('rail', 'unknown'),
                preset_used=preset_name,
                shield_action='block',  # All blocked trades are blocks
                market_condition=market_regime.value,
                classification="",  # Will be set below
                reason=trade.get('reason', ''),
                price_at_block=block_price,
                equity_at_block=block_equity
            )
            
            # Get equity history for drawdown classification
            equity_history = equity_curve[:len(equity_curve)] if equity_curve else []
            
            # Classify the block
            classification = fp_classifier.classify_block(
                block_event,
                market_regime,
                price_history if price_history else [],
                equity_history
            )
            block_event.classification = classification.value
            
            block_events.append(block_event)
        
        preset_results[preset_name] = {
            'results': shield_results,
            'block_events': [e for e in block_events if e.preset_used == preset_name]
        }
    
    # Calculate FPR metrics
    fpr_metrics = calculate_fpr_metrics(block_events, presets)
    
    # Compile results
    results = {
        'test_config': {
            'data_path': data_path,
            'symbols': symbols,
            'presets': presets,
            'start_date': start_date,
            'end_date': end_date,
            'initial_equity': initial_equity
        },
        'baseline_results': baseline_results,
        'preset_results': preset_results,
        'block_events': [asdict(e) for e in block_events],
        'fpr_metrics': fpr_metrics,
        'timestamp': datetime.now().isoformat()
    }
    
    return results


def calculate_fpr_metrics(
    block_events: List[BlockEvent],
    presets: List[str]
) -> Dict[str, Any]:
    """
    Calculate False Positive Rate metrics
    
    Formula: FPR = (Number of False Positives / Total Block Events) * 100
    """
    metrics = {
        'per_rail': {},
        'per_preset': {},
        'global': {}
    }
    
    # Per-rail FPR
    rails = ['drawdown', 'regime', 'health', 'preset']
    for rail in rails:
        rail_events = [e for e in block_events if e.rail_triggered == rail]
        total_blocks = len([e for e in rail_events if e.classification != BlockClassification.NA.value])
        fp_count = len([e for e in rail_events if e.classification == BlockClassification.FP.value])
        
        if total_blocks > 0:
            fpr = (fp_count / total_blocks) * 100
        else:
            fpr = 0.0
        
        metrics['per_rail'][rail] = {
            'total_blocks': total_blocks,
            'fp_count': fp_count,
            'tp_count': len([e for e in rail_events if e.classification == BlockClassification.TP.value]),
            'fpr': fpr
        }
    
    # Per-preset FPR
    for preset in presets:
        preset_events = [e for e in block_events if e.preset_used == preset]
        total_blocks = len([e for e in preset_events if e.classification != BlockClassification.NA.value])
        fp_count = len([e for e in preset_events if e.classification == BlockClassification.FP.value])
        
        if total_blocks > 0:
            fpr = (fp_count / total_blocks) * 100
        else:
            fpr = 0.0
        
        metrics['per_preset'][preset] = {
            'total_blocks': total_blocks,
            'fp_count': fp_count,
            'tp_count': len([e for e in preset_events if e.classification == BlockClassification.TP.value]),
            'fpr': fpr
        }
    
    # Global FPR
    total_blocks = len([e for e in block_events if e.classification != BlockClassification.NA.value])
    fp_count = len([e for e in block_events if e.classification == BlockClassification.FP.value])
    
    if total_blocks > 0:
        global_fpr = (fp_count / total_blocks) * 100
    else:
        global_fpr = 0.0
    
    metrics['global'] = {
        'total_blocks': total_blocks,
        'fp_count': fp_count,
        'tp_count': len([e for e in block_events if e.classification == BlockClassification.TP.value]),
        'fpr': global_fpr
    }
    
    return metrics


def generate_fp_summary(results: Dict[str, Any]) -> str:
    """
    Generate Markdown summary of FP test results
    
    Args:
        results: Results dict from run_fp_test()
        
    Returns:
        Markdown string
    """
    fpr_metrics = results['fpr_metrics']
    block_events = results['block_events']
    test_config = results['test_config']
    
    lines = [
        "# False Positive Rate (FPR) Test Results",
        "",
        f"**Date**: {results.get('timestamp', 'N/A')}",
        "",
        "## Test Configuration",
        "",
        f"- **Dataset**: `{test_config['data_path']}`",
        f"- **Symbols**: {', '.join(test_config['symbols'])}",
        f"- **Presets Tested**: {', '.join(test_config['presets'])}",
        f"- **Initial Equity**: ${test_config['initial_equity']:,.2f}",
        "",
        "## Summary Statistics",
        "",
        f"- **Total Block Events**: {len(block_events)}",
        f"- **False Positives**: {fpr_metrics['global']['fp_count']}",
        f"- **True Positives**: {fpr_metrics['global']['tp_count']}",
        f"- **Global FPR**: {fpr_metrics['global']['fpr']:.2f}%",
        "",
        "## Per-Rail FPR",
        "",
        "| Rail | Total Blocks | FP | TP | FPR |",
        "|------|-------------:|--:|--:|----:|"
    ]
    
    for rail, metrics in fpr_metrics['per_rail'].items():
        lines.append(
            f"| {rail.title()} | {metrics['total_blocks']} | "
            f"{metrics['fp_count']} | {metrics['tp_count']} | "
            f"{metrics['fpr']:.2f}% |"
        )
    
    lines.extend([
        "",
        "## Per-Preset FPR",
        "",
        "| Preset | Total Blocks | FP | TP | FPR |",
        "|--------|-------------:|--:|--:|----:|"
    ])
    
    for preset, metrics in fpr_metrics['per_preset'].items():
        lines.append(
            f"| {preset.title()} | {metrics['total_blocks']} | "
            f"{metrics['fp_count']} | {metrics['tp_count']} | "
            f"{metrics['fpr']:.2f}% |"
        )
    
    # Interpretation
    global_fpr = fpr_metrics['global']['fpr']
    if global_fpr < 5:
        interpretation = "✅ Excellent (institutional-grade)"
    elif global_fpr < 12:
        interpretation = "⚠️ Acceptable depending on preset"
    else:
        interpretation = "❌ Too restrictive; requires tuning"
    
    lines.extend([
        "",
        "## Interpretation",
        "",
        f"**Global FPR**: {global_fpr:.2f}%",
        "",
        f"**Assessment**: {interpretation}",
        "",
        "**Guidelines** (from FP_TEST_PROTOCOL.md):",
        "- FPR < 5% = Excellent (institutional-grade)",
        "- FPR between 5–12% = Acceptable depending on preset",
        "- FPR > 15% = Too restrictive; requires tuning",
        "",
        "---",
        "",
        f"*Report generated: {results.get('timestamp', 'N/A')}*"
    ])
    
    return "\n".join(lines)


def export_fp_results(
    results: Dict[str, Any],
    output_dir: str = "fp_test_results",
    filename_prefix: Optional[str] = None
):
    """
    Export FP test results to JSON, Markdown, and CSV
    
    Args:
        results: Results dict from run_fp_test()
        output_dir: Directory to save outputs
        filename_prefix: Optional prefix for filenames (e.g., "FP_SUMMARY_bull_2017_conservative")
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine filenames
    if filename_prefix:
        json_filename = f"{filename_prefix}.json"
        md_filename = f"{filename_prefix}.md"
        csv_filename = f"{filename_prefix}.csv"
    else:
        json_filename = "FP_TEST_SUMMARY.json"
        md_filename = "FP_TEST_SUMMARY.md"
        csv_filename = "FP_DETAILED_LOG.csv"
    
    # Export JSON
    json_path = os.path.join(output_dir, json_filename)
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Export Markdown
    md_path = os.path.join(output_dir, md_filename)
    md_content = generate_fp_summary(results)
    with open(md_path, 'w') as f:
        f.write(md_content)
    
    # Export CSV log
    csv_path = os.path.join(output_dir, csv_filename)
    if results['block_events']:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results['block_events'][0].keys())
            writer.writeheader()
            writer.writerows(results['block_events'])
    else:
        # Create empty CSV with headers if no block events
        block_event_fields = ['timestamp', 'asset', 'rail_triggered', 'preset_used', 'shield_action', 
                             'market_condition', 'classification', 'reason', 'price_at_block', 'equity_at_block']
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=block_event_fields)
            writer.writeheader()
        print(f"   - {csv_path} (empty - no block events)")
    
    print(f"✅ FP test results exported to {output_dir}/")
    print(f"   - {json_path}")
    print(f"   - {md_path}")
    print(f"   - {csv_path}")
    
    return json_path, md_path, csv_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run False Positive Rate test according to FP_TEST_PROTOCOL.md"
    )
    parser.add_argument("--data-path", "--dataset", required=True, help="Path to CSV data file")
    parser.add_argument("--symbols", nargs="+", default=None, help="Symbols to test (if None, uses 'close' column)")
    parser.add_argument("--preset", "--presets", nargs="+", default=["conservative"],
                       help="Preset(s) to test")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", "--output-dir", default="fp_test_results", help="Output directory")
    parser.add_argument("--filename-prefix", help="Prefix for output filenames (e.g., 'FP_SUMMARY_bull_2017_conservative')")
    
    args = parser.parse_args()
    
    # Handle both --preset and --presets
    presets = args.preset if isinstance(args.preset, list) else [args.preset]
    
    # Validate dataset first
    print(f"Validating dataset: {args.data_path}")
    try:
        validation_result = validate_dataset(args.data_path)
        print(f"✅ Dataset validation: {validation_result}")
    except ValueError as e:
        print(f"❌ Dataset validation failed: {e}")
        exit(1)
    
    # Run FP test
    print(f"\nRunning FP test with presets: {', '.join(presets)}")
    results = run_fp_test(
        data_path=args.data_path,
        symbols=args.symbols,
        presets=presets,
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    # Export results
    export_fp_results(results, args.output, args.filename_prefix)
    
    print("\n✅ FP test complete!")

