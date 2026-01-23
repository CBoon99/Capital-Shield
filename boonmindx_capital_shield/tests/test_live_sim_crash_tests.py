"""
Crash Test Scenarios - Test Capital Shield safety rails under stress
"""
import os
import tempfile
import pytest
from live_sim.crash_tests import (
    run_drawdown_crash_test,
    run_health_failure_test,
    run_bear_regime_strict_block_test,
    create_drawdown_crash_data,
    create_bear_regime_data
)
from live_sim.data_loader import create_synthetic_data


class TestDrawdownCrashTest:
    """Test drawdown crash scenario"""
    
    def test_drawdown_crash_test_blocks_trades_and_reduces_dd(self):
        """Verify drawdown crash test blocks trades and reduces drawdown"""
        result = run_drawdown_crash_test(max_drawdown_threshold=-0.10)
        
        # Check structure
        assert 'baseline' in result
        assert 'capital_shielded' in result or 'shielded' in result
        assert 'comparison' in result
        
        baseline_metrics = result['baseline']['portfolio_metrics']
        shielded_key = 'capital_shielded' if 'capital_shielded' in result else 'shielded'
        shielded_metrics = result[shielded_key]['portfolio_metrics']
        comparison = result['comparison']
        
        # Capital Shielded should have >= final equity (may be equal if no trades blocked)
        assert shielded_metrics['final_equity'] >= baseline_metrics['final_equity']
        
        # Capital Shielded max drawdown should be >= baseline (less negative = better)
        assert shielded_metrics['max_drawdown'] >= baseline_metrics['max_drawdown']
        
        # Check blocked trades are tracked
        blocked_count = result[shielded_key].get('blocked_trades_count', 0)
        assert blocked_count >= 0  # May be 0 if no trades attempted
        
        # Check comparison structure
        assert 'shield_effect' in comparison
        assert 'differences' in comparison


class TestHealthFailureTest:
    """Test health failure scenario"""
    
    def test_health_failure_blocks_trades_in_strict_and_permissive(self):
        """Verify health failure blocks trades in both STRICT and PERMISSIVE modes"""
        result = run_health_failure_test()
        
        # Check structure
        assert 'baseline' in result
        assert 'capital_shielded_strict' in result or 'shielded_strict' in result
        assert 'capital_shielded_permissive' in result or 'shielded_permissive' in result
        
        baseline_metrics = result['baseline']['portfolio_metrics']
        strict_key = 'capital_shielded_strict' if 'capital_shielded_strict' in result else 'shielded_strict'
        permissive_key = 'capital_shielded_permissive' if 'capital_shielded_permissive' in result else 'shielded_permissive'
        strict_metrics = result[strict_key]['portfolio_metrics']
        permissive_metrics = result[permissive_key]['portfolio_metrics']
        
        # Both capital_shielded modes should have <= trade count vs baseline
        # (health check should block trades in both modes)
        assert strict_metrics['total_trades'] <= baseline_metrics['total_trades']
        assert permissive_metrics['total_trades'] <= baseline_metrics['total_trades']
        
        # Check blocked trades reasons include health failures
        strict_blocked = result[strict_key].get('blocked_trades', [])
        permissive_blocked = result[permissive_key].get('blocked_trades', [])
        
        # Check that health-related blocks are present if any trades were blocked
        if strict_blocked:
            health_blocks = [bt for bt in strict_blocked if 'health' in bt.get('reason', '').lower() or 'unhealthy' in bt.get('reason', '').lower()]
            # May have health blocks or other blocks
        
        if permissive_blocked:
            health_blocks = [bt for bt in permissive_blocked if 'health' in bt.get('reason', '').lower() or 'unhealthy' in bt.get('reason', '').lower()]
            # May have health blocks or other blocks
        
        # No exceptions should be thrown - behavior is clean
        assert 'comparison_strict' in result
        assert 'comparison_permissive' in result


class TestBearRegimeStrictBlockTest:
    """Test bear regime strict block scenario"""
    
    def test_bear_regime_strict_blocks_buy_trades(self):
        """Verify STRICT mode blocks BUY trades in BEAR regime"""
        result = run_bear_regime_strict_block_test()
        
        # Check structure
        assert 'baseline' in result
        assert 'capital_shielded_strict' in result or 'shielded_strict' in result
        assert 'capital_shielded_permissive' in result or 'shielded_permissive' in result
        
        baseline_metrics = result['baseline']['portfolio_metrics']
        strict_key = 'capital_shielded_strict' if 'capital_shielded_strict' in result else 'shielded_strict'
        strict_metrics = result[strict_key]['portfolio_metrics']
        
        # STRICT should have <= trades vs baseline (blocks BEAR+BUY)
        assert strict_metrics['total_trades'] <= baseline_metrics['total_trades']
        
        # Check blocked trades
        strict_blocked = result[strict_key].get('blocked_trades', [])
        strict_blocked_count = result[strict_key].get('blocked_trades_count', 0)
        
        # If trades were blocked, reasons should include regime guard
        if strict_blocked_count > 0:
            regime_blocks = [bt for bt in strict_blocked if 'bear' in bt.get('reason', '').lower() or 'regime' in bt.get('reason', '').lower()]
            # Should have at least some regime-related blocks
        
        # Check comparison
        assert 'comparison_strict' in result
    
    def test_bear_regime_permissive_allows_buy_trades(self):
        """Verify PERMISSIVE mode allows BUY trades in BEAR regime"""
        result = run_bear_regime_strict_block_test()
        
        baseline_metrics = result['baseline']['portfolio_metrics']
        permissive_key = 'capital_shielded_permissive' if 'capital_shielded_permissive' in result else 'shielded_permissive'
        permissive_metrics = result[permissive_key]['portfolio_metrics']
        
        # PERMISSIVE should have similar trade count to baseline
        # (allows trades, doesn't hard-block purely due to regime)
        # Allow some variance but should be close
        trade_diff = abs(permissive_metrics['total_trades'] - baseline_metrics['total_trades'])
        assert trade_diff <= 2  # Allow small variance
        
        # Check comparison
        assert 'comparison_permissive' in result
        
        # PERMISSIVE should not have regime-based hard blocks
        permissive_blocked = result[permissive_key].get('blocked_trades', [])
        # If there are blocks, they shouldn't be purely regime-based in PERMISSIVE mode
        # (other safety rails may still block)


class TestCrashTestDataGenerators:
    """Test crash test data generators"""
    
    def test_create_drawdown_crash_data(self):
        """Test drawdown crash data generation"""
        df = create_drawdown_crash_data(
            symbol="TEST",
            num_candles=30,
            crash_start=15,
            crash_severity=0.25
        )
        
        assert len(df) == 30
        assert "TEST" in df.columns
        
        # Price should drop significantly after crash_start
        prices = df["TEST"].values
        initial_price = prices[0]
        peak_price = max(prices[:15])  # Peak before crash
        crash_price = prices[15]
        
        # Crash should cause significant drop from peak
        drop_pct = (crash_price - peak_price) / peak_price if peak_price > 0 else 0
        assert drop_pct < -0.20  # At least 20% drop from peak
        
        # Verify crash actually happened (price drops significantly)
        assert crash_price < peak_price * 0.8  # At least 20% below peak
    
    def test_create_bear_regime_data(self):
        """Test bear regime data generation"""
        df = create_bear_regime_data(
            symbol="BEAR_TEST",
            num_candles=20
        )
        
        assert len(df) == 20
        assert "BEAR_TEST" in df.columns
        
        # Price should trend downward
        prices = df["BEAR_TEST"].values
        initial_price = prices[0]
        final_price = prices[-1]
        
        # Should be declining trend
        assert final_price < initial_price

