import pytest
import asyncio
import json
import time
import psutil
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ..backtest import BacktestEngine, BacktestConfig
from ..trading_logic import TradingLogic
from ..helius_provider import HeliusDataProvider

def generate_large_dataset(num_events=1000):
    """Generate a large dataset for performance testing"""
    events = []
    base_time = datetime.now(tz=datetime.now().astimezone().tzinfo)

    # Generate pool creation events
    for i in range(num_events // 10):  # 10% are pool creations
        events.append(
            {
                "type": "pool_creation",
                "timestamp": base_time + timedelta(minutes=i * 10),
                "pool_id": f"pool{i}",
                "pool_data": {
                    "initial_liquidity": 1000000,
                    "price_impact": 0.01,
                    "creator_address": f"creator{i}",
                    "price": 1.0,
                },
            }
        )

    # Generate price updates
    for i in range(num_events - len(events)):
        pool_idx = i % (num_events // 10)
        events.append(
            {
                "type": "price_update",
                "timestamp": base_time + timedelta(minutes=i),
                "pool_id": f"pool{pool_idx}",
                "price": 1.0 + (i % 10) * 0.1,
            }
        )

    return sorted(events, key=lambda x: x["timestamp"])

@pytest.fixture
def mock_trading_logic():
    mock = AsyncMock(spec=TradingLogic)
    mock.evaluate_trading_opportunity.return_value = (True, 0.8, {"pool_metrics": {"liquidity": 1000000}})
    mock.execute_entry.return_value = {"status": "success", "position": MagicMock(entry_price=1.0)}
    mock._check_exit_conditions.return_value = True
    return mock

@pytest.fixture
def mock_helius_provider():
    mock = AsyncMock(spec=HeliusDataProvider)
    
    async def mock_get_historical_data(start_time, end_time):
        return [
            {
                "type": "pool_creation",
                "pool_id": "test_pool_1",
                "pool_data": {
                    "initial_liquidity": 1000000,
                    "price_impact": 0.01,
                    "creator_address": "test_creator_1",
                    "price": 1.0,
                },
                "token_address": "token1"
            },
            {
                "type": "pool_creation",
                "pool_id": "test_pool_2",
                "pool_data": {
                    "initial_liquidity": 2000000,
                    "price_impact": 0.02,
                    "creator_address": "test_creator_2",
                    "price": 2.0,
                },
                "token_address": "token2"
            }
        ]
    
    async def mock_get_pool_data(pool_id):
        return {
            "price": 1.5 if pool_id == "test_pool_1" else 2.5,
            "liquidity": 1000000,
        }
    
    mock.get_historical_data = mock_get_historical_data
    mock.get_pool_data = mock_get_pool_data
    return mock

@pytest.fixture
def backtest_config():
    """Create test backtest configuration"""
    return BacktestConfig(
        start_date=datetime.now(tz=datetime.now().astimezone().tzinfo) - timedelta(days=1),
        end_date=datetime.now(tz=datetime.now().astimezone().tzinfo),
        initial_capital=1000.0,
        trade_size=100.0,
        max_concurrent_positions=5,
        min_profit_threshold=0.02,
        max_loss_threshold=0.05,
        use_dynamic_sizing=True,
        include_failed_txs=False,
        max_slippage=0.02,
        min_liquidity=0.1
    )

def get_process_memory():
    """Get current process memory usage"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # Convert to MB

@pytest.mark.asyncio
async def test_execution_time(backtest_config, mock_trading_logic, mock_helius_provider):
    """Test execution time meets performance requirements"""
    engine = BacktestEngine(backtest_config, mock_trading_logic, mock_helius_provider)

    # Measure execution time
    start_time = time.time()
    results = await engine.run()
    execution_time = time.time() - start_time

    # Verify execution time is within limits (5.0 seconds for 1000 events)
    assert execution_time <= 5.0, f"Execution time {execution_time:.2f}s exceeds 5.0s limit"
    assert results.total_trades > 0, "No trades were executed"

    # Log performance metrics
    print(f"\nExecution time: {execution_time:.2f}s")
    print(f"Events processed: {len(results.trades)}")
    print(f"Events per second: {len(results.trades)/execution_time:.2f}")

@pytest.mark.asyncio
async def test_memory_usage(backtest_config, mock_trading_logic, mock_helius_provider):
    """Test memory usage meets performance requirements"""
    # Record initial memory usage
    initial_memory = get_process_memory()

    engine = BacktestEngine(backtest_config, mock_trading_logic, mock_helius_provider)
    results = await engine.run()

    # Record peak memory usage
    peak_memory = get_process_memory()
    memory_increase = peak_memory - initial_memory

    # Verify memory increase is within limits (100 MB)
    assert memory_increase <= 100, f"Memory increase {memory_increase:.2f}MB exceeds 100MB limit"
    assert results.total_trades > 0, "No trades were executed"

    # Log memory metrics
    print(f"\nInitial memory: {initial_memory:.2f}MB")
    print(f"Peak memory: {peak_memory:.2f}MB")
    print(f"Memory increase: {memory_increase:.2f}MB")

@pytest.mark.asyncio
async def test_operation_latency(backtest_config, mock_trading_logic, mock_helius_provider):
    """Test individual operation latency meets performance requirements"""
    engine = BacktestEngine(backtest_config, mock_trading_logic, mock_helius_provider)
    latencies = []

    # Patch key operations to measure latency
    original_process_transaction = engine._process_transaction

    async def measure_latency(tx_data):
        start_time = time.time()
        result = await original_process_transaction(tx_data)
        latency = (time.time() - start_time) * 1000  # Convert to ms
        latencies.append(latency)
        return result

    engine._process_transaction = measure_latency

    # Run backtest
    results = await engine.run()
    assert results.total_trades > 0, "No trades were executed"

    # Calculate latency statistics
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0

    # Verify latency is within limits (200ms)
    assert max_latency <= 200, f"Maximum latency {max_latency:.2f}ms exceeds 200ms limit"

    # Log latency metrics
    print(f"\nAverage latency: {avg_latency:.2f}ms")
    print(f"Maximum latency: {max_latency:.2f}ms")
    print(f"Total operations: {len(latencies)}")

@pytest.mark.asyncio
async def test_concurrent_processing(backtest_config, mock_trading_logic, mock_helius_provider):
    """Test performance with concurrent processing"""
    # Create multiple backtest instances
    num_instances = 3
    engines = [BacktestEngine(backtest_config, mock_trading_logic, mock_helius_provider) for _ in range(num_instances)]

    # Run backtests concurrently
    start_time = time.time()
    results = await asyncio.gather(*[engine.run() for engine in engines])
    execution_time = time.time() - start_time

    # Verify all instances completed successfully
    assert len(results) == num_instances
    for result in results:
        assert result.total_trades > 0, "No trades were executed"

    # Log concurrent processing metrics
    print(f"\nConcurrent execution time: {execution_time:.2f}s")
    print(f"Number of instances: {num_instances}")
    print(f"Average time per instance: {execution_time/num_instances:.2f}s")

@pytest.mark.asyncio
async def test_data_streaming_performance(backtest_config, mock_trading_logic, mock_helius_provider):
    """Test performance of data streaming and processing"""
    engine = BacktestEngine(backtest_config, mock_trading_logic, mock_helius_provider)
    processed_events = 0
    stream_start_time = time.time()

    # Track event processing rate
    async def count_events(tx_data):
        nonlocal processed_events
        processed_events += 1
        return await engine._process_transaction(tx_data)

    engine._process_transaction = count_events

    # Run backtest
    results = await engine.run()
    assert results.total_trades > 0, "No trades were executed"

    processing_time = time.time() - stream_start_time
    events_per_second = processed_events / processing_time if processing_time > 0 else 0

    # Log streaming metrics
    print(f"\nEvents processed: {processed_events}")
    print(f"Processing time: {processing_time:.2f}s")
    print(f"Events per second: {events_per_second:.2f}")

    # Verify processing rate is acceptable (subjective threshold)
    assert events_per_second >= 100, f"Processing rate {events_per_second:.2f} events/s below threshold"

@pytest.mark.asyncio
async def test_memory_cleanup(backtest_config, mock_trading_logic, mock_helius_provider):
    """Test memory is properly cleaned up after backtest"""
    initial_memory = get_process_memory()

    # Run multiple backtest iterations
    for _ in range(3):
        engine = BacktestEngine(backtest_config, mock_trading_logic, mock_helius_provider)
        results = await engine.run()
        assert results.total_trades > 0, "No trades were executed"

        # Force garbage collection
        import gc
        gc.collect()

    final_memory = get_process_memory()
    memory_diff = final_memory - initial_memory

    # Verify memory is properly cleaned up
    assert memory_diff <= 10, f"Memory not properly cleaned up. Difference: {memory_diff:.2f}MB"

    # Log cleanup metrics
    print(f"\nInitial memory: {initial_memory:.2f}MB")
    print(f"Final memory: {final_memory:.2f}MB")
    print(f"Memory difference: {memory_diff:.2f}MB")
