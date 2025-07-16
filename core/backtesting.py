"""
Backtesting framework for sentiment-based trading strategies
"""
import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import asdict
import json

from core.data_models import TradingSignal, BacktestResult, SignalType, MarketData
from config import trading_config

logger = logging.getLogger(__name__)

class MockMarketData:
    """Generate mock market data for backtesting"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.current_prices = {symbol: np.random.uniform(100, 50000) for symbol in symbols}
        self.volatilities = {symbol: np.random.uniform(0.02, 0.05) for symbol in symbols}
    
    def generate_price_data(self, start_date: datetime, end_date: datetime, 
                          frequency_minutes: int = 5) -> Dict[str, List[MarketData]]:
        """Generate mock price data for backtesting"""
        data = {symbol: [] for symbol in self.symbols}
        
        current_date = start_date
        while current_date <= end_date:
            for symbol in self.symbols:
                # Random walk with some mean reversion
                change = np.random.normal(0, self.volatilities[symbol])
                self.current_prices[symbol] *= (1 + change)
                
                # Ensure price doesn't go negative
                self.current_prices[symbol] = max(self.current_prices[symbol], 0.01)
                
                volume = np.random.uniform(1000000, 100000000)
                change_24h = np.random.uniform(-0.15, 0.15)
                
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=current_date,
                    price=self.current_prices[symbol],
                    volume=volume,
                    change_24h=change_24h
                )
                
                data[symbol].append(market_data)
            
            current_date += timedelta(minutes=frequency_minutes)
        
        return data

class Position:
    """Represents a trading position"""
    
    def __init__(self, symbol: str, signal: TradingSignal, entry_price: float):
        self.symbol = symbol
        self.signal = signal
        self.entry_price = entry_price
        self.entry_time = signal.timestamp
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[datetime] = None
        self.pnl: float = 0.0
        self.is_closed = False
        self.max_favorable_excursion = 0.0  # Best price reached
        self.max_adverse_excursion = 0.0    # Worst price reached
    
    def update_price(self, current_price: float, current_time: datetime):
        """Update position with current market price"""
        if self.is_closed:
            return
        
        # Calculate unrealized PnL
        if self.signal.signal_type == SignalType.BUY:
            unrealized_pnl = (current_price - self.entry_price) / self.entry_price
            # Track excursions
            if current_price > self.entry_price:
                self.max_favorable_excursion = max(
                    self.max_favorable_excursion, 
                    (current_price - self.entry_price) / self.entry_price
                )
            else:
                self.max_adverse_excursion = min(
                    self.max_adverse_excursion,
                    (current_price - self.entry_price) / self.entry_price
                )
        else:  # SELL
            unrealized_pnl = (self.entry_price - current_price) / self.entry_price
            # Track excursions
            if current_price < self.entry_price:
                self.max_favorable_excursion = max(
                    self.max_favorable_excursion,
                    (self.entry_price - current_price) / self.entry_price
                )
            else:
                self.max_adverse_excursion = min(
                    self.max_adverse_excursion,
                    (self.entry_price - current_price) / self.entry_price
                )
        
        # Check exit conditions
        should_exit, exit_reason = self._check_exit_conditions(current_price, current_time)
        if should_exit:
            self.close_position(current_price, current_time, exit_reason)
    
    def _check_exit_conditions(self, current_price: float, current_time: datetime) -> Tuple[bool, str]:
        """Check if position should be closed"""
        # Time-based exit (max holding period)
        max_hold_time = timedelta(hours=24)  # 24 hours max
        if current_time - self.entry_time > max_hold_time:
            return True, "time_exit"
        
        # Stop loss
        if self.signal.stop_loss:
            if self.signal.signal_type == SignalType.BUY and current_price <= self.signal.stop_loss:
                return True, "stop_loss"
            elif self.signal.signal_type == SignalType.SELL and current_price >= self.signal.stop_loss:
                return True, "stop_loss"
        
        # Take profit
        if self.signal.take_profit:
            if self.signal.signal_type == SignalType.BUY and current_price >= self.signal.take_profit:
                return True, "take_profit"
            elif self.signal.signal_type == SignalType.SELL and current_price <= self.signal.take_profit:
                return True, "take_profit"
        
        return False, ""
    
    def close_position(self, exit_price: float, exit_time: datetime, reason: str):
        """Close the position"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.is_closed = True
        
        # Calculate final PnL
        if self.signal.signal_type == SignalType.BUY:
            self.pnl = (exit_price - self.entry_price) / self.entry_price
        else:  # SELL
            self.pnl = (self.entry_price - exit_price) / self.entry_price
        
        # Apply position sizing
        self.pnl *= self.signal.position_size
        
        logger.debug(f"Closed {self.symbol} position: {reason}, PnL: {self.pnl:.4f}")

class Portfolio:
    """Portfolio management for backtesting"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.equity_curve = []
        self.daily_returns = []
        self.max_drawdown = 0.0
        self.peak_equity = initial_capital
    
    def add_signal(self, signal: TradingSignal, current_price: float) -> bool:
        """Add a trading signal to the portfolio"""
        if signal.signal_type == SignalType.HOLD:
            return False
        
        # Check if we already have a position in this asset
        existing_position = self._get_open_position(signal.asset)
        if existing_position:
            # Close existing position first
            existing_position.close_position(current_price, signal.timestamp, "new_signal")
            self._settle_closed_position(existing_position)
        
        # Calculate position size in dollar terms
        position_value = self.current_capital * signal.position_size
        
        # Check if we have enough capital
        if position_value > self.current_capital * 0.95:  # 95% max utilization
            logger.warning(f"Insufficient capital for position in {signal.asset}")
            return False
        
        # Create new position
        position = Position(signal.asset, signal, current_price)
        self.positions.append(position)
        
        logger.debug(f"Opened {signal.signal_type.value} position in {signal.asset} at {current_price}")
        return True
    
    def update_positions(self, market_data: Dict[str, MarketData]):
        """Update all positions with current market data"""
        for position in self.positions[:]:  # Copy list to allow modification
            if position.symbol in market_data:
                data = market_data[position.symbol]
                position.update_price(data.price, data.timestamp)
                
                if position.is_closed:
                    self._settle_closed_position(position)
        
        # Update equity curve
        current_equity = self._calculate_current_equity(market_data)
        self.equity_curve.append({
            'timestamp': datetime.now(),
            'equity': current_equity,
            'drawdown': (self.peak_equity - current_equity) / self.peak_equity
        })
        
        # Update peak and drawdown
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        else:
            current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
            self.max_drawdown = max(self.max_drawdown, current_drawdown)
    
    def _get_open_position(self, symbol: str) -> Optional[Position]:
        """Get open position for a symbol"""
        for position in self.positions:
            if position.symbol == symbol and not position.is_closed:
                return position
        return None
    
    def _settle_closed_position(self, position: Position):
        """Settle a closed position"""
        # Update capital based on PnL
        pnl_amount = position.pnl * self.current_capital
        self.current_capital += pnl_amount
        
        # Move to closed positions
        self.positions.remove(position)
        self.closed_positions.append(position)
        
        # Record daily return
        daily_return = pnl_amount / self.current_capital
        self.daily_returns.append(daily_return)
    
    def _calculate_current_equity(self, market_data: Dict[str, MarketData]) -> float:
        """Calculate current portfolio equity including unrealized PnL"""
        equity = self.current_capital
        
        for position in self.positions:
            if not position.is_closed and position.symbol in market_data:
                current_price = market_data[position.symbol].price
                if position.signal.signal_type == SignalType.BUY:
                    unrealized_pnl = (current_price - position.entry_price) / position.entry_price
                else:
                    unrealized_pnl = (position.entry_price - current_price) / position.entry_price
                
                equity += unrealized_pnl * position.signal.position_size * self.current_capital
        
        return equity

class BacktestEngine:
    """Main backtesting engine"""
    
    def __init__(self):
        self.mock_data_generator = None
        self.portfolio = None
        self.signals_to_test = []
    
    async def run_backtest(
        self, 
        signals: List[TradingSignal], 
        start_date: datetime, 
        end_date: datetime,
        initial_capital: float = 100000,
        symbols: List[str] = None
    ) -> BacktestResult:
        """Run a complete backtest"""
        
        if not symbols:
            symbols = list(set(signal.asset for signal in signals))
        
        # Initialize components
        self.mock_data_generator = MockMarketData(symbols)
        self.portfolio = Portfolio(initial_capital)
        
        # Generate market data
        logger.info(f"Generating market data from {start_date} to {end_date}")
        market_data = self.mock_data_generator.generate_price_data(start_date, end_date)
        
        # Organize signals by timestamp
        signals_by_time = {}
        for signal in signals:
            timestamp = signal.timestamp
            if timestamp not in signals_by_time:
                signals_by_time[timestamp] = []
            signals_by_time[timestamp].append(signal)
        
        # Run simulation
        logger.info("Running backtest simulation...")
        current_date = start_date
        while current_date <= end_date:
            # Get current market data
            current_market_data = {}
            for symbol in symbols:
                # Find closest market data point
                symbol_data = market_data[symbol]
                closest_data = min(
                    symbol_data, 
                    key=lambda x: abs((x.timestamp - current_date).total_seconds())
                )
                current_market_data[symbol] = closest_data
            
            # Process any signals at this timestamp
            if current_date in signals_by_time:
                for signal in signals_by_time[current_date]:
                    if signal.asset in current_market_data:
                        current_price = current_market_data[signal.asset].price
                        self.portfolio.add_signal(signal, current_price)
            
            # Update portfolio
            self.portfolio.update_positions(current_market_data)
            
            # Move to next timestamp
            current_date += timedelta(minutes=5)
        
        # Calculate final results
        return self._calculate_results(start_date, end_date)
    
    def _calculate_results(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """Calculate backtest results and performance metrics"""
        
        # Basic metrics
        final_equity = self.portfolio.equity_curve[-1]['equity'] if self.portfolio.equity_curve else self.portfolio.initial_capital
        total_return = (final_equity - self.portfolio.initial_capital) / self.portfolio.initial_capital
        
        # Calculate Sharpe ratio
        if self.portfolio.daily_returns:
            returns_array = np.array(self.portfolio.daily_returns)
            sharpe_ratio = np.mean(returns_array) / np.std(returns_array) * np.sqrt(252) if np.std(returns_array) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Win rate and profit factor
        profitable_trades = [p for p in self.portfolio.closed_positions if p.pnl > 0]
        losing_trades = [p for p in self.portfolio.closed_positions if p.pnl < 0]
        
        total_trades = len(self.portfolio.closed_positions)
        win_rate = len(profitable_trades) / total_trades if total_trades > 0 else 0
        
        total_profit = sum(p.pnl for p in profitable_trades)
        total_loss = abs(sum(p.pnl for p in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Average trade duration
        if self.portfolio.closed_positions:
            durations = [(p.exit_time - p.entry_time).total_seconds() / 3600 for p in self.portfolio.closed_positions if p.exit_time]
            avg_trade_duration = np.mean(durations) if durations else 0
        else:
            avg_trade_duration = 0
        
        # Detailed analysis
        details = {
            'final_equity': final_equity,
            'total_profitable_trades': len(profitable_trades),
            'total_losing_trades': len(losing_trades),
            'largest_win': max((p.pnl for p in profitable_trades), default=0),
            'largest_loss': min((p.pnl for p in losing_trades), default=0),
            'avg_win': np.mean([p.pnl for p in profitable_trades]) if profitable_trades else 0,
            'avg_loss': np.mean([p.pnl for p in losing_trades]) if losing_trades else 0,
            'max_consecutive_wins': self._calculate_max_consecutive(profitable_trades),
            'max_consecutive_losses': self._calculate_max_consecutive(losing_trades),
            'equity_curve': self.portfolio.equity_curve,
            'all_trades': [asdict(p) for p in self.portfolio.closed_positions]
        }
        
        return BacktestResult(
            strategy_name="Sentiment-Based Trading",
            start_date=start_date,
            end_date=end_date,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=self.portfolio.max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            avg_trade_duration=avg_trade_duration,
            details=details
        )
    
    def _calculate_max_consecutive(self, trades: List[Position]) -> int:
        """Calculate maximum consecutive wins or losses"""
        if not trades:
            return 0
        
        max_consecutive = 0
        current_consecutive = 0
        
        # Sort trades by time
        sorted_trades = sorted(trades, key=lambda x: x.entry_time)
        
        for trade in sorted_trades:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        
        return max_consecutive

async def run_strategy_backtest(signals: List[TradingSignal]) -> BacktestResult:
    """Run a backtest with the provided signals"""
    engine = BacktestEngine()
    
    # Define backtest period (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Run backtest
    result = await engine.run_backtest(
        signals=signals,
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000
    )
    
    logger.info(f"Backtest completed: {result.total_return:.2%} return, {result.sharpe_ratio:.2f} Sharpe ratio")
    
    return result