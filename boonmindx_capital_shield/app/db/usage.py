"""
Usage Tracking Database Module

Tracks API calls per user per day for tier enforcement and overage billing.
"""
import sqlite3
import os
from datetime import datetime, date
from typing import Optional, Dict, List
from contextlib import contextmanager
from app.core.config import DATABASE_URL


def get_db_path() -> str:
    """Get database path from DATABASE_URL"""
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "")
    # For PostgreSQL, we'd use a connection pool
    # For now, default to SQLite
    return "capital_shield.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize database tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # API usage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                call_date DATE NOT NULL,
                call_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(api_key, endpoint, call_date)
            )
        """)
        
        # User subscriptions table (linked to Stripe)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT UNIQUE NOT NULL,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                tier TEXT NOT NULL,
                status TEXT NOT NULL,
                billing_cycle TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Overage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                billing_period_start DATE NOT NULL,
                billing_period_end DATE NOT NULL,
                overage_calls INTEGER DEFAULT 0,
                overage_amount_gbp REAL DEFAULT 0.0,
                billed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_usage_key_date 
            ON api_usage(api_key, call_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_subscriptions_api_key 
            ON subscriptions(api_key)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_overages_api_key_period 
            ON overages(api_key, billing_period_start)
        """)


def track_api_call(api_key: str, endpoint: str) -> None:
    """
    Track an API call for usage monitoring and billing
    
    Args:
        api_key: The API key making the call
        endpoint: The endpoint being called (e.g., '/api/v1/filter')
    """
    today = date.today()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_usage (api_key, endpoint, call_date, call_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(api_key, endpoint, call_date) 
            DO UPDATE SET 
                call_count = call_count + 1,
                updated_at = CURRENT_TIMESTAMP
        """, (api_key, endpoint, today))


def get_daily_usage(api_key: str, target_date: Optional[date] = None) -> int:
    """
    Get total API calls for a given API key on a specific date
    
    Args:
        api_key: The API key to check
        target_date: Date to check (defaults to today)
    
    Returns:
        Total number of API calls for that day
    """
    if target_date is None:
        target_date = date.today()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(call_count) as total
            FROM api_usage
            WHERE api_key = ? AND call_date = ?
        """, (api_key, target_date))
        
        result = cursor.fetchone()
        return result['total'] if result and result['total'] else 0


def get_monthly_usage(api_key: str, year: int, month: int) -> Dict[str, int]:
    """
    Get monthly usage statistics for an API key
    
    Args:
        api_key: The API key to check
        year: Year
        month: Month (1-12)
    
    Returns:
        Dictionary with 'total_calls', 'daily_average', and 'peak_day' stats
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SUM(call_count) as total_calls,
                AVG(call_count) as daily_avg,
                MAX(call_count) as peak_day_calls
            FROM api_usage
            WHERE api_key = ? 
            AND strftime('%Y', call_date) = ?
            AND strftime('%m', call_date) = ?
        """, (api_key, str(year), f"{month:02d}"))
        
        result = cursor.fetchone()
        if result and result['total_calls']:
            return {
                'total_calls': result['total_calls'],
                'daily_average': int(result['daily_avg'] or 0),
                'peak_day': result['peak_day_calls'] or 0
            }
        return {'total_calls': 0, 'daily_average': 0, 'peak_day': 0}


def calculate_overages(api_key: str, tier: str, billing_period_start: date, 
                       billing_period_end: date) -> Dict[str, float]:
    """
    Calculate overage charges for a billing period
    
    Args:
        api_key: The API key to calculate overages for
        tier: The tier name (starter, professional, etc.)
        billing_period_start: Start date of billing period
        billing_period_end: End date of billing period
    
    Returns:
        Dictionary with 'overage_calls' and 'overage_amount_gbp'
    """
    from app.core.config import TIER_LIMITS
    
    tier_config = TIER_LIMITS.get(tier, {})
    daily_limit = tier_config.get('daily_calls', 0)
    overage_rate = tier_config.get('overage_rate_gbp', 0.0)
    
    if daily_limit == float('inf') or overage_rate == 0.0:
        return {'overage_calls': 0, 'overage_amount_gbp': 0.0}
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT call_date, SUM(call_count) as daily_calls
            FROM api_usage
            WHERE api_key = ? 
            AND call_date >= ? 
            AND call_date <= ?
            GROUP BY call_date
        """, (api_key, billing_period_start, billing_period_end))
        
        total_overage_calls = 0
        for row in cursor.fetchall():
            daily_calls = row['daily_calls']
            if daily_calls > daily_limit:
                total_overage_calls += (daily_calls - daily_limit)
        
        overage_amount = total_overage_calls * overage_rate
        
        return {
            'overage_calls': total_overage_calls,
            'overage_amount_gbp': round(overage_amount, 4)
        }


def record_overage(api_key: str, billing_period_start: date, 
                  billing_period_end: date, overage_calls: int, 
                  overage_amount_gbp: float) -> None:
    """
    Record overage charges for a billing period
    
    Args:
        api_key: The API key
        billing_period_start: Start date of billing period
        billing_period_end: End date of billing period
        overage_calls: Number of overage calls
        overage_amount_gbp: Amount in GBP
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO overages 
            (api_key, billing_period_start, billing_period_end, 
             overage_calls, overage_amount_gbp, billed)
            VALUES (?, ?, ?, ?, ?, FALSE)
            ON CONFLICT DO NOTHING
        """, (api_key, billing_period_start, billing_period_end, 
              overage_calls, overage_amount_gbp))


def get_usage_stats(api_key: str) -> Dict:
    """
    Get comprehensive usage statistics for an API key
    
    Args:
        api_key: The API key to get stats for
    
    Returns:
        Dictionary with usage statistics
    """
    today = date.today()
    daily_usage = get_daily_usage(api_key, today)
    
    # Get monthly stats for current month
    monthly_stats = get_monthly_usage(api_key, today.year, today.month)
    
    return {
        'daily_usage': daily_usage,
        'monthly_total': monthly_stats['total_calls'],
        'monthly_average': monthly_stats['daily_average'],
        'peak_day': monthly_stats['peak_day']
    }


# Initialize database on import
init_database()
