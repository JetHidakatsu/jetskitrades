import pytest
import asyncio
import json
import time
import psutil
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from backtest import BacktestEngine, BacktestConfig


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
def large_data_file(tmp_path):
    """Create a large test data file"""
    data_file = tmp_path / "large_test_data.json"
    events = generate_large_dataset()
    with open(data_file, "w") as f:
        json.dump({"events": events}, f, default=str)
    return data_file


@pytest.fixture
def backtest_config():
    """Create test backtest configuration"""
    return BacktestConfig(
        start_date=datetime.now(tz=datetime.now().astimezone().tzinfo)
        - timedelta(days=1),
        end_date=datetime.now(tz=datetime.now().astimezone().tzinfo),
        initial_capital=1000.0,
        risk_factor=0.02,
        max_position_size=0.1,
        min_position_size=0.01,
        max_positions=5,
        slippage=0.02,
        use_helius=False,
        data_source="file",
    )


def get_process_memory():
    """Get current process memory usage"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # Convert to MB


@pytest.mark.asyncio
async def test_execution_time(large_data_file, backtest_config):
    """Test execution time meets performance requirements"""
    engine = BacktestEngine(backtest_config)

    # Measure execution time
    start_time = time.time()
    results = await engine.run_backtest(large_data_file)
    execution_time = time.time() - start_time

    # Verify execution time is within limits (5.0 seconds for 1000 events)
    assert (
        execution_time <= 5.0
    ), f"Execution time {execution_time:.2f}s exceeds 5.0s limit"

    # Log performance metrics
    print(f"\nExecution time: {execution_time:.2f}s")
    print(f"Events processed: {len(results.trades)}")
    print(f"Events per second: {len(results.trades)/execution_time:.2f}")


@pytest.mark.asyncio
async def test_memory_usage(large_data_file, backtest_config):
    """Test memory usage meets performance requirements"""
    # Record initial memory usage
    initial_memory = get_process_memory()

    engine = BacktestEngine(backtest_config)
    results = await engine.run_backtest(large_data_file)

    # Record peak memory usage
    peak_memory = get_process_memory()
    memory_increase = peak_memory - initial_memory

    # Verify memory increase is within limits (100 MB)
    assert (
        memory_increase <= 100
    ), f"Memory increase {memory_increase:.2f}MB exceeds 100MB limit"

    # Log memory metrics
    print(f"\nInitial memory: {initial_memory:.2f}MB")
    print(f"Peak memory: {peak_memory:.2f}MB")
    print(f"Memory increase: {memory_increase:.2f}MB")


@pytest.mark.asyncio
async def test_operation_latency(large_data_file, backtest_config):
    """Test individual operation latency meets performance requirements"""
    engine = BacktestEngine(backtest_config)
    latencies = []

    # Patch key operations to measure latency
    original_process_event = engine._process_event

    async def measure_latency(event, trading_logic):
        start_time = time.time()
        result = await original_process_event(event, trading_logic)
        latency = (time.time() - start_time) * 1000  # Convert to ms
        latencies.append(latency)
        return result

    engine._process_event = measure_latency

    # Run backtest
    await engine.run_backtest(large_data_file)

    # Calculate latency statistics
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    # Verify latency is within limits (200ms)
    assert (
        max_latency <= 200
    ), f"Maximum latency {max_latency:.2f}ms exceeds 200ms limit"

    # Log latency metrics
    print(f"\nAverage latency: {avg_latency:.2f}ms")
    print(f"Maximum latency: {max_latency:.2f}ms")
    print(f"Total operations: {len(latencies)}")


@pytest.mark.asyncio
async def test_concurrent_processing(large_data_file, backtest_config):
    """Test performance with concurrent processing"""
    # Create multiple backtest instances
    num_instances = 3
    engines = [BacktestEngine(backtest_config) for _ in range(num_instances)]

    # Run backtests concurrently
    start_time = time.time()
    results = await asyncio.gather(
        *[engine.run_backtest(large_data_file) for engine in engines]
    )
    execution_time = time.time() - start_time

    # Verify all instances completed successfully
    assert len(results) == num_instances
    for result in results:
        assert result.total_trades > 0

    # Log concurrent processing metrics
    print(f"\nConcurrent execution time: {execution_time:.2f}s")
    print(f"Number of instances: {num_instances}")
    print(f"Average time per instance: {execution_time/num_instances:.2f}s")


@pytest.mark.asyncio
async def test_success_rate(large_data_file, backtest_config):
    """Test trading success rate meets performance requirements"""
    engine = BacktestEngine(backtest_config)
    results = await engine.run_backtest(large_data_file)

    # Calculate success rate
    if results.total_trades > 0:
        success_rate = (results.successful_trades / results.total_trades) * 100

        # Verify success rate is within acceptable range (>= 90%)
        assert (
            success_rate >= 90
        ), f"Success rate {success_rate:.2f}% below 90% requirement"

        # Log success metrics
        print(f"\nSuccess rate: {success_rate:.2f}%")
        print(f"Total trades: {results.total_trades}")
        print(f"Successful trades: {results.successful_trades}")


@pytest.mark.asyncio
async def test_data_streaming_performance(large_data_file, backtest_config):
    """Test performance of data streaming and processing"""
    engine = BacktestEngine(backtest_config)
    processed_events = 0
    stream_start_time = time.time()

    # Track event processing rate
    async def count_events(event, trading_logic):
        nonlocal processed_events
        processed_events += 1
        return await engine._process_event(event, trading_logic)

    engine._process_event = count_events

    # Run backtest
    results = await engine.run_backtest(large_data_file)

    processing_time = time.time() - stream_start_time
    events_per_second = processed_events / processing_time

    # Log streaming metrics
    print(f"\nEvents processed: {processed_events}")
    print(f"Processing time: {processing_time:.2f}s")
    print(f"Events per second: {events_per_second:.2f}")

    # Verify processing rate is acceptable (subjective threshold)
    assert (
        events_per_second >= 100
    ), f"Processing rate {events_per_second:.2f} events/s below threshold"


@pytest.mark.asyncio
async def test_memory_cleanup(large_data_file, backtest_config):
    """Test memory is properly cleaned up after backtest"""
    initial_memory = get_process_memory()

    # Run multiple backtest iterations
    for _ in range(3):
        engine = BacktestEngine(backtest_config)
        await engine.run_backtest(large_data_file)

        # Force garbage collection
        import gc

        gc.collect()

    final_memory = get_process_memory()
    memory_diff = final_memory - initial_memory

    # Verify memory is properly cleaned up
    assert (
        memory_diff <= 10
    ), f"Memory not properly cleaned up. Difference: {memory_diff:.2f}MB"

    # Log cleanup metrics
    print(f"\nInitial memory: {initial_memory:.2f}MB")
    print(f"Final memory: {final_memory:.2f}MB")
    print(f"Memory difference: {memory_diff:.2f}MB")
