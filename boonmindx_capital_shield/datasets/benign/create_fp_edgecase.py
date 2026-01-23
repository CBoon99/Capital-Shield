"""
Create FP edgecase dataset with controlled dips that trigger safety rails

This dataset is mostly benign but includes 1-3 controlled dips that will
trigger drawdown rails, allowing us to test FP/TP classification logic.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_fp_edgecase_mild_dip(num_days: int = 250, start_price: float = 100.0):
    """
    Create edgecase dataset with mild dips that trigger safety rails
    
    Characteristics:
    - Mostly benign, upward or sideways movement
    - Include 1-3 controlled dips that cross CONSERVATIVE rail threshold
    - Still "benign" overall (not a full crash)
    - Drawdowns around 5-8% to trigger drawdown rail
    """
    dates = pd.date_range(start='2023-01-01', periods=num_days, freq='D')
    
    # Generate base returns with slight upward drift
    daily_return = 0.0002  # ~5% annual return
    volatility = 0.015  # 1.5% daily volatility
    
    returns = np.random.normal(daily_return, volatility, num_days)
    
    # Add controlled dips at specific points
    # Dip 1: Around day 50-60 (5% drawdown)
    dip1_start = 50
    dip1_duration = 8
    for i in range(dip1_start, min(dip1_start + dip1_duration, num_days)):
        returns[i] = -0.008  # -0.8% per day for 8 days ≈ 6.4% total
    
    # Dip 2: Around day 120-130 (6% drawdown)
    dip2_start = 120
    dip2_duration = 10
    for i in range(dip2_start, min(dip2_start + dip2_duration, num_days)):
        returns[i] = -0.006  # -0.6% per day for 10 days ≈ 6% total
    
    # Dip 3: Around day 200-210 (7% drawdown)
    dip3_start = 200
    dip3_duration = 12
    for i in range(dip3_start, min(dip3_start + dip3_duration, num_days)):
        returns[i] = -0.006  # -0.6% per day for 12 days ≈ 7.2% total
    
    # Generate prices
    prices = [start_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Create OHLCV data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # High/Low within 1-2% of close
        daily_range = close * np.random.uniform(0.01, 0.02)
        high = close + daily_range * np.random.uniform(0.3, 0.7)
        low = close - daily_range * np.random.uniform(0.3, 0.7)
        open_price = close + np.random.uniform(-0.01, 0.01) * close
        
        # Volume (random but consistent)
        volume = np.random.uniform(1000000, 5000000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # Set seed for reproducibility
    np.random.seed(123)
    
    print("Creating fp_edgecase_mild_dip.csv...")
    df_edgecase = create_fp_edgecase_mild_dip(num_days=250)
    df_edgecase.to_csv('datasets/benign/fp_edgecase_mild_dip.csv', index=False)
    print(f"  Created {len(df_edgecase)} rows")
    print(f"  Price range: ${df_edgecase['close'].min():.2f} - ${df_edgecase['close'].max():.2f}")
    print(f"  Total return: {(df_edgecase['close'].iloc[-1] / df_edgecase['close'].iloc[0] - 1) * 100:.2f}%")
    
    # Calculate drawdowns
    peak = df_edgecase['close'].expanding().max()
    drawdown = (df_edgecase['close'] - peak) / peak
    max_drawdown = drawdown.min()
    print(f"  Max drawdown: {max_drawdown * 100:.2f}%")
    
    print("\n✅ Edgecase dataset created successfully!")
    print("   This dataset includes controlled dips that should trigger drawdown rails.")


