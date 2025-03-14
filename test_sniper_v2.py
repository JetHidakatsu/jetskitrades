"""
Test script for the improved memecoin sniper implementation
"""

import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from env.latency_tracker import LatencyTracker
from env.pool_validator import PoolValidator
from env.transaction_executor_v2 import TransactionExecutorV2, TransactionConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main test execution function"""
    logger.info("Starting memecoin sniper v2 test")

    # Initialize components
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    latency_tracker = LatencyTracker()
    pool_validator = PoolValidator(client)

    # Initialize transaction executor with custom config
    config = TransactionConfig(
        max_retries=3,
        retry_delay=1.0,
        timeout=30.0,
        max_priority_fee=0.000001,
        min_priority_fee=0.0000001,
        dynamic_fee_multiplier=1.5,
        memecoin_fee_multiplier=2.0,
    )

    executor = TransactionExecutorV2(
        client=client,
        latency_tracker=latency_tracker,
        pool_validator=pool_validator,
        config=config,
    )

    # Simulate some trades for testing
    for i in range(3):
        logger.info(f"\nExecuting test trade {i+1}/3")

        # Example trade parameters
        success = await executor.execute_swap(
            pool_id=f"pool_{i}",
            amount=0.1,
            slippage=0.01,
            priority_fee=0.000001,
            max_fee=0.0001,
        )

        if not success:
            logger.error(f"Test trade {i+1} - ERROR: Transaction failed")
            logger.info("Checking error counts:")
            metrics = executor.get_performance_metrics()
            for error_type, count in metrics["error_counts"].items():
                logger.info(f"- {error_type}: {count} occurrences")

    # Print final results
    metrics = executor.get_performance_metrics()
    logger.info("\n=== Test Results ===")
    logger.info(f"Success Rate: {metrics['success_rate']*100:.1f}%")
    logger.info(f"Average Latency: {metrics['avg_latency']:.2f}s")
    logger.info(f"Total Transactions: {metrics['recent_transaction_count']}")
    logger.info("\nError Distribution:")
    for error_type, count in metrics["error_counts"].items():
        logger.info(f"- {error_type}: {count} occurrences")

    # Cleanup
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
