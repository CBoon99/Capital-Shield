"""
Data Loader for Live Simulation

Loads historical OHLCV data from CSV files (same format as BearHunter backtests)
"""
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
import os


def load_historical_data(
    symbols: List[str],
    data_path: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    timeframe: str = "1d"
) -> pd.DataFrame:
    """
    Load historical OHLCV data from CSV file
    
    Args:
        symbols: List of symbol names to load
        data_path: Path to CSV file (format: date, SYMBOL_1, SYMBOL_2, ...)
        start_date: Start date filter (YYYY-MM-DD) or None for all
        end_date: End date filter (YYYY-MM-DD) or None for all
        timeframe: Candle timeframe (e.g., "1d", "1h") - currently only "1d" supported
        
    Returns:
        DataFrame with MultiIndex (date, symbol) and columns: open, high, low, close, volume
        Or simpler format: date index, columns per symbol (close prices)
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    # Read CSV
    df = pd.read_csv(data_path)
    
    # Parse date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    elif df.index.name == 'date' or df.index.dtype == 'datetime64[ns]':
        # Already has date index
        pass
    else:
        # Try to parse first column as date
        df.index = pd.to_datetime(df.index)
    
    # Filter by date range
    if start_date:
        start = pd.to_datetime(start_date)
        df = df[df.index >= start]
    if end_date:
        end = pd.to_datetime(end_date)
        df = df[df.index <= end]
    
    # Filter columns to requested symbols
    available_symbols = [col for col in df.columns if col in symbols]
    if not available_symbols:
        raise ValueError(f"None of the requested symbols {symbols} found in data file")
    
    df = df[available_symbols]
    
    # Sort by date
    df.sort_index(inplace=True)
    
    return df


def get_price_history(
    df: pd.DataFrame,
    symbol: str,
    current_date: pd.Timestamp,
    lookback_periods: int = 100
) -> Tuple[List[float], Optional[List[float]]]:
    """
    Extract price history for a symbol up to current_date
    
    Args:
        df: DataFrame with historical data
        symbol: Symbol name
        current_date: Current date (inclusive)
        lookback_periods: Maximum number of periods to look back
        
    Returns:
        Tuple of (close_prices, volumes)
        close_prices: List of close prices (oldest to newest)
        volumes: List of volumes (or None if not available)
    """
    if symbol not in df.columns:
        return [], None
    
    # Filter data up to current_date
    mask = df.index <= current_date
    symbol_data = df.loc[mask, symbol]
    
    # Take last lookback_periods
    symbol_data = symbol_data.tail(lookback_periods)
    
    # Convert to lists (oldest to newest)
    close_prices = symbol_data.dropna().tolist()
    
    # Try to get volumes (if available in separate columns or same format)
    volumes = None
    # For now, volumes are not in the standard format, return None
    
    return close_prices, volumes


def create_synthetic_data(
    symbols: List[str],
    num_candles: int = 100,
    start_price: float = 100.0,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    Create synthetic OHLCV data for testing
    
    Args:
        symbols: List of symbol names
        num_candles: Number of candles to generate
        start_price: Starting price
        volatility: Daily volatility (std dev of returns)
        
    Returns:
        DataFrame with date index and columns per symbol (close prices)
    """
    dates = pd.date_range(start='2024-01-01', periods=num_candles, freq='D')
    
    data = {}
    for symbol in symbols:
        # Generate random walk
        returns = np.random.normal(0, volatility, num_candles)
        prices = [start_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        data[symbol] = prices
    
    df = pd.DataFrame(data, index=dates)
    return df


def validate_data(df: pd.DataFrame, symbols: List[str]) -> Dict[str, bool]:
    """
    Validate data quality for symbols
    
    Returns:
        Dict mapping symbol -> is_valid (bool)
    """
    validation = {}
    for symbol in symbols:
        if symbol not in df.columns:
            validation[symbol] = False
            continue
        
        symbol_data = df[symbol].dropna()
        
        # Check for sufficient data
        has_data = len(symbol_data) > 0
        
        # Check for reasonable values (no negatives, no zeros)
        has_valid_values = (symbol_data > 0).all() if has_data else False
        
        validation[symbol] = has_data and has_valid_values
    
    return validation

