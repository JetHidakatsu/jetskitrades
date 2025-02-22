#!/usr/bin/env python3
"""Backtesting and simulation utility for trading strategy evaluation"""

import asyncio
import sys
import argparse
import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from env.quantum_pool_selector import QuantumPoolSelector, PoolMetrics
from env.sentiment_analyzer import SentimentAnalyzer
from env.trading_logic import TradingLogic, TradingParameters
from env.latency_tracker import LatencyTracker
from env.helius_provider import HeliusDataProvider, PoolCreationEvent
from dotenv import load_dotenv

@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    start_date: datetime
    end_date: datetime
    initial_capital: float
    risk_factor: float
    max_position_size: float
    min_position_size: float
    max_positions: int
    slippage: float
    use_helius: bool = False  # Whether to fetch data from Helius API
    data_source: str = "file"  # "file" or "helius"

@dataclass
class BacktestResults:
    """Backtesting results"""
    total_trades: int
    successful_trades: int
    total_profit: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[Dict]
    equity_curve: List[float]
    positions: List[Dict]

class BacktestEngine:
    """Engine for backtesting trading strategies"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.quantum_selector = QuantumPoolSelector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.latency_tracker = LatencyTracker(metrics_port=8006)
        
        # Convert USD capital to SOL (assuming $240/SOL)
        self.sol_price_usd = 240.0  # Current approximate SOL price
        self.capital = config.initial_capital / self.sol_price_usd
        self.logger.info(f"Initial capital: ${config.initial_capital:.2f} = {self.capital:.4f} SOL")
        
        # Trading state
        self.positions = {}
        self.trades = []
        self.equity_curve = [self.capital]
        
    async def run_backtest(self, data_path: Optional[Path] = None) -> BacktestResults:
        """Run backtest simulation"""
        try:
            # Load historical data
            if self.config.data_source == "helius":
                self.historical_data = await self._load_helius_data()
            else:
                if not data_path:
                    raise ValueError("data_path required when data_source is 'file'")
                self.historical_data = self._load_historical_data(data_path)
            
            # Initialize trading logic
            trading_logic = self._initialize_trading_logic()
            
            # Process each event in chronological order
            for event in self._generate_events(self.historical_data):
                await self._process_event(event, trading_logic)
                
            # Close any remaining positions if there is data
            if self.historical_data:
                await self._close_all_positions(self.historical_data[-1]['timestamp'])
            else:
                self.logger.warning("No historical data found in the specified date range")
            
            # Calculate results
            results = self._calculate_results()
            
            # Save results
            self._save_results(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in backtesting: {e}")
            raise
            
    async def _load_helius_data(self) -> List[Dict]:
        """Load historical data from Helius API"""
        try:
            load_dotenv()
            helius_provider = HeliusDataProvider(
                api_key=os.getenv('HELIUS_API_KEY'),
                endpoint=os.getenv('HELIUS_ENDPOINT', 'https://api.helius.xyz/v0')
            )
            
            # Get pool creation events
            pools = await helius_provider.get_pool_creations(
                self.config.start_date,
                self.config.end_date
            )
            
            # Convert to historical data format
            historical_data = []
            for pool in pools:
                # Add pool creation event
                historical_data.append({
                    'type': 'pool_creation',
                    'timestamp': pool.timestamp,
                    'pool_id': pool.pool_id,
                    'pool_data': {
                        'initial_liquidity': pool.initial_liquidity,
                        'price_impact': pool.price_impact,
                        'creator_address': pool.creator_address,
                        'token_mint': pool.token_mint
                    }
                })
                
                # Get price impact history
                price_impacts = await helius_provider.get_price_impacts(
                    [pool.pool_id],
                    timeframe=self.config.end_date - self.config.start_date
                )
                
                if pool.pool_id in price_impacts:
                    for impact in price_impacts[pool.pool_id]:
                        historical_data.append({
                            'type': 'price_update',
                            'timestamp': pool.timestamp + timedelta(minutes=1),  # Approximate
                            'pool_id': pool.pool_id,
                            'price': 1.0 + impact  # Approximate price from impact
                        })
            
            return sorted(historical_data, key=lambda x: x['timestamp'])
            
        except Exception as e:
            self.logger.error(f"Error loading Helius data: {e}")
            raise

    def _load_historical_data(self, data_path: Path) -> List[Dict]:
        """Load and preprocess historical data"""
        try:
            with open(data_path) as f:
                json_data = json.load(f)
                
            # Extract events from the JSON structure
            data = json_data['events']
            
            # Convert timestamps
            for event in data:
                # Remove 'Z' and add UTC timezone info
                timestamp_str = event['timestamp'].replace('Z', '+00:00')
                event['timestamp'] = datetime.fromisoformat(timestamp_str).astimezone()
                
            # Sort by timestamp
            data.sort(key=lambda x: x['timestamp'])
            
            # Filter by date range
            data = [
                event for event in data
                if self.config.start_date <= event['timestamp'] <= self.config.end_date
            ]
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            raise
            
    def _initialize_trading_logic(self) -> TradingLogic:
        """Initialize trading logic with backtest parameters"""
        from env.pool_validator import PoolValidator
        from solana.rpc.async_api import AsyncClient
        
        params = TradingParameters(
            max_position_size=self.config.max_position_size,
            min_position_size=self.config.min_position_size,
            risk_factor=self.config.risk_factor,
            max_slippage=self.config.slippage,
            min_liquidity=1000,
            sentiment_threshold=0.4,  # Lowered from 0.6
            quantum_threshold=0.3,    # Lowered from 0.7
        )
        
        # Initialize RPC client and pool validator
        rpc_client = AsyncClient("https://api.mainnet-beta.solana.com")
        pool_validator = PoolValidator(rpc_client)
        
        return TradingLogic(
            self.quantum_selector,
            self.sentiment_analyzer,
            None,  # No transaction executor needed for backtest
            pool_validator,
            self.latency_tracker,
            params
        )
        
    def _generate_events(self, data: List[Dict]) -> List[Dict]:
        """Generate trading events from historical data"""
        events = []
        
        for entry in data:
            # Pool creation events
            if entry.get('type') == 'pool_creation':
                events.append({
                    'type': 'pool_creation',
                    'timestamp': entry['timestamp'],
                    'pool_id': entry['pool_id'],
                    'data': entry['pool_data']
                })
                
            # Price update events
            elif entry.get('type') == 'price_update':
                events.append({
                    'type': 'price_update',
                    'timestamp': entry['timestamp'],
                    'pool_id': entry['pool_id'],
                    'price': entry['price']
                })
                
        return sorted(events, key=lambda x: x['timestamp'])
        
    async def _process_event(self, event: Dict, trading_logic: TradingLogic):
        """Process a single event"""
        try:
            if event['type'] == 'pool_creation':
                await self._handle_pool_creation(event, trading_logic)
            elif event['type'] == 'price_update':
                await self._handle_price_update(event, trading_logic)
                
            # Update equity curve
            self.equity_curve.append(self._calculate_current_equity())
            
        except Exception as e:
            self.logger.error(f"Error processing event: {e}")
            
    async def _handle_pool_creation(self, event: Dict, trading_logic: TradingLogic):
        """Handle pool creation event"""
        try:
            pool_id = event['pool_id']
            pool_data = event['data']
            
            self.logger.info(f"Processing pool creation: {pool_id}")
            self.logger.debug(f"Pool data: {pool_data}")
            
            # Evaluate trading opportunity
            meets_criteria, score, analysis = await trading_logic.evaluate_trading_opportunity(
                pool_id,
                pool_data,
                pool_data.get('creator_address', '')
            )
            
            self.logger.info(f"Evaluation results - Meets criteria: {meets_criteria}, Score: {score}")
            self.logger.debug(f"Analysis: {analysis}")
            
            if meets_criteria and len(self.positions) < self.config.max_positions:
                # Create pool metrics
                metrics = PoolMetrics(
                    liquidity=pool_data.get('initial_liquidity', 0),
                    volume_24h=0,  # Not available at creation
                    price_impact=pool_data.get('price_impact', 0),
                    holder_count=0,  # Not available at creation
                    creator_score=0.5,  # Default score
                    time_since_creation=0.0  # Just created
                )
                
                # Calculate position size
                size = await trading_logic.calculate_position_size(
                    score,
                    metrics,
                    self.capital
                )
                
                self.logger.info(f"Opening position - Size: {size}, Entry price: {pool_data['price']}")
                
                # Open position
                self.positions[pool_id] = {
                    'entry_time': event['timestamp'],
                    'entry_price': pool_data['price'],
                    'size': size,
                    'score': score
                }
                
                self.capital -= size
                
        except Exception as e:
            self.logger.error(f"Error handling pool creation: {e}")
            
    async def _handle_price_update(self, event: Dict, trading_logic: TradingLogic):
        """Handle price update event"""
        pool_id = event['pool_id']
        current_price = event['price']
        
        if pool_id in self.positions:
            position = self.positions[pool_id]
            
            # Create pool metrics for exit check
            pool_metrics = PoolMetrics(
                liquidity=0,  # Will be filled by validator
                volume_24h=0,
                price_impact=0,
                holder_count=0,
                creator_score=0,
                time_since_creation=0
            )
            
            # Check exit conditions
            should_exit = await trading_logic._check_exit_conditions(
                pool_id,
                current_price,
                pool_metrics,
                False  # Not a memecoin by default
            )
            
            if should_exit:
                await self._close_position(pool_id, current_price, event['timestamp'])
                
    async def _close_position(self, pool_id: str, price: float, timestamp: datetime):
        """Close a single position"""
        position = self.positions[pool_id]
        
        # Calculate profit/loss
        profit = (price - position['entry_price']) * position['size']
        
        # Record trade
        self.trades.append({
            'pool_id': pool_id,
            'entry_time': position['entry_time'],
            'exit_time': timestamp,
            'entry_price': position['entry_price'],
            'exit_price': price,
            'size': position['size'],
            'profit': profit
        })
        
        # Update capital
        self.capital += position['size'] + profit
        
        # Remove position
        del self.positions[pool_id]
        
    async def _close_all_positions(self, timestamp: datetime):
        """Close all open positions"""
        # Find the last known price for each pool
        last_prices = {}
        for event in reversed(self._generate_events(self.historical_data)):
            if event['type'] == 'price_update' and event['pool_id'] not in last_prices:
                last_prices[event['pool_id']] = event['price']

        # Close positions with last known price or entry price as fallback
        for pool_id in list(self.positions.keys()):
            final_price = last_prices.get(pool_id, self.positions[pool_id]['entry_price'])
            await self._close_position(pool_id, final_price, timestamp)
            
    def _calculate_current_equity(self) -> float:
        """Calculate current equity including open positions"""
        return self.capital + sum(pos['size'] for pos in self.positions.values())
        
    def _calculate_results(self) -> BacktestResults:
        """Calculate backtest results"""
        if not self.trades:
            return self._get_default_results()
            
        successful_trades = sum(1 for t in self.trades if t['profit'] > 0)
        total_profit = sum(t['profit'] for t in self.trades)
        
        # Calculate max drawdown
        equity_array = np.array(self.equity_curve)
        peak = np.maximum.accumulate(equity_array)
        drawdown = (peak - equity_array) / peak
        max_drawdown = np.max(drawdown)
        
        # Calculate Sharpe ratio
        returns = np.diff(equity_array) / equity_array[:-1]
        sharpe = np.mean(returns) / np.std(returns) if len(returns) > 1 else 0
        
        return BacktestResults(
            total_trades=len(self.trades),
            successful_trades=successful_trades,
            total_profit=total_profit,
            win_rate=successful_trades / len(self.trades),
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            trades=self.trades,
            equity_curve=self.equity_curve,
            positions=list(self.positions.values())
        )
        
    def _get_default_results(self) -> BacktestResults:
        """Return default results when no trades are made"""
        return BacktestResults(
            total_trades=0,
            successful_trades=0,
            total_profit=0.0,
            win_rate=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            trades=[],
            equity_curve=[self.config.initial_capital],
            positions=[]
        )
        
    def _save_results(self, results: BacktestResults):
        """Save backtest results"""
        save_dir = Path('metrics/backtest')
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save summary
        with open(save_dir / 'summary.json', 'w') as f:
            summary = {
                'total_trades': results.total_trades,
                'successful_trades': results.successful_trades,
                'total_profit': results.total_profit,
                'win_rate': results.win_rate,
                'max_drawdown': results.max_drawdown,
                'sharpe_ratio': results.sharpe_ratio
            }
            json.dump(summary, f, indent=2)
            
        # Save detailed results with datetime conversion
        trades_json = []
        for trade in results.trades:
            trade_dict = trade.copy()
            trade_dict['entry_time'] = trade['entry_time'].isoformat()
            trade_dict['exit_time'] = trade['exit_time'].isoformat()
            trades_json.append(trade_dict)
            
        with open(save_dir / 'trades.json', 'w') as f:
            json.dump(trades_json, f, indent=2)
            
        # Save equity curve
        pd.Series(results.equity_curve).to_csv(save_dir / 'equity_curve.csv')

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Trading Strategy Backtester')
    
    parser.add_argument('--data', type=str,
                       help='Path to historical data file')
    parser.add_argument('--data-source', type=str, choices=['file', 'helius'],
                       default='file', help='Data source (file or Helius API)')
    parser.add_argument('--start-date', type=str, required=True,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, required=True,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--capital', type=float, default=100.0,
                       help='Initial capital')
    parser.add_argument('--risk', type=float, default=0.02,
                       help='Risk factor')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create config
    config = BacktestConfig(
        start_date=datetime.fromisoformat(f"{args.start_date}T00:00:00+00:00"),
        end_date=datetime.fromisoformat(f"{args.end_date}T23:59:59+00:00"),
        initial_capital=args.capital,
        risk_factor=args.risk,
        max_position_size=0.2,  # Increased from 0.1 for smaller capital
        min_position_size=0.01,
        max_positions=10,  # Increased from 5 to allow more concurrent trades
        slippage=0.02,
        data_source=args.data_source
    )
    
    # Run backtest
    try:
        engine = BacktestEngine(config)
        data_path = Path(args.data) if args.data else None
        asyncio.run(engine.run_backtest(data_path))
    except Exception as e:
        logging.error(f"Backtest failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
