"""Example usage of sandbox environment for testing trading strategies"""

import asyncio
import logging
from datetime import datetime
import json

from mock_components import (
    MockClient,
    MockLatencyTracker,
    MockPoolValidator,
    MockTransactionExecutor,
    MockQuantumPoolSelector,
    MockSentimentAnalyzer,
    MockMempoolMonitor,
    MockTradingParameters,
    MockTradeMetrics,
    MockPoolMetrics,
)

from env.sandbox_environment import (
    SandboxEnvironment,
    SandboxConfig,
    EnhancedJSONEncoder,
)
from env.trading_logic_v2 import TradingLogic


async def run_sandbox_test():
    """Run a sample trading strategy in the sandbox"""

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize mock components
    client = MockClient()
    latency_tracker = MockLatencyTracker()
    pool_validator = MockPoolValidator()

    # Initialize trading components
    quantum_selector = MockQuantumPoolSelector()
    sentiment_analyzer = MockSentimentAnalyzer()
    transaction_executor = MockTransactionExecutor(
        client=client, latency_tracker=latency_tracker, pool_validator=pool_validator
    )

    mempool_monitor = MockMempoolMonitor(
        websocket_url="ws://localhost:8899",
        latency_tracker=latency_tracker,
        pool_validator=pool_validator,
    )

    # Initialize trading logic with mock parameters
    trading_params = MockTradingParameters()

    trading_logic = TradingLogic(
        quantum_selector=quantum_selector,
        sentiment_analyzer=sentiment_analyzer,
        transaction_executor=transaction_executor,
        pool_validator=pool_validator,
        latency_tracker=latency_tracker,
        mempool_monitor=mempool_monitor,
        params=trading_params,
    )

    # Configure sandbox
    sandbox_config = SandboxConfig(
        initial_balance=0.12,
        max_slippage=0.05,
        simulated_gas_price=0.000001,
        transaction_delay=0.1,
        fail_rate=0.02,
        price_impact_factor=1.0,
        liquidity_factor=1.0,
        mempool_simulation=True,
        record_transactions=True,
    )

    # Initialize sandbox
    sandbox = SandboxEnvironment(
        trading_logic=trading_logic,
        config=sandbox_config,
        log_file="sandbox_trades.log",
    )

    try:
        logger.info("Starting sandbox trading simulation...")

        # Simulate a series of trades
        for i in range(5):
            # Simulate pool discovery
            pool_id = f"test_pool_{i}"

            # Update pool state with different characteristics
            await sandbox.update_pool_state(
                pool_id,
                {
                    "liquidity": 0.1 * (i + 1),
                    "volume_24h": 0.05 * (i + 1),
                    "price_impact": 0.01 / (i + 1),
                    "holder_count": 10 * (i + 1),
                    "creator_score": min(0.7 + (i * 0.1), 1.0),
                    "time_since_creation": 3600,
                    "depth_scores": {
                        "buy_depth": min(0.8 + (i * 0.05), 1.0),
                        "sell_depth": min(0.7 + (i * 0.05), 1.0),
                    },
                },
            )

            # Execute buy trade
            logger.info(f"Executing buy trade for pool {pool_id}")
            buy_result = await sandbox.execute_trade(
                pool_id=pool_id, size=0.01, is_buy=True  # 0.01 SOL
            )
            logger.info(
                f"Buy result: {json.dumps(buy_result, indent=2, cls=EnhancedJSONEncoder)}"
            )

            # Simulate market movement
            await asyncio.sleep(1)

            # Execute sell trade
            logger.info(f"Executing sell trade for pool {pool_id}")
            sell_result = await sandbox.execute_trade(
                pool_id=pool_id, size=0.01, is_buy=False  # 0.01 SOL
            )
            logger.info(
                f"Sell result: {json.dumps(sell_result, indent=2, cls=EnhancedJSONEncoder)}"
            )

            # Get current metrics
            metrics = sandbox.get_metrics()
            logger.info(
                f"Current metrics: {json.dumps(metrics, indent=2, cls=EnhancedJSONEncoder)}"
            )

            await asyncio.sleep(1)

        # Save transaction history
        sandbox.save_transaction_history("sandbox_history.json")

        # Final metrics
        final_metrics = sandbox.get_metrics()
        logger.info("Final sandbox metrics:")
        logger.info(json.dumps(final_metrics, indent=2, cls=EnhancedJSONEncoder))

    except Exception as e:
        logger.error(f"Error in sandbox simulation: {e}")
        raise  # Re-raise to see full traceback
    finally:
        # Reset sandbox state
        sandbox.reset()
        # Close client connection
        await client.close()


def main():
    """Main entry point"""
    asyncio.run(run_sandbox_test())


if __name__ == "__main__":
    main()
