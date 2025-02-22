#!/usr/bin/env python3
"""Main entry point for the Solana trading bot"""

import asyncio
import argparse
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
import os

from env.trading_bot import TradingBot
from env.quantum_pool_selector import QuantumPoolSelector
from env.sentiment_analyzer import SentimentAnalyzer
from env.latency_tracker import LatencyTracker
from env.trading_logic import TradingLogic, TradingParameters
from simulate import SimulationConfig, SimulationEngine
from backtest import BacktestConfig, BacktestEngine
from monitor import PerformanceMonitor

# Global bot instance for signal handling
bot: Optional[TradingBot] = None

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
        
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Force reconfiguration of the root logger
    )
    
    # Create logger for main module
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Add debug message
    logger.debug("Logging system initialized")
    return logger

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Quantum-enhanced Solana Trading Bot')
    
    parser.add_argument(
        '--mode',
        choices=['live', 'simulate', 'backtest'],
        default='live',
        help='Trading mode (default: live)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        default=100.0,
        help='Initial capital in SOL (default: 100)'
    )
    
    parser.add_argument(
        '--risk',
        type=float,
        default=0.02,
        help='Risk percentage per trade (default: 0.02)'
    )
    
    # Simulation mode arguments
    parser.add_argument(
        '--duration',
        type=int,
        default=24,
        help='Simulation duration in hours (default: 24)'
    )
    
    parser.add_argument(
        '--pools',
        type=int,
        default=50,
        help='Number of pools to simulate (default: 50)'
    )
    
    parser.add_argument(
        '--volatility',
        type=float,
        default=0.02,
        help='Price volatility factor (default: 0.02)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for simulation'
    )
    
    # Backtest mode arguments
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory containing historical data'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for backtesting (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for backtesting (YYYY-MM-DD)'
    )
    
    return parser.parse_args()

async def run_bot(args):
    """Run the trading bot with specified arguments"""
    global bot
    
    try:
        if args.mode == 'live':
            await run_live_mode(args)
        elif args.mode == 'simulate':
            await run_simulation_mode(args)
        else:  # backtest
            await run_backtest_mode(args)
            
    except Exception as e:
        logging.error(f"Error running bot: {e}")
        if bot:
            await bot.stop()
        sys.exit(1)

async def run_live_mode(args):
    """Run bot in live trading mode"""
    global bot
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting bot in live trading mode")
    
    try:
        # Initialize bot
        logger.debug("Initializing trading bot...")
        bot = TradingBot()
        
        # Update configuration
        logger.debug(f"Configuring bot with capital: {args.capital} SOL")
        bot.total_capital = args.capital
        bot.available_capital = args.capital
        bot.risk_percentage = args.risk
        
        # Validate configuration
        logger.debug("Validating configuration...")
        from env.config import validate_config
        if not validate_config():
            raise ValueError("Configuration validation failed")
        
        # Start bot
        logger.debug("Starting bot operation...")
        await bot.start()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}", exc_info=True)
        raise

async def run_simulation_mode(args):
    """Run bot in simulation mode"""
    logging.info("Starting bot in simulation mode")
    
    # Create simulation config
    config = SimulationConfig(
        duration_hours=args.duration,
        initial_capital=args.capital,
        num_pools=args.pools,
        price_volatility=args.volatility,
        random_seed=args.seed
    )
    
    # Initialize components
    quantum_selector = QuantumPoolSelector()
    sentiment_analyzer = SentimentAnalyzer()
    latency_tracker = LatencyTracker()
    
    # Create trading logic with simulation parameters
    trading_logic = TradingLogic(
        quantum_selector,
        sentiment_analyzer,
        None,  # No transaction executor needed for simulation
        latency_tracker,
        TradingParameters(
            max_position_size=0.1,
            min_position_size=0.01,
            risk_factor=args.risk,
            max_slippage=0.02,
            min_liquidity=1000,
            sentiment_threshold=0.6
        )
    )
    
    # Create and run simulation
    engine = SimulationEngine(config, trading_logic, latency_tracker)
    await engine.run_simulation()
    
    # Start performance monitor
    monitor = PerformanceMonitor()
    await monitor.start_monitoring()

async def run_backtest_mode(args):
    """Run bot in backtest mode"""
    logging.info("Starting bot in backtest mode")
    
    if not args.start_date or not args.end_date:
        logging.error("Start and end dates required for backtesting")
        sys.exit(1)
        
    # Create backtest config
    config = BacktestConfig(
        start_date=datetime.strptime(args.start_date, '%Y-%m-%d'),
        end_date=datetime.strptime(args.end_date, '%Y-%m-%d'),
        initial_capital=args.capital,
        risk_factor=args.risk
    )
    
    # Initialize components
    quantum_selector = QuantumPoolSelector()
    sentiment_analyzer = SentimentAnalyzer()
    latency_tracker = LatencyTracker()
    
    trading_logic = TradingLogic(
        quantum_selector,
        sentiment_analyzer,
        None,
        latency_tracker,
        TradingParameters()
    )
    
    # Run backtest
    engine = BacktestEngine(config, trading_logic, latency_tracker)
    await engine.run_backtest(Path(args.data_dir))

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logging.info("Shutdown signal received")
    if bot:
        # Schedule bot shutdown in the event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(shutdown())
        else:
            loop.run_until_complete(shutdown())

async def shutdown():
    """Perform graceful shutdown"""
    global bot
    if bot:
        await bot.stop()
        bot = None
    
    # Stop the event loop
    loop = asyncio.get_event_loop()
    loop.stop()

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    log_file = f"trading_bot_{args.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging(args.log_level, log_file)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Run bot
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot(args))
    except KeyboardInterrupt:
        logging.info("Manual shutdown initiated")
        if bot:
            loop.run_until_complete(bot.stop())
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if bot:
            loop.run_until_complete(bot.stop())
        sys.exit(1)
    finally:
        loop.close()

if __name__ == "__main__":
    main()
