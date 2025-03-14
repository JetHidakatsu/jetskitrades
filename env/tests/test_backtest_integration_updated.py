import pytest
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from env.backtest import BacktestEngine, BacktestConfig
from env.quantum_pool_selector import QuantumPoolSelector, PoolMetrics
from env.trading_logic_updated import TradingLogic, TradingParameters
from env.pool_validator import PoolValidator


@pytest.fixture
def mock_historical_data():
    """Create mock historical trading data"""
    return [
        {
            "type": "pool_creation",
            "timestamp": datetime.now(tz=datetime.now().astimezone().tzinfo),
            "pool_id": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # Valid Base58 string
            "pool_data": {
                "initial_liquidity": 1000000,
                "price_impact": 0.01,
                "creator_address": "creator123",
                "price": 1.0,
            },
        },
        {
            "type": "price_update",
            "timestamp": datetime.now(tz=datetime.now().astimezone().tzinfo)
            + timedelta(minutes=5),
            "pool_id": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            "price": 1.2,
        },
        {
            "type": "price_update",
            "timestamp": datetime.now(tz=datetime.now().astimezone().tzinfo)
            + timedelta(minutes=10),
            "pool_id": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            "price": 1.5,
        },
    ]


@pytest.fixture
def mock_data_file(tmp_path, mock_historical_data):
    """Create temporary data file with mock data"""
    data_file = tmp_path / "test_data.json"
    with open(data_file, "w") as f:
        json.dump({"events": mock_historical_data}, f, default=str)
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


@pytest.mark.asyncio
async def test_component_integration(mock_data_file, backtest_config):
    """Test integration between different components"""
    with patch("env.quantum_pool_selector.QuantumPoolSelector") as mock_selector:
        selector_instance = mock_selector.return_value
        selector_instance.score_pool = MagicMock(return_value=0.8)

        with patch("env.sentiment_analyzer.SentimentAnalyzer") as mock_analyzer:
            analyzer_instance = mock_analyzer.return_value
            analyzer_instance.analyze_sentiment = AsyncMock(return_value=0.7)

            with patch("env.pool_validator.PoolValidator") as mock_validator:
                validator_instance = mock_validator.return_value
                validator_instance.validate_pool = AsyncMock(return_value=True)

                # Create and run backtest engine
                engine = BacktestEngine(backtest_config)
                results = await engine.run_backtest(mock_data_file)

                # Verify component interactions
                assert selector_instance.score_pool.called
                assert analyzer_instance.analyze_sentiment.called
                assert validator_instance.validate_pool.called

                # Verify trading decisions were made
                assert results.total_trades > 0
                assert len(results.trades) == results.total_trades


@pytest.mark.asyncio
async def test_data_flow_integration(mock_data_file, backtest_config):
    """Test data flow through the system"""
    engine = BacktestEngine(backtest_config)

    # Track event processing
    processed_events = []
    original_process_event = engine._process_event

    async def mock_process_event(event, trading_logic):
        processed_events.append(event)
        await original_process_event(event, trading_logic)

    engine._process_event = mock_process_event

    # Run backtest
    results = await engine.run_backtest(mock_data_file)

    # Verify event processing
    assert len(processed_events) > 0
    assert any(event["type"] == "pool_creation" for event in processed_events)
    assert any(event["type"] == "price_update" for event in processed_events)

    # Verify results calculation
    assert isinstance(results.total_profit, float)
    assert isinstance(results.win_rate, float)
    assert len(results.equity_curve) > 0


@pytest.mark.asyncio
async def test_position_management_integration(mock_data_file, backtest_config):
    """Test position management integration"""
    engine = BacktestEngine(backtest_config)

    # Track position changes
    position_snapshots = []

    def track_positions():
        position_snapshots.append(engine.positions.copy())

    # Patch position tracking into key methods
    original_handle_pool_creation = engine._handle_pool_creation
    original_handle_price_update = engine._handle_price_update

    async def tracked_handle_pool_creation(*args, **kwargs):
        await original_handle_pool_creation(*args, **kwargs)
        track_positions()

    async def tracked_handle_price_update(*args, **kwargs):
        await original_handle_price_update(*args, **kwargs)
        track_positions()

    engine._handle_pool_creation = tracked_handle_pool_creation
    engine._handle_price_update = tracked_handle_price_update

    # Run backtest
    results = await engine.run_backtest(mock_data_file)

    # Verify position management
    assert len(position_snapshots) > 0
    for positions in position_snapshots:
        assert len(positions) <= backtest_config.max_positions
        for pos in positions.values():
            assert (
                pos["size"]
                <= backtest_config.max_position_size * backtest_config.initial_capital
            )
            assert (
                pos["size"]
                >= backtest_config.min_position_size * backtest_config.initial_capital
            )


@pytest.mark.asyncio
async def test_end_to_end_trading_cycle(mock_data_file, backtest_config):
    """Test complete trading cycle from entry to exit"""
    engine = BacktestEngine(backtest_config)

    # Track trading cycle events
    cycle_events = []

    async def mock_handle_pool_creation(*args, **kwargs):
        cycle_events.append("entry")
        return await engine._handle_pool_creation(*args, **kwargs)

    async def mock_handle_price_update(*args, **kwargs):
        cycle_events.append("update")
        return await engine._handle_price_update(*args, **kwargs)

    async def mock_close_position(*args, **kwargs):
        cycle_events.append("exit")
        return await engine._close_position(*args, **kwargs)

    engine._handle_pool_creation = mock_handle_pool_creation
    engine._handle_price_update = mock_handle_price_update
    engine._close_position = mock_close_position

    # Run backtest
    results = await engine.run_backtest(mock_data_file)

    # Verify complete trading cycle
    assert "entry" in cycle_events
    assert "update" in cycle_events
    assert "exit" in cycle_events
    assert results.total_trades > 0


@pytest.mark.asyncio
async def test_capital_management_integration(mock_data_file, backtest_config):
    """Test capital management throughout trading"""
    engine = BacktestEngine(backtest_config)

    # Track capital changes
    capital_snapshots = []

    def track_capital():
        capital_snapshots.append(engine.capital)

    # Patch capital tracking
    original_handle_pool_creation = engine._handle_pool_creation
    original_close_position = engine._close_position

    async def tracked_handle_pool_creation(*args, **kwargs):
        await original_handle_pool_creation(*args, **kwargs)
        track_capital()

    async def tracked_close_position(*args, **kwargs):
        await original_close_position(*args, **kwargs)
        track_capital()

    engine._handle_pool_creation = tracked_handle_pool_creation
    engine._close_position = tracked_close_position

    # Run backtest
    results = await engine.run_backtest(mock_data_file)

    # Verify capital management
    assert len(capital_snapshots) > 0
    for capital in capital_snapshots:
        assert capital >= 0  # No negative capital
        # Verify capital doesn't exceed initial capital by unrealistic amount
        assert (
            capital <= backtest_config.initial_capital * 2
        )  # Allow for reasonable profits


@pytest.mark.asyncio
async def test_error_handling_integration(mock_data_file, backtest_config):
    """Test error handling across components"""
    with patch("env.quantum_pool_selector.QuantumPoolSelector") as mock_selector:
        selector_instance = mock_selector.return_value
        selector_instance.score_pool = MagicMock(side_effect=Exception("Quantum error"))

        engine = BacktestEngine(backtest_config)

        # Run backtest and expect graceful error handling
        results = await engine.run_backtest(mock_data_file)

        # Verify system remains stable
        assert results is not None
        assert isinstance(results.total_trades, int)
        assert isinstance(results.total_profit, float)
        assert len(results.equity_curve) > 0
