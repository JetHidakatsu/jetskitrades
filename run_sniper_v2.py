#!/usr/bin/env python3
"""Memecoin Sniper Strategy Runner (Version 2)"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os
import signal
import sys

from solana.rpc.async_api import AsyncClient
from env.trading_bot import TradingBot
from env.quantum_pool_selector import QuantumPoolSelector, PoolMetrics
from env.sentiment_analyzer import SentimentAnalyzer
from env.latency_tracker import LatencyTracker
from env.trading_logic import TradingLogic, TradingParameters
from env.monitor_simple import SimplePerformanceMonitor, setup_monitor
from env.transaction_executor import TransactionExecutor
from env.pool_validator import PoolValidator

# Global bot instance
bot: Optional[TradingBot] = None
trades_completed = 0
total_profit = 0.0
moonbag_positions: Dict[str, float] = {}

def setup_logging():
    """Setup logging configuration"""
    log_file = f"sniper_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger(__name__)

async def execute_trade(trading_logic: TradingLogic, pool_metrics: PoolMetrics) -> Dict[str, Any]:
    """Execute a single trade with the sniper strategy"""
    global trades_completed, total_profit, moonbag_positions
    
    try:
        # Calculate position size (3% of available capital)
        position_size = trading_logic.params.initial_capital * 0.03
        
        # Execute entry
        result = await trading_logic.execute_entry(
            pool_id=f"pool_{trades_completed}",
            position_size=position_size,
            pool_metrics=pool_metrics
        )
        
        if result['status'] == 'success':
            position = result['position']
            moonbag_size = position.moonbag_size
            
            # Simulate price movement (70% chance of profit)
            if trades_completed % 3 != 0:  # Profitable trade
                current_price = pool_metrics.price_impact * 1.6  # 60% gain
                exit_result = await trading_logic.manage_position(
                    pool_id=f"pool_{trades_completed}",
                    current_price=current_price,
                    pool_metrics=pool_metrics
                )
                
                if exit_result and exit_result['status'] == 'take_profit':
                    # Calculate profit
                    exit_size = position.position_size - moonbag_size
                    profit = exit_size * 0.5  # 50% gain on exit portion
                    total_profit += profit
                    
                    # Track moonbag
                    moonbag_positions[f"pool_{trades_completed}"] = moonbag_size
                    
                    return {
                        'status': 'take_profit',
                        'profit': profit,
                        'moonbag': moonbag_size
                    }
                
            else:  # Stop loss trade
                current_price = pool_metrics.price_impact * 0.7  # 30% drop
                exit_result = await trading_logic.manage_position(
                    pool_id=f"pool_{trades_completed}",
                    current_price=current_price,
                    pool_metrics=pool_metrics
                )
                
                if exit_result and exit_result['status'] == 'stop_loss':
                    # Calculate loss
                    loss = position.position_size * 0.2  # 20% loss
                    total_profit -= loss
                    
                    return {
                        'status': 'stop_loss',
                        'loss': loss,
                        'moonbag': 0
                    }
        
        return {
            'status': 'error',
            'error': result.get('error', 'Unknown error')
        }
            
    except Exception as e:
        logging.error(f"Error executing trade: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

async def run_sniper_strategy():
    """Run the memecoin sniper strategy for 10 trades"""
    global bot, trades_completed
    
    logger = logging.getLogger(__name__)
    logger.info("Starting memecoin sniper strategy")
    
    try:
        # Initialize Solana client
        rpc_url = os.getenv('QUICKNODE_RPC_URL')
        solana_client = AsyncClient(rpc_url)
        
        # Initialize components
        quantum_selector = QuantumPoolSelector()
        sentiment_analyzer = SentimentAnalyzer()
        latency_tracker = LatencyTracker()
        pool_validator = PoolValidator(client=solana_client)
        
        # Initialize transaction executor with dependencies
        transaction_executor = TransactionExecutor(
            client=solana_client,
            latency_tracker=latency_tracker,
            pool_validator=pool_validator
        )
        
        # Initialize trading logic with memecoin parameters
        trading_logic = TradingLogic(
            quantum_selector=quantum_selector,
            sentiment_analyzer=sentiment_analyzer,
            transaction_executor=transaction_executor,
            pool_validator=pool_validator,
            latency_tracker=latency_tracker,
            params=TradingParameters(
                initial_capital=0.12,  # 0.12 SOL
                max_position_size=0.05,  # 5% max position
                min_position_size=0.01,  # 1% min position
                risk_factor=0.4,        # Conservative risk
                max_slippage=0.05,      # 5% max slippage
                min_liquidity=0.01,     # 0.01 SOL min liquidity
                moonbag_pct=0.15        # 15% moonbag
            )
        )
        
        # Initialize bot
        bot = TradingBot()
        bot.trading_logic = trading_logic
        
        # Start performance monitor
        monitor = setup_monitor()
        monitor_task = asyncio.create_task(monitor.start())
        
        # Execute 10 trades
        while trades_completed < 10:
            logger.info(f"\nExecuting trade {trades_completed + 1}/10")
            
            # Create sample pool metrics
            pool_metrics = PoolMetrics(
                liquidity=0.1,
                volume_24h=0.05,
                price_impact=0.02,
                holder_count=10,
                creator_score=0.8,
                time_since_creation=1.0,
                depth_scores={"depth1": 0.5},
                market_conditions=None,
                total_supply=1000000.0,
                quantum_score=0.85
            )
            
            # Execute trade
            result = await execute_trade(trading_logic, pool_metrics)
            
            # Log results
            if result['status'] == 'take_profit':
                logger.info(f"Trade {trades_completed + 1} - PROFIT: {result['profit']:.4f} SOL")
                logger.info(f"Moonbag retained: {result['moonbag']:.4f} SOL")
            elif result['status'] == 'stop_loss':
                logger.info(f"Trade {trades_completed + 1} - LOSS: {result['loss']:.4f} SOL")
            else:
                logger.error(f"Trade {trades_completed + 1} - ERROR: {result.get('error', 'Unknown error')}")
            
            trades_completed += 1
            
            # Add small delay between trades
            await asyncio.sleep(1)
        
        # Print final results
        logger.info("\n=== Final Results ===")
        logger.info(f"Total Profit/Loss: {total_profit:.4f} SOL")
        logger.info(f"Active Moonbag Positions: {len(moonbag_positions)}")
        logger.info(f"Total Moonbag Value: {sum(moonbag_positions.values()):.4f} SOL")
        logger.info(f"Win Rate: {(len(moonbag_positions) / 10) * 100:.1f}%")
        
        # Cancel monitor task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # Close Solana client
        await solana_client.close()
        
    except Exception as e:
        logger.error(f"Strategy execution failed: {str(e)}", exc_info=True)
        raise
    finally:
        if bot:
            await bot.stop()

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logging.info("Shutdown signal received")
    if bot:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(bot.stop())
        else:
            loop.run_until_complete(bot.stop())

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logging()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_sniper_strategy())
    except KeyboardInterrupt:
        logger.info("Manual shutdown initiated")
        if bot:
            loop.run_until_complete(bot.stop())
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if bot:
            loop.run_until_complete(bot.stop())
        sys.exit(1)
    finally:
        loop.close()

if __name__ == "__main__":
    main()
