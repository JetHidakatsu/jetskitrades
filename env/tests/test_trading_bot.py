import pytest
from unittest.mock import AsyncMock, MagicMock
from trading_bot import TradingBot

@pytest.fixture
def trading_bot():
    client = MagicMock()
    latency_tracker = MagicMock()
    return TradingBot(client, latency_tracker)

@pytest.mark.asyncio
async def test_handle_pool_detection(trading_bot):
    trading_bot.sniper.execute_swap = AsyncMock(return_value=True)
    signature = "mock_signature"
    pool_metrics = {"pool_address": "mock_address"}

    await trading_bot.handle_pool_detection(signature, pool_metrics)

    trading_bot.sniper.execute_swap.assert_called_once_with(signature, Any, {"pool_address": "mock_address", "signature": signature})
