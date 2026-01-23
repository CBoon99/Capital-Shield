"""
Create synthetic benign market datasets for FP testing

Generates clean bull market datasets with:
- Steady upward drift
- No extreme drawdowns
- Volatility within normal bounds
- 200+ trading days
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_bull_2017_synthetic(num_days: int = 250, start_price: float = 100.0):
    """
    Create synthetic bull market dataset (2017-style)
    
    Characteristics:
    - Strong uptrend (15-20% annual return)
    - Low volatility (1-2% daily)
    - Occasional small pullbacks (2-3%)
    - No extreme drawdowns
    """
    dates = pd.date_range(start='2017-01-01', periods=num_days, freq='D')
    
    # Generate returns with upward drift
    daily_return = 0.0006  # ~15% annual return
    volatility = 0.015  # 1.5% daily volatility
    
    returns = np.random.normal(daily_return, volatility, num_days)
    
    # Add occasional small pullbacks (every 30-40 days)
    for i in range(30, num_days, 35):
        if i < num_days:
            returns[i:i+3] -= 0.02  # Small 2% pullback
    
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


def create_mild_bull_2020_synthetic(num_days: int = 250, start_price: float = 100.0):
    """
    Create synthetic mild bull market dataset (2020-style recovery)
    
    Characteristics:
    - Moderate uptrend (8-12% annual return)
    - Moderate volatility (2-3% daily)
    - More frequent small pullbacks
    - Still no extreme drawdowns
    """
    dates = pd.date_range(start='2020-06-01', periods=num_days, freq='D')
    
    # Generate returns with moderate upward drift
    daily_return = 0.0003  # ~8% annual return
    volatility = 0.025  # 2.5% daily volatility
    
    returns = np.random.normal(daily_return, volatility, num_days)
    
    # Add more frequent small pullbacks (every 20-25 days)
    for i in range(20, num_days, 22):
        if i < num_days:
            returns[i:i+2] -= 0.015  # Small 1.5% pullback
    
    # Generate prices
    prices = [start_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Create OHLCV data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # High/Low within 2-3% of close
        daily_range = close * np.random.uniform(0.015, 0.03)
        high = close + daily_range * np.random.uniform(0.3, 0.7)
        low = close - daily_range * np.random.uniform(0.3, 0.7)
        open_price = close + np.random.uniform(-0.015, 0.015) * close
        
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
    np.random.seed(42)
    
    # Create datasets
    print("Creating bull_2017_synthetic.csv...")
    df_2017 = create_bull_2017_synthetic(num_days=250)
    df_2017.to_csv('datasets/benign/bull_2017_synthetic.csv', index=False)
    print(f"  Created {len(df_2017)} rows")
    print(f"  Price range: ${df_2017['close'].min():.2f} - ${df_2017['close'].max():.2f}")
    print(f"  Total return: {(df_2017['close'].iloc[-1] / df_2017['close'].iloc[0] - 1) * 100:.2f}%")
    
    print("\nCreating mild_bull_2020_synthetic.csv...")
    df_2020 = create_mild_bull_2020_synthetic(num_days=250)
    df_2020.to_csv('datasets/benign/mild_bull_2020_synthetic.csv', index=False)
    print(f"  Created {len(df_2020)} rows")
    print(f"  Price range: ${df_2020['close'].min():.2f} - ${df_2020['close'].max():.2f}")
    print(f"  Total return: {(df_2020['close'].iloc[-1] / df_2020['close'].iloc[0] - 1) * 100:.2f}%")
    
    print("\n✅ Datasets created successfully!")


