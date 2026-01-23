"""
Live Simulation Runner

Main orchestrator for running BoonMindX Capital Shield API simulations over historical data
Supports both baseline (BearHunter engine only) and capital_shielded (engine + BoonMindX Capital Shield safety rails) modes
"""
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Literal
from datetime import datetime
from .data_loader import load_historical_data, get_price_history
from .shield_client import CapitalShieldClient
from .bearhunter_bridge import get_signal as bridge_get_signal, filter_trade as bridge_filter_trade
from .reporting import generate_summary
from .slippage_model import ExecutionCostConfig, calculate_execution_cost, calculate_volatility_from_history


class Portfolio:
    """Simple portfolio tracker for simulation"""
    
    def __init__(self, initial_equity: float = 100000.0):
        self.initial_equity = initial_equity
        self.equity = initial_equity
        self.cash = initial_equity
        self.positions: Dict[str, Dict[str, Any]] = {}  # {symbol: {entry_price, entry_time, size}}
        self.equity_curve: List[float] = [initial_equity]
        self.trades: List[Dict[str, Any]] = []
        self.max_drawdown = 0.0
        self.peak_equity = initial_equity
    
    def update_equity(self, current_prices: Dict[str, float]):
        """Update equity based on current prices"""
        # Calculate unrealized PnL from open positions
        unrealized_pnl = 0.0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                entry_price = position['entry_price']
                size = position['size']
                pnl = (current_price - entry_price) * size
                unrealized_pnl += pnl
        
        self.equity = self.cash + unrealized_pnl
        self.equity_curve.append(self.equity)
        
        # Update max drawdown
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
        
        drawdown = (self.equity - self.peak_equity) / self.peak_equity if self.peak_equity > 0 else 0.0
        if drawdown < self.max_drawdown:
            self.max_drawdown = drawdown
    
    def enter_position(self, symbol: str, price: float, size: float, timestamp: pd.Timestamp):
        """Enter a new position"""
        if symbol in self.positions:
            # Already have position, skip
            return False
        
        cost = price * size
        if cost > self.cash:
            # Insufficient cash
            return False
        
        self.positions[symbol] = {
            'entry_price': price,
            'entry_time': timestamp,
            'size': size
        }
        self.cash -= cost
        
        self.trades.append({
            'symbol': symbol,
            'action': 'BUY',
            'price': price,
            'size': size,
            'timestamp': timestamp,
            'equity': self.equity
        })
        
        return True
    
    def exit_position(self, symbol: str, price: float, timestamp: pd.Timestamp) -> Optional[float]:
        """Exit an existing position"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        size = position['size']
        
        # Calculate PnL
        pnl = (price - entry_price) * size
        
        # Update cash
        self.cash += price * size
        
        # Record trade
        self.trades.append({
            'symbol': symbol,
            'action': 'SELL',
            'price': price,
            'size': size,
            'entry_price': entry_price,
            'pnl': pnl,
            'pnl_percent': (pnl / (entry_price * size)) * 100 if entry_price * size > 0 else 0.0,
            'timestamp': timestamp,
            'equity': self.equity
        })
        
        # Remove position
        del self.positions[symbol]
        
        return pnl
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get portfolio metrics"""
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        total_pnl = self.equity - self.initial_equity
        pnl_percent = (total_pnl / self.initial_equity) * 100 if self.initial_equity > 0 else 0.0
        
        return {
            'initial_equity': self.initial_equity,
            'final_equity': self.equity,
            'total_pnl': total_pnl,
            'pnl_percent': pnl_percent,
            'max_drawdown': self.max_drawdown,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'open_positions': len(self.positions)
        }


def run_simulation(
    data_path: str,
    symbols: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_equity: float = 100000.0,
    max_position_size: float = 0.1,
    leverage: float = 1.0,
    mode: Literal["baseline", "capital_shielded"] = "capital_shielded",
    engine_mode: str = "LIVE",  # For capital_shielded mode, use LIVE to get real engine
    capital_shield_mode: str = "PERMISSIVE",
    lookback_periods: int = 100,
    preset_name: Optional[str] = None,  # For FP tracking
    exec_cost_config: Optional[ExecutionCostConfig] = None  # Execution cost configuration
) -> Dict[str, Any]:
    """
    Run live simulation over historical data
    
    Args:
        data_path: Path to CSV file with historical data
        symbols: List of symbols to trade
        start_date: Start date (YYYY-MM-DD) or None
        end_date: End date (YYYY-MM-DD) or None
        initial_equity: Starting equity
        max_position_size: Max position size as fraction of equity
        leverage: Leverage multiplier
        mode: "baseline" (engine only) or "capital_shielded" (engine + safety rails)
        engine_mode: "MOCK" or "LIVE" (for capital_shielded mode)
        capital_shield_mode: "PERMISSIVE" or "STRICT" (for capital_shielded mode)
        lookback_periods: Number of periods to use for price history
        
    Returns:
        Dict with simulation results and metrics
    """
    # Load historical data
    df = load_historical_data(symbols, data_path, start_date, end_date)
    
    # Initialize client based on mode
    if mode == "baseline":
        # Baseline mode: Direct BearHunter engine, no Shield
        shield_client = None  # Not used in baseline
        use_bridge = True
    else:
        # Capital Shielded mode: Use Capital Shield client with engine adapter
        shield_client = CapitalShieldClient(engine_mode=engine_mode, capital_shield_mode=capital_shield_mode)
        shield_client.set_system_health(True)
        if preset_name:
            shield_client.set_preset_name(preset_name)
        use_bridge = False
    
    # Initialize portfolio
    portfolio = Portfolio(initial_equity=initial_equity)
    
    # Initialize execution cost tracking
    total_execution_costs = 0.0
    execution_cost_count = 0
    
    # Iterate over dates chronologically
    dates = df.index.unique().sort_values()
    
    for current_date in dates:
        # Get current prices for all symbols
        current_prices = {}
        for symbol in symbols:
            if symbol in df.columns:
                symbol_data = df.loc[df.index == current_date, symbol]
                if not symbol_data.empty and not pd.isna(symbol_data.iloc[0]):
                    current_prices[symbol] = float(symbol_data.iloc[0])
        
        # Update portfolio equity with current prices
        portfolio.update_equity(current_prices)
        
        # Update safety rails with current metrics (only for shielded mode)
        if not use_bridge and shield_client:
            metrics = portfolio.get_metrics()
            shield_client.set_current_metrics({
                'max_drawdown': portfolio.max_drawdown,
                'equity': portfolio.equity,
                'total_trades': metrics['total_trades']
            })
        
        # Process each symbol
        for symbol in symbols:
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Get price history for this symbol
            price_history, volume_history = get_price_history(
                df, symbol, current_date, lookback_periods
            )
            
            if len(price_history) < 10:  # Need minimum data
                continue
            
            # Get signal (baseline or shielded)
            if use_bridge:
                # Baseline mode: Direct BearHunter engine
                signal_response = bridge_get_signal(symbol, price_history, volume_history)
            else:
                # Shielded mode: Via Shield client
                signal_response = shield_client.get_signal(symbol, price_history, volume_history)
            
            # Determine action based on signal and current position
            action = None
            if symbol in portfolio.positions:
                # Have position - check for exit signal
                if signal_response.signal == "SELL":
                    action = "SELL"
            else:
                # No position - check for entry signal
                if signal_response.signal == "BUY":
                    action = "BUY"
            
            if action:
                # Check if trade is allowed
                if use_bridge:
                    # Baseline mode: Direct engine filter (no safety rails)
                    filter_response = bridge_filter_trade(
                        symbol, action, price_history, volume_history
                    )
                else:
                    # Shielded mode: Shield filter (with safety rails)
                    filter_response = shield_client.filter_trade(
                        symbol, action, price_history, volume_history,
                        current_price=current_price,
                        current_equity=portfolio.equity,
                        timestamp=current_date.isoformat() if hasattr(current_date, 'isoformat') else str(current_date)
                    )
                
                if filter_response.trade_allowed:
                    # Execute trade
                    if action == "BUY":
                        # Calculate position size
                        position_value = portfolio.equity * max_position_size * leverage
                        size = position_value / current_price
                        
                        # Calculate execution cost
                        notional = size * current_price
                        volatility = calculate_volatility_from_history(price_history) if len(price_history) >= 20 else None
                        exec_cost = calculate_execution_cost(
                            current_price,
                            notional,
                            exec_cost_config or ExecutionCostConfig(enabled=False),
                            volatility
                        )
                        
                        # Apply execution cost
                        if exec_cost > 0:
                            portfolio.cash -= exec_cost
                            total_execution_costs += exec_cost
                            execution_cost_count += 1
                        
                        portfolio.enter_position(symbol, current_price, size, current_date)
                    
                    elif action == "SELL":
                        # Get position size before exit
                        if symbol in portfolio.positions:
                            position = portfolio.positions[symbol]
                            exit_size = position['size']
                            notional = exit_size * current_price
                            
                            # Calculate execution cost
                            volatility = calculate_volatility_from_history(price_history) if len(price_history) >= 20 else None
                            exec_cost = calculate_execution_cost(
                                current_price,
                                notional,
                                exec_cost_config or ExecutionCostConfig(enabled=False),
                                volatility
                            )
                            
                            # Apply execution cost
                            if exec_cost > 0:
                                portfolio.cash -= exec_cost
                                total_execution_costs += exec_cost
                                execution_cost_count += 1
                        
                        portfolio.exit_position(symbol, current_price, current_date)
        
        # Update equity again after trades
        portfolio.update_equity(current_prices)
    
    # Final metrics
    portfolio_metrics = portfolio.get_metrics()
    
    # Get blocked trades (only for shielded mode)
    if use_bridge:
        blocked_trades = []
        blocked_by_reason = {}
    else:
        blocked_trades = shield_client.get_blocked_trades() if shield_client else []
        # Count blocked trades by reason
        blocked_by_reason = {}
        for bt in blocked_trades:
            reason = bt['reason']
            blocked_by_reason[reason] = blocked_by_reason.get(reason, 0) + 1
    
    # Execution cost metrics
    execution_cost_metrics = {}
    if exec_cost_config and exec_cost_config.enabled:
        execution_cost_metrics = {
            'total_execution_costs': total_execution_costs,
            'avg_cost_per_trade': total_execution_costs / execution_cost_count if execution_cost_count > 0 else 0.0,
            'slippage_model_used': exec_cost_config.slippage_model,
            'latency_ms': exec_cost_config.latency_ms,
            'execution_cost_count': execution_cost_count
        }
    else:
        execution_cost_metrics = {
            'total_execution_costs': 0.0,
            'avg_cost_per_trade': 0.0,
            'slippage_model_used': 'none',
            'latency_ms': 0,
            'execution_cost_count': 0
        }
    
    results = {
        'portfolio_metrics': portfolio_metrics,
        'equity_curve': portfolio.equity_curve,
        'trades': portfolio.trades,
        'blocked_trades': blocked_trades,
        'blocked_trades_count': len(blocked_trades),
        'blocked_by_reason': blocked_by_reason,
        'execution_costs': execution_cost_metrics,
        'simulation_config': {
            'mode': mode,
            'symbols': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'initial_equity': initial_equity,
            'engine_mode': engine_mode if not use_bridge else "LIVE",
            'capital_shield_mode': capital_shield_mode if not use_bridge else None,
            'exec_cost_enabled': exec_cost_config.enabled if exec_cost_config else False
        }
    }
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Capital Shield API live simulation")
    parser.add_argument("--data-path", required=True, help="Path to CSV data file")
    parser.add_argument("--symbols", nargs="+", required=True, help="Symbols to trade")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--initial-equity", type=float, default=100000.0)
    parser.add_argument("--mode", default="capital_shielded", choices=["baseline", "capital_shielded"], 
                       help="baseline = engine only, capital_shielded = engine + safety rails")
    parser.add_argument("--engine-mode", default="LIVE", choices=["MOCK", "LIVE"],
                       help="Engine mode for capital_shielded mode (ignored for baseline)")
    parser.add_argument("--capital-shield-mode", default="PERMISSIVE", choices=["PERMISSIVE", "STRICT"],
                       help="Capital Shield mode for capital_shielded mode (ignored for baseline)")
    parser.add_argument("--output", help="Output file for results JSON")
    
    args = parser.parse_args()
    
    # Run simulation
    results = run_simulation(
        data_path=args.data_path,
        symbols=args.symbols,
        start_date=args.start_date,
        end_date=args.end_date,
        initial_equity=args.initial_equity,
        mode=args.mode,
        engine_mode=args.engine_mode,
        capital_shield_mode=getattr(args, 'capital_shield_mode', 'PERMISSIVE')
    )
    
    # Print summary
    summary = generate_summary(results)
    print(summary)
    
    # Save results if output specified
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)

