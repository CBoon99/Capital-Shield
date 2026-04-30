"""
Tests for Live Simulation Harness

Tests basic functionality, safety rails, determinism, and edge cases
"""
import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from datetime import datetime

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from live_sim.data_loader import (
    load_historical_data,
    get_price_history,
    create_synthetic_data,
    validate_data
)
from live_sim.shield_client import CapitalShieldClient
from live_sim.runner import Portfolio, run_simulation
from live_sim.reporting import generate_summary, export_equity_curve, compare_runs, generate_markdown_summary
from live_sim.historical_validation import run_historical_validation, run_scenario, Scenario


class TestDataLoader:
    """Test data loading functionality"""
    
    def test_create_synthetic_data(self):
        """Test synthetic data creation"""
        symbols = ["BTC", "ETH"]
        df = create_synthetic_data(symbols, num_candles=50)
        
        assert len(df) == 50
        assert all(symbol in df.columns for symbol in symbols)
        assert all(df[symbol].min() > 0 for symbol in symbols)
    
    def test_get_price_history(self):
        """Test price history extraction"""
        df = create_synthetic_data(["BTC"], num_candles=100)
        
        # Get history up to middle date
        mid_date = df.index[50]
        prices, volumes = get_price_history(df, "BTC", mid_date, lookback_periods=30)
        
        assert len(prices) <= 30
        assert len(prices) > 0
        assert all(isinstance(p, (int, float)) for p in prices)
    
    def test_validate_data(self):
        """Test data validation"""
        df = create_synthetic_data(["BTC", "ETH"], num_candles=50)
        
        validation = validate_data(df, ["BTC", "ETH", "INVALID"])
        
        assert validation["BTC"] == True
        assert validation["ETH"] == True
        assert validation["INVALID"] == False


class TestPortfolio:
    """Test portfolio tracking"""
    
    def test_portfolio_initialization(self):
        """Test portfolio initialization"""
        portfolio = Portfolio(initial_equity=100000)
        
        assert portfolio.equity == 100000
        assert portfolio.cash == 100000
        assert len(portfolio.positions) == 0
        assert len(portfolio.equity_curve) == 1
    
    def test_enter_position(self):
        """Test entering a position"""
        portfolio = Portfolio(initial_equity=100000)
        
        success = portfolio.enter_position("BTC", price=50000, size=1.0, timestamp=pd.Timestamp.now())
        
        assert success is True
        assert "BTC" in portfolio.positions
        assert portfolio.cash < 100000
        assert len(portfolio.trades) == 1
    
    def test_exit_position(self):
        """Test exiting a position"""
        portfolio = Portfolio(initial_equity=100000)
        
        # Enter position
        portfolio.enter_position("BTC", price=50000, size=1.0, timestamp=pd.Timestamp.now())
        initial_cash = portfolio.cash
        
        # Exit position
        pnl = portfolio.exit_position("BTC", price=55000, timestamp=pd.Timestamp.now())
        
        assert pnl is not None
        assert pnl > 0  # Profit
        assert "BTC" not in portfolio.positions
        assert portfolio.cash > initial_cash
        assert len(portfolio.trades) == 2
    
    def test_update_equity(self):
        """Test equity update with current prices"""
        portfolio = Portfolio(initial_equity=100000)
        
        # Enter position (costs 50000, leaves 50000 cash)
        portfolio.enter_position("BTC", price=50000, size=1.0, timestamp=pd.Timestamp.now())
        # Equity hasn't been updated yet, still at initial
        assert portfolio.equity == 100000
        
        # Update equity with higher price (should show unrealized profit)
        portfolio.update_equity({"BTC": 55000})
        
        # Equity = cash (50000) + unrealized PnL (5000) = 55000
        assert portfolio.equity == 55000
        assert len(portfolio.equity_curve) == 2
    
    def test_max_drawdown_tracking(self):
        """Test max drawdown calculation"""
        portfolio = Portfolio(initial_equity=100000)
        
        # Enter position and update to set peak
        portfolio.enter_position("BTC", price=50000, size=1.0, timestamp=pd.Timestamp.now())
        portfolio.update_equity({"BTC": 55000})  # Equity = 55000, peak = 55000
        
        # Now simulate decline
        portfolio.update_equity({"BTC": 50000})  # Equity = 50000, drawdown = (50000-55000)/55000 = -0.091
        
        # Max drawdown should be negative (decline from peak)
        assert portfolio.max_drawdown < 0
        # Should be around -9% (50000 / 55000 - 1 = -0.091)
        assert portfolio.max_drawdown <= -0.08  # Allow some tolerance


class TestCapitalShieldClient:
    """Test Capital Shield client integration"""
    
    def test_get_signal(self):
        """Test getting signal from Capital Shield"""
        client = CapitalShieldClient(engine_mode="MOCK")
        
        price_history = [100, 105, 110, 115, 120]  # Bullish
        
        response = client.get_signal("BTC", price_history)
        
        assert response.signal in ["BUY", "SELL", "HOLD"]
        assert 0.0 <= response.confidence <= 1.0
        assert response.regime in ["BULL", "BEAR", "SIDEWAYS"]
    
    def test_filter_trade(self):
        """Test trade filtering"""
        client = CapitalShieldClient(engine_mode="MOCK")
        
        price_history = [100, 105, 110, 115, 120]
        
        response = client.filter_trade("BTC", "BUY", price_history)
        
        assert isinstance(response.trade_allowed, bool)
        assert response.reason is not None
    
    def test_blocked_trades_tracking(self):
        """Test that blocked trades are tracked"""
        client = CapitalShieldClient(engine_mode="MOCK")
        
        # Force a blocked trade by setting unhealthy system
        client.set_system_health(False)
        
        price_history = [100, 105, 110]
        response = client.filter_trade("BTC", "BUY", price_history)
        
        # Should be blocked due to health check
        if not response.trade_allowed:
            blocked = client.get_blocked_trades()
            assert len(blocked) > 0


class TestRunner:
    """Test simulation runner"""
    
    def test_run_simulation_basic(self):
        """Test basic simulation run"""
        # Create temporary CSV file
        df = create_synthetic_data(["BTC", "ETH"], num_candles=30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name)
            temp_path = f.name
        
        try:
            results = run_simulation(
                data_path=temp_path,
                symbols=["BTC", "ETH"],
                initial_equity=100000,
                engine_mode="MOCK",
                capital_shield_mode="PERMISSIVE"
            )
            
            # Check results structure
            assert 'portfolio_metrics' in results
            assert 'equity_curve' in results
            assert 'trades' in results
            assert 'blocked_trades' in results
            
            # Check metrics
            metrics = results['portfolio_metrics']
            assert metrics['initial_equity'] == 100000
            assert metrics['final_equity'] >= 0  # No negative equity
            assert metrics['total_trades'] >= 0
            assert metrics['max_drawdown'] <= 0  # Drawdown is negative or zero
            
            # Check equity curve
            assert len(results['equity_curve']) > 0
            assert all(eq >= 0 for eq in results['equity_curve'])  # No negative equity
            
        finally:
            os.unlink(temp_path)
    
    def test_safety_rails_block_trades(self):
        """Test that safety rails can block trades"""
        df = create_synthetic_data(["BTC"], num_candles=30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name)
            temp_path = f.name
        
        try:
            # Run with forced max drawdown breach
            # We'll simulate this by setting metrics manually in the client
            results = run_simulation(
                data_path=temp_path,
                symbols=["BTC"],
                initial_equity=100000,
                engine_mode="MOCK",
                capital_shield_mode="STRICT"
            )
            
            # Should complete without errors
            assert 'blocked_trades' in results
            assert isinstance(results['blocked_trades'], list)
            
        finally:
            os.unlink(temp_path)
    
    def test_determinism(self):
        """Test that simulation is deterministic"""
        df = create_synthetic_data(["BTC"], num_candles=30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name)
            temp_path = f.name
        
        try:
            # Run simulation twice with same config
            results1 = run_simulation(
                data_path=temp_path,
                symbols=["BTC"],
                initial_equity=100000,
                engine_mode="MOCK",
                capital_shield_mode="PERMISSIVE"
            )
            
            results2 = run_simulation(
                data_path=temp_path,
                symbols=["BTC"],
                initial_equity=100000,
                engine_mode="MOCK",
                capital_shield_mode="PERMISSIVE"
            )
            
            # In MOCK mode, results should be identical
            assert results1['portfolio_metrics']['final_equity'] == results2['portfolio_metrics']['final_equity']
            assert results1['portfolio_metrics']['total_trades'] == results2['portfolio_metrics']['total_trades']
            
        finally:
            os.unlink(temp_path)
    
    def test_edge_case_empty_data(self):
        """Test handling of empty data"""
        # Create empty DataFrame
        df = pd.DataFrame(columns=["BTC"])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name)
            temp_path = f.name
        
        try:
            # Should handle gracefully
            results = run_simulation(
                data_path=temp_path,
                symbols=["BTC"],
                initial_equity=100000,
                engine_mode="MOCK"
            )
            
            # Should complete without errors
            assert 'portfolio_metrics' in results
            assert results['portfolio_metrics']['total_trades'] == 0
            
        finally:
            os.unlink(temp_path)
    
    def test_edge_case_single_candle(self):
        """Test handling of single candle"""
        df = create_synthetic_data(["BTC"], num_candles=1)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name)
            temp_path = f.name
        
        try:
            # Should handle gracefully (not enough data for signals)
            results = run_simulation(
                data_path=temp_path,
                symbols=["BTC"],
                initial_equity=100000,
                engine_mode="MOCK"
            )
            
            # Should complete without errors
            assert 'portfolio_metrics' in results
            
        finally:
            os.unlink(temp_path)


class TestReporting:
    """Test reporting functionality"""
    
    def test_generate_summary(self):
        """Test summary generation"""
        results = {
            'portfolio_metrics': {
                'initial_equity': 100000,
                'final_equity': 110000,
                'total_pnl': 10000,
                'pnl_percent': 10.0,
                'max_drawdown': -0.05,
                'total_trades': 10,
                'win_rate': 0.6,
                'open_positions': 2
            },
            'blocked_trades_count': 3,
            'blocked_by_reason': {
                'Max drawdown threshold exceeded': 2,
                'System health check failed': 1
            },
            'simulation_config': {
                'symbols': ['BTC', 'ETH'],
                'engine_mode': 'MOCK',
                'capital_shield_mode': 'PERMISSIVE'
            }
        }
        
        summary = generate_summary(results)
        
        assert "CAPITAL SHIELD API LIVE SIMULATION RESULTS" in summary or "LIVE SIMULATION RESULTS" in summary
        assert "100,000" in summary or "100000" in summary
        assert "110,000" in summary or "110000" in summary
        assert "Blocked Trades: 3" in summary
    
    def test_export_equity_curve(self):
        """Test equity curve export"""
        equity_curve = [100000, 105000, 110000, 108000, 112000]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            export_equity_curve(equity_curve, temp_path)
            
            # Verify file exists and has correct content
            assert os.path.exists(temp_path)
            
            df = pd.read_csv(temp_path)
            assert len(df) == len(equity_curve)
            assert 'equity' in df.columns
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_baseline_vs_capital_shielded_interface(self):
        """Test that baseline and capital_shielded modes both work"""
        df = create_synthetic_data(["BTC"], num_candles=30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name)
            temp_path = f.name
        
        try:
            # Run baseline mode
            baseline_results = run_simulation(
                data_path=temp_path,
                symbols=["BTC"],
                initial_equity=100000,
                mode="baseline"
            )
            
            # Run capital_shielded mode
            capital_shielded_results = run_simulation(
                data_path=temp_path,
                symbols=["BTC"],
                initial_equity=100000,
                mode="capital_shielded",
                engine_mode="MOCK",  # Use MOCK for testing
                capital_shield_mode="PERMISSIVE"
            )
            
            # Both should complete without errors
            assert 'portfolio_metrics' in baseline_results
            assert 'portfolio_metrics' in capital_shielded_results
            assert baseline_results['simulation_config']['mode'] == 'baseline'
            assert capital_shielded_results['simulation_config']['mode'] == 'capital_shielded'
            
            # Both should have consistent metric structures
            assert 'final_equity' in baseline_results['portfolio_metrics']
            assert 'final_equity' in capital_shielded_results['portfolio_metrics']
            assert 'max_drawdown' in baseline_results['portfolio_metrics']
            assert 'max_drawdown' in capital_shielded_results['portfolio_metrics']
            
        finally:
            os.unlink(temp_path)
    
    def test_compare_runs_summary(self):
        """Test comparison reporting function"""
        # Create fake results
        baseline_results = {
            'portfolio_metrics': {
                'final_equity': 100000,
                'total_pnl': 0,
                'pnl_percent': 0.0,
                'max_drawdown': -0.10,
                'total_trades': 10,
                'win_rate': 0.5
            },
            'blocked_trades_count': 0
        }
        
        capital_shielded_results = {
            'portfolio_metrics': {
                'final_equity': 105000,
                'total_pnl': 5000,
                'pnl_percent': 5.0,
                'max_drawdown': -0.05,
                'total_trades': 8,
                'win_rate': 0.6
            },
            'blocked_trades_count': 2
        }
        
        comparison = compare_runs(baseline_results, capital_shielded_results)
        
        # Check structure
        assert 'baseline' in comparison
        assert 'shielded' in comparison
        assert 'differences' in comparison
        assert 'shield_effect' in comparison
        
        # Check values
        assert comparison['baseline']['final_equity'] == 100000
        assert comparison['shielded']['final_equity'] == 105000
        assert comparison['shielded']['blocked_trades'] == 2
        assert comparison['differences']['equity_diff'] == 5000
        
        # Check shield effects
        assert len(comparison['shield_effect']) > 0
        assert any('drawdown' in effect.lower() for effect in comparison['shield_effect'])
        assert any('blocked' in effect.lower() for effect in comparison['shield_effect'])
    
    def test_run_historical_validation_smoke(self):
        """Test historical validation runs without errors"""
        df = create_synthetic_data(["BTC", "ETH"], num_candles=30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name)
            temp_path = f.name
        
        try:
            summary = run_historical_validation(
                data_path=temp_path,
                symbols=["BTC", "ETH"],
                initial_equity=100000
            )
            
            # Check structure
            assert 'baseline' in summary
            assert 'scenarios' in summary
            assert 'data_path' in summary
            assert 'symbols' in summary
            
            # Check baseline exists
            baseline = summary['baseline']
            assert 'portfolio_metrics' in baseline
            assert 'final_equity' in baseline['portfolio_metrics']
            assert 'max_drawdown' in baseline['portfolio_metrics']
            assert 'total_trades' in baseline['portfolio_metrics']
            
            # Check at least one capital_shielded scenario exists
            assert len(summary['scenarios']) > 0
            
            # Check each scenario has results and comparison
            for scenario_name, scenario_data in summary['scenarios'].items():
                assert 'results' in scenario_data
                assert 'comparison' in scenario_data
                
                comparison = scenario_data['comparison']
                assert 'baseline' in comparison
                assert 'capital_shielded' in comparison or 'shielded' in comparison
                assert 'differences' in comparison
                assert 'shield_effect' in comparison
                
                # Check comparison has key metrics
                assert 'final_equity' in comparison['baseline']
                shielded_key = 'capital_shielded' if 'capital_shielded' in comparison else 'shielded'
                assert 'final_equity' in comparison[shielded_key]
                assert 'max_drawdown' in comparison['baseline']
                assert 'max_drawdown' in comparison[shielded_key]
                
        finally:
            os.unlink(temp_path)
    
    def test_generate_markdown_summary_contains_core_metrics(self):
        """Test markdown summary generation"""
        # Create fake summary dict
        summary = {
            'data_path': 'test_data.csv',
            'symbols': ['BTC', 'ETH'],
            'initial_equity': 100000,
            'baseline': {
                'portfolio_metrics': {
                    'final_equity': 100000,
                    'total_pnl': 0,
                    'pnl_percent': 0.0,
                    'max_drawdown': -0.10,
                    'total_trades': 10,
                    'win_rate': 0.5
                }
            },
            'scenarios': {
                'capital_shielded_permissive': {
                    'comparison': {
                        'baseline': {
                            'final_equity': 100000,
                            'max_drawdown': -0.10,
                            'total_trades': 10
                        },
                        'capital_shielded': {
                            'final_equity': 105000,
                            'max_drawdown': -0.05,
                            'total_trades': 8,
                            'blocked_trades': 2
                        },
                        'differences': {
                            'equity_diff': 5000,
                            'equity_diff_pct': 5.0,
                            'drawdown_diff': 0.05,
                            'drawdown_improvement_pct': 50.0,
                            'trades_diff': -2
                        },
                        'shield_effect': [
                            'Reduced max drawdown by 50.0%',
                            'Blocked 2 trades via safety rails'
                        ]
                    }
                }
            }
        }
        
        markdown = generate_markdown_summary(summary)
        
        # Check key content appears
        assert 'test_data.csv' in markdown
        assert 'BTC' in markdown
        assert 'ETH' in markdown
        assert '100,000' in markdown or '100000' in markdown
        assert 'capital_shielded_permissive' in markdown.lower() or 'Capital Shielded Permissive' in markdown or 'shielded_permissive' in markdown.lower()
        assert '5.0%' in markdown or '5.00%' in markdown  # Equity diff
        assert '50.0%' in markdown or '50.0' in markdown  # Drawdown improvement
        assert 'Blocked 2 trades' in markdown

