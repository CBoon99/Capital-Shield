"""
CoinGecko Client for Capital Shield Shadow-Live Mode

Fetches live and historical cryptocurrency price data from CoinGecko's free API
and normalizes it into the internal OHLCV format used by the Monte Carlo and
FP/OC/Execution harnesses.

API Docs: https://www.coingecko.com/en/api/documentation
Rate Limits: 10-50 calls/minute on free tier (we respect this with polling delays)
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests


class CoinGeckoClient:
    """
    Client for fetching cryptocurrency data from CoinGecko API.
    
    Attributes:
        base_url: CoinGecko API base URL
        session: Persistent HTTP session for connection pooling
        last_request_time: Timestamp of last API call (for rate limiting)
        min_request_interval: Minimum seconds between requests (default 1.2s = ~50/min)
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3/"
    
    def __init__(self, min_request_interval: float = 1.2):
        """
        Initialize CoinGecko client.
        
        Args:
            min_request_interval: Minimum seconds between API calls (default 1.2)
        """
        self.base_url = self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "BoonMindX-Capital-Shield/1.0"
        })
        self.last_request_time = 0.0
        self.min_request_interval = min_request_interval
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a rate-limited GET request to CoinGecko API.
        
        Args:
            endpoint: API endpoint (e.g., "coins/bitcoin/market_chart")
            params: Query parameters
        
        Returns:
            JSON response as dictionary
        
        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()
        url = urljoin(self.base_url, endpoint)
        response = self.session.get(url, params=params or {})
        response.raise_for_status()
        return response.json()
    
    def get_current_price(self, coin_id: str, vs_currency: str = "usd") -> float:
        """
        Get current price for a single coin.
        
        Args:
            coin_id: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
            vs_currency: Quote currency (default "usd")
        
        Returns:
            Current price as float
        
        Example:
            >>> client = CoinGeckoClient()
            >>> price = client.get_current_price("bitcoin")
            >>> print(f"BTC: ${price:,.2f}")
        """
        data = self._get(
            "simple/price",
            params={"ids": coin_id, "vs_currencies": vs_currency}
        )
        return float(data[coin_id][vs_currency])
    
    def get_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 30,
        interval: str = "daily"
    ) -> Dict[str, List[List[float]]]:
        """
        Get historical market data (price, volume, market cap).
        
        Args:
            coin_id: CoinGecko coin ID
            vs_currency: Quote currency (default "usd")
            days: Number of days of history (1-365 or "max")
            interval: Data granularity ("daily" or "hourly" if days <= 90)
        
        Returns:
            Dictionary with keys: "prices", "market_caps", "total_volumes"
            Each value is a list of [timestamp_ms, value] pairs
        
        Example:
            >>> client = CoinGeckoClient()
            >>> data = client.get_market_chart("bitcoin", days=7)
            >>> prices = data["prices"]
            >>> print(f"Fetched {len(prices)} price points")
        """
        return self._get(
            f"coins/{coin_id}/market_chart",
            params={"vs_currency": vs_currency, "days": days, "interval": interval}
        )
    
    def to_ohlcv(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Fetch market data and convert to internal OHLCV format.
        
        Args:
            coin_id: CoinGecko coin ID
            vs_currency: Quote currency
            days: Number of days of history
        
        Returns:
            Dictionary with:
                - asset: str (coin_id)
                - timestamps: List[int] (Unix timestamps in seconds)
                - prices: List[float] (close prices, approximated from CoinGecko data)
                - volumes: List[float]
                - open: List[float] (approximated as previous close)
                - high: List[float] (approximated as price + small buffer)
                - low: List[float] (approximated as price - small buffer)
        
        Note:
            CoinGecko free API does not provide true OHLC data, only periodic
            snapshots. We approximate OHLC from price/volume time series.
        """
        data = self.get_market_chart(coin_id, vs_currency, days)
        
        prices_raw = data.get("prices", [])
        volumes_raw = data.get("total_volumes", [])
        
        if not prices_raw:
            return {
                "asset": coin_id,
                "timestamps": [],
                "prices": [],
                "volumes": [],
                "open": [],
                "high": [],
                "low": [],
            }
        
        timestamps = [int(p[0] / 1000) for p in prices_raw]  # Convert ms to seconds
        prices = [p[1] for p in prices_raw]
        volumes = [v[1] for v in volumes_raw] if volumes_raw else [0.0] * len(prices)
        
        # Approximate OHLC from price snapshots
        # Open = previous close (or current for first)
        open_prices = [prices[0]] + prices[:-1]
        
        # High/Low = price +/- 1% (crude approximation for volatility)
        high_prices = [p * 1.01 for p in prices]
        low_prices = [p * 0.99 for p in prices]
        
        return {
            "asset": coin_id,
            "timestamps": timestamps,
            "prices": prices,  # Close prices
            "volumes": volumes,
            "open": open_prices,
            "high": high_prices,
            "low": low_prices,
        }
    
    def get_watchlist_ohlcv(
        self,
        coin_ids: List[str],
        vs_currency: str = "usd",
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data for multiple coins.
        
        Args:
            coin_ids: List of CoinGecko coin IDs
            vs_currency: Quote currency
            days: Number of days of history
        
        Returns:
            List of OHLCV dictionaries (one per coin)
        
        Example:
            >>> client = CoinGeckoClient()
            >>> watchlist = ["bitcoin", "ethereum", "cardano"]
            >>> ohlcv_data = client.get_watchlist_ohlcv(watchlist, days=7)
            >>> for data in ohlcv_data:
            ...     print(f"{data['asset']}: {len(data['prices'])} candles")
        """
        results = []
        for coin_id in coin_ids:
            try:
                ohlcv = self.to_ohlcv(coin_id, vs_currency, days)
                results.append(ohlcv)
            except Exception as e:
                print(f"[CoinGecko] Failed to fetch {coin_id}: {e}")
                # Continue with other coins even if one fails
        return results


def get_default_watchlist() -> List[str]:
    """
    Return a default watchlist of major cryptocurrencies.
    
    Returns:
        List of CoinGecko coin IDs
    """
    return [
        "bitcoin",
        "ethereum",
        "cardano",
        "solana",
        "polkadot",
    ]


if __name__ == "__main__":
    # Quick test
    client = CoinGeckoClient()
    watchlist = get_default_watchlist()
    
    print(f"[CoinGecko] Fetching data for {len(watchlist)} coins...")
    ohlcv_data = client.get_watchlist_ohlcv(watchlist, days=7)
    
    for data in ohlcv_data:
        print(f"  {data['asset']}: {len(data['prices'])} candles, "
              f"latest price: ${data['prices'][-1]:,.2f}")

