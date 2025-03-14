import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from env.backtest import BacktestEngine, BacktestConfig
from env.helius_provider import PoolCreationEvent
from env.mempool_monitor import MempoolMonitor
from env.quantum_pool_selector import PoolMetrics
from env.trading_logic_updated import TradingLogic


@pytest.fixture
def mock_helius_data():
    """Mock Helius API response data"""
    pool_creation = PoolCreationEvent(
        pool_id="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        timestamp=datetime.now(tz=datetime.now().astimezone().tzinfo),
        initial_liquidity=1000000,
        price_impact=0.01,
        creator_address="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # Valid Base58 string
        token_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # Valid Base58 string
        tx_signature="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # Valid Base58 string
    )

    price_impacts = {
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": [
            0.02,  # 2% impact
            0.03,  # 3% impact
            0.01,  # 1% impact
        ]
    }

    return pool_creation, price_impacts


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
        use_helius=True,
        data_source="helius",
    )


@pytest.mark.asyncio
async def test_helius_data_loading(mock_helius_data, backtest_config):
    """Test loading historical data from Helius API"""
    pool_creation, price_impacts = mock_helius_data

    with patch("env.helius_provider.HeliusDataProvider") as mock_provider:
        # Configure mock provider
        provider_instance = mock_provider.return_value
        provider_instance.get_pool_creations = AsyncMock(return_value=[pool_creation])
        provider_instance.get_price_impacts = AsyncMock(return_value=price_impacts)

        # Create and run backtest engine with mock provider
        engine = BacktestEngine(backtest_config, helius_provider=provider_instance)
        engine.config.use_helius = True
        engine.config.data_source = "helius"
        results = await engine.run_backtest()

        # Verify API calls
        provider_instance.get_pool_creations.assert_called_once_with(
            backtest_config.start_date, backtest_config.end_date
        )
        provider_instance.get_price_impacts.assert_called_once()

        # Verify data processing
        assert results.total_trades >= 0
        assert len(results.equity_curve) > 0


@pytest.mark.asyncio
async def test_helius_error_handling(backtest_config):
    """Test error handling for Helius API failures"""
    with patch("env.helius_provider.HeliusDataProvider") as mock_provider:
        # Configure mock provider to raise exception
        provider_instance = mock_provider.return_value
        provider_instance.get_pool_creations = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Create engine with Helius enabled and mock provider
        engine = BacktestEngine(backtest_config, helius_provider=provider_instance)
        engine.config.use_helius = True
        engine.config.data_source = "helius"

        # Verify error handling
        with pytest.raises(Exception) as exc_info:
            await engine.run_backtest()
        assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_helius_trading_logic(mock_helius_data, backtest_config):
    """Test trading logic with Helius data"""
    pool_creation, price_impacts = mock_helius_data

    with patch("env.helius_provider.HeliusDataProvider") as mock_provider, patch(
        "env.quantum_pool_selector.QuantumPoolSelector"
    ) as mock_selector, patch(
        "env.sentiment_analyzer.SentimentAnalyzer"
    ) as mock_analyzer, patch(
        "env.mempool_monitor.MempoolMonitor"
    ) as mock_mempool:

        # Configure mock provider
        provider_instance = mock_provider.return_value
        provider_instance.get_pool_creations = AsyncMock(return_value=[pool_creation])
        provider_instance.get_price_impacts = AsyncMock(return_value=price_impacts)

        # Configure mock components
        selector_instance = mock_selector.return_value
        selector_instance.score_pool = MagicMock(return_value=0.8)
        selector_instance.get_optimal_size = AsyncMock(return_value=0.1)

        analyzer_instance = mock_analyzer.return_value
        analyzer_instance.analyze = AsyncMock(return_value=0.7)

        mempool_instance = mock_mempool.return_value
        mempool_instance.analyze_pool = AsyncMock(return_value={"score": 0.9})

        # Create and run backtest engine with mock provider
        engine = BacktestEngine(backtest_config, helius_provider=provider_instance)
        engine.config.use_helius = True
        engine.config.data_source = "helius"
        results = await engine.run_backtest()

        # Verify component interactions
        assert selector_instance.score_pool.called
        assert selector_instance.get_optimal_size.called
        assert analyzer_instance.analyze.called

        # Verify trading decisions
        assert results.total_trades > 0
        if results.total_trades > 0:
            assert results.win_rate >= 0
            assert len(results.trades) == results.total_trades


@pytest.mark.asyncio
async def test_helius_performance_metrics(mock_helius_data, backtest_config):
    """Test performance calculations with Helius data"""
    pool_creation, price_impacts = mock_helius_data

    with patch("env.helius_provider.HeliusDataProvider") as mock_provider:
        # Configure mock provider
        provider_instance = mock_provider.return_value
        provider_instance.get_pool_creations = AsyncMock(return_value=[pool_creation])
        provider_instance.get_price_impacts = AsyncMock(return_value=price_impacts)

        # Create and run backtest engine with mock provider
        engine = BacktestEngine(backtest_config, helius_provider=provider_instance)
        engine.config.use_helius = True
        engine.config.data_source = "helius"
        results = await engine.run_backtest()

        # Verify performance metrics
        assert isinstance(results.total_profit, float)
        assert isinstance(results.max_drawdown, float)
        assert isinstance(results.sharpe_ratio, float)
        assert 0 <= results.win_rate <= 1
        assert len(results.equity_curve) > 0


@pytest.mark.asyncio
async def test_helius_position_management(mock_helius_data, backtest_config):
    """Test position management with Helius data"""
    pool_creation, price_impacts = mock_helius_data

    with patch("env.helius_provider.HeliusDataProvider") as mock_provider:
        # Configure mock provider
        provider_instance = mock_provider.return_value
        provider_instance.get_pool_creations = AsyncMock(return_value=[pool_creation])
        provider_instance.get_price_impacts = AsyncMock(return_value=price_impacts)

        # Create and run backtest engine with mock provider
        engine = BacktestEngine(backtest_config, helius_provider=provider_instance)
        engine.config.use_helius = True
        engine.config.data_source = "helius"

        # Verify position constraints
        assert len(engine.positions) <= backtest_config.max_positions

        results = await engine.run_backtest()

        # Verify position sizing
        for trade in results.trades:
            assert (
                trade["size"]
                <= backtest_config.max_position_size * backtest_config.initial_capital
            )
            assert (
                trade["size"]
                >= backtest_config.min_position_size * backtest_config.initial_capital
            )
