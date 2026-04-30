"""
Quick Demo Runner

One-command demo that runs a complete end-to-end validation
and produces investor-grade reports.
"""
import os
import sys
from pathlib import Path
from .data_loader import create_synthetic_data
from .multi_validation import run_multi_validation
from .reporting import generate_investor_summary


def main():
    """
    Run Shield API demo validation
    
    Creates synthetic data, runs multi-dataset validation,
    and generates investor reports.
    """
    print("=" * 80)
    print("SHIELD API QUICK DEMO")
    print("=" * 80)
    print()
    print("This demo will:")
    print("  1. Generate synthetic test data")
    print("  2. Run baseline vs Shielded (Conservative/Balanced/Aggressive)")
    print("  3. Generate JSON summary and investor report")
    print()
    print("=" * 80)
    print()
    
    # Create synthetic dataset
    print("Generating synthetic test data...")
    symbols = ["DEMO_BEAR", "DEMO_BULL", "DEMO_SIDEWAYS"]
    df = create_synthetic_data(symbols, num_candles=50)
    
    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name)
        demo_data_path = f.name
    
    try:
        # Run multi-dataset validation
        print(f"Running validation on {len(symbols)} symbols...")
        print()
        
        summary = run_multi_validation(
            datasets=[demo_data_path],
            symbols=symbols,
            presets=["conservative", "balanced", "aggressive"],
            engine_mode="MOCK",  # Use MOCK for deterministic demo
            initial_equity=100000.0
        )
        
        # Generate outputs
        output_dir = Path.cwd()
        json_path = output_dir / "demo_multi_validation_summary.json"
        markdown_path = output_dir / "DEMO_INVESTOR_VALIDATION_REPORT.md"
        
        # Save JSON summary
        import json
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Generate and save Markdown report
        markdown_report = generate_investor_summary(summary)
        with open(markdown_path, 'w') as f:
            f.write(markdown_report)
        
        # Print success message
        print()
        print("=" * 80)
        print("✅ SHIELD DEMO COMPLETE")
        print("=" * 80)
        print()
        print("Generated files:")
        print(f"  📄 JSON summary: {json_path}")
        print(f"  📊 Investor report: {markdown_path}")
        print()
        print("Next steps:")
        print(f"  1. Open {markdown_path} to see how Shield behaves vs baseline")
        print("     across Conservative/Balanced/Aggressive presets")
        print("  2. Review the JSON summary for detailed metrics")
        print("  3. Run your own validation:")
        print("     python -m live_sim.multi_validation \\")
        print("       --datasets your_data.csv \\")
        print("       --symbols YOUR_SYM1 YOUR_SYM2 \\")
        print("       --presets conservative balanced aggressive \\")
        print("       --output-json your_validation.json \\")
        print("       --output-markdown YOUR_REPORT.md")
        print()
        print("=" * 80)
        
    finally:
        # Clean up temp file
        if os.path.exists(demo_data_path):
            os.unlink(demo_data_path)


if __name__ == "__main__":
    main()

