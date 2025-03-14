"""Test new bot components with fixes"""

import asyncio
from datetime import datetime
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.transaction import Transaction
from solana.system_program import TransactionInstruction

from env.distribution_analyzer import DistributionAnalyzer, DistributionConfig
from env.liquidity_analyzer import LiquidityAnalyzer, LiquidityConfig
from env.arbitrage_engine import ArbitrageEngine, ArbitrageConfig
from env.websocket_manager import WebSocketManager
from env.priority_fee_calculator import PriorityFeeCalculator


async def setup_client():
    """Setup RPC client"""
    return AsyncClient(
        endpoint="https://api.mainnet-beta.solana.com",
        commitment=Commitment("confirmed"),
    )


async def test_distribution(client):
    """Test distribution analysis"""
    print("\nTesting Distribution Analysis...")

    config = DistributionConfig(
        top_holder_count=20,
        min_gini_coefficient=0.5,
        max_whale_percentage=0.1,
        analysis_window=3600,
        update_interval=60,
        heatmap_resolution=100,
        historical_samples=1000,
    )
    analyzer = DistributionAnalyzer(client, config)

    # Test token (BONK)
    token_pubkey = Pubkey.from_string("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")

    try:
        # Update distribution
        await analyzer.update_distribution(token_pubkey)

        # Get summary
        summary = analyzer.get_distribution_summary(str(token_pubkey))

        print(f"Gini Coefficient: {summary['gini_coefficient']:.3f}")
        print(f"Whale Percentage: {summary['whale_percentage']:.3f}")
        print(f"Distribution Score: {summary['distribution_score']:.3f}")
        print(f"Top Holders: {len(summary['top_holders'])}")

        return True
    except Exception as e:
        print(f"Distribution test error: {e}")
        return False


async def test_liquidity(client):
    """Test liquidity analysis"""
    print("\nTesting Liquidity Analysis...")

    config = LiquidityConfig(
        min_locked_ratio=0.3,
        min_depth_ratio=0.8,
        max_slippage=0.02,
        min_growth_rate=0.01,
        analysis_window=3600,
        update_interval=60,
        test_amount=1000,
        depth_range=0.02,
    )
    analyzer = LiquidityAnalyzer(client, config)

    # Test pool (BONK/SOL)
    token_pubkey = Pubkey.from_string("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")
    pool_pubkey = Pubkey.from_string("8PhnCfgqpgFM7ZJvttGdBVMXHuU4Q23ACxCvWkbs1M71")

    try:
        # Update liquidity
        await analyzer.update_liquidity(str(token_pubkey), str(pool_pubkey))

        # Get summary
        summary = analyzer.get_liquidity_summary(str(token_pubkey))

        print(f"Locked Ratio: {summary['locked_ratio']:.3f}")
        print(f"Depth Ratio: {summary['depth_ratio']:.3f}")
        print(f"Average Slippage: {summary['avg_slippage']:.3f}")
        print(f"Growth Score: {summary['growth_score']:.3f}")
        print(f"Overall Score: {summary['overall_score']:.3f}")

        return True
    except Exception as e:
        print(f"Liquidity test error: {e}")
        return False


async def test_arbitrage(client):
    """Test arbitrage engine"""
    print("\nTesting Arbitrage Engine...")

    # Initialize WebSocket manager
    ws_manager = WebSocketManager(urls=["wss://api.mainnet-beta.solana.com"])

    # Initialize fee calculator
    fee_calculator = PriorityFeeCalculator(client)

    config = ArbitrageConfig(
        min_profit_threshold=0.002,
        max_path_length=3,
        price_update_interval=1,
        execution_timeout=2,
        max_slippage=0.01,
        min_liquidity=10000,
    )
    engine = ArbitrageEngine(client, ws_manager, fee_calculator, config)

    # Test pools
    pools = [
        # USDC/SOL, SOL/BONK, BONK/USDC
        (
            "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2",
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "So11111111111111111111111111111111111111112",
        ),
        (
            "8PhnCfgqpgFM7ZJvttGdBVMXHuU4Q23ACxCvWkbs1M71",
            "So11111111111111111111111111111111111111112",
            "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        ),
        (
            "9vqYJjDUFecLL2xPUC4Rc7hyCtZ6iJ4mDiVZX7aFXoAe",
            "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        ),
    ]

    try:
        # Start monitoring
        monitor_task = asyncio.create_task(engine.start_monitoring(pools))

        # Wait for updates
        await asyncio.sleep(5)

        # Get metrics
        metrics = engine.get_performance_metrics()

        print(f"Average Execution Time: {metrics['avg_execution_time']:.3f}s")
        print(f"Success Rate: {metrics['success_rate']:.3f}")
        print(f"Total Executions: {metrics['total_executions']}")
        print(f"Unique Paths: {metrics['unique_paths']}")

        # Stop monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        return True
    except Exception as e:
        print(f"Arbitrage test error: {e}")
        return False
    finally:
        await ws_manager.close()


async def main():
    """Run component tests"""
    print("Starting Component Tests...")

    # Setup shared client
    client = await setup_client()

    try:
        # Test distribution analysis
        dist_success = await test_distribution(client)
        print(f"Distribution Analysis: {'✓' if dist_success else '✗'}")

        # Test liquidity analysis
        liq_success = await test_liquidity(client)
        print(f"Liquidity Analysis: {'✓' if liq_success else '✗'}")

        # Test arbitrage engine
        arb_success = await test_arbitrage(client)
        print(f"Arbitrage Engine: {'✓' if arb_success else '✗'}")

        print("\nTest Summary:")
        print(f"Total Tests: 3")
        print(f"Passed: {sum([dist_success, liq_success, arb_success])}")
        print(f"Failed: {3 - sum([dist_success, liq_success, arb_success])}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
