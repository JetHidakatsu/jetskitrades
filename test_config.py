"""Test configuration module"""

import os
import pytest
from env.config import Config, NetworkConfig, WalletConfig, TradingConfig, PoolValidationConfig


def test_network_config():
    """Test network configuration"""
    os.environ["NETWORK"] = "testnet"
    os.environ["RPC_URL"] = "https://test-url"
    os.environ["WS_URL"] = "wss://test-ws"

    config = NetworkConfig()
    assert config.network == "testnet"
    assert config.rpc_url == "https://test-url"
    assert config.ws_url == "wss://test-ws"


def test_wallet_config():
    """Test wallet configuration"""
    os.environ["PRIVATE_KEY"] = "test-key"

    config = WalletConfig()
    assert config.private_key == "test-key"


def test_config_defaults():
    """Test configuration defaults"""
    config = Config()

    assert config.trading.initial_capital == 0.12
    assert config.trading.max_position_size == 0.05
    assert config.trading.stop_loss_pct == 0.20
    assert config.trading.take_profit_pct == 0.50
    assert config.trading.moonbag_pct == 0.10
    assert config.trading.min_liquidity == 0.1
    assert config.trading.min_holder_count == 10


def test_invalid_values():
    """Test handling of invalid configuration values"""
    os.environ["INITIAL_CAPITAL"] = "invalid"

    with pytest.raises(ValueError):
        TradingConfig()


def test_boolean_values():
    """Test boolean configuration values"""
    os.environ["DEBUG"] = "true"
    os.environ["TEST_MODE"] = "false"

    config = Config()
    assert config.development.debug is True
    assert config.development.test_mode is False


def test_numeric_values():
    """Test numeric configuration values"""
    os.environ["MAX_RETRIES"] = "5"
    os.environ["RETRY_DELAY"] = "2"

    config = Config()
    assert config.transaction.max_retries == 5
    assert config.transaction.retry_delay == 2


def test_pool_validation_config():
    """Test pool validation configuration"""
    os.environ["MIN_POOL_AGE_HOURS"] = "2"
    os.environ["MAX_POOL_AGE_HOURS"] = "48"
    os.environ["MIN_LIQUIDITY_SOL"] = "0.5"

    config = PoolValidationConfig()
    assert config.min_pool_age_hours == 2
    assert config.max_pool_age_hours == 48
    assert config.min_liquidity_sol == 0.5


def test_config_override():
    """Test configuration override"""
    original_config = Config()

    os.environ["INITIAL_CAPITAL"] = "0.24"
    os.environ["MAX_POSITION_SIZE"] = "0.1"

    new_config = Config()
    assert new_config.trading.initial_capital == 0.24
    assert new_config.trading.max_position_size == 0.1
    assert new_config.trading.stop_loss_pct == original_config.trading.stop_loss_pct


def test_required_values():
    """Test required configuration values"""
    required_vars = [
        "NETWORK",
        "RPC_URL",
        "WS_URL",
        "PRIVATE_KEY",
    ]

    for var in required_vars:
        if var in os.environ:
            del os.environ[var]

    config = Config()
    assert config.network.network == "devnet"  # Default value
    assert config.network.rpc_url == ""  # Empty string
    assert config.network.ws_url == ""  # Empty string
    assert config.wallet.private_key == ""  # Empty string


def test_api_config():
    """Test API configuration"""
    os.environ["HELIUS_API_KEY"] = "test-helius-key"
    os.environ["DEXSCREENER_API_KEY"] = "test-dexscreener-key"

    config = Config()
    assert config.api.helius_api_key == "test-helius-key"
    assert config.api.dexscreener_api_key == "test-dexscreener-key"


def test_advanced_config():
    """Test advanced configuration"""
    os.environ["USE_PARALLEL_EXECUTION"] = "false"
    os.environ["USE_PRIORITY_FEES"] = "true"
    os.environ["USE_MOONBAG_STRATEGY"] = "true"

    config = Config()
    assert config.advanced.use_parallel_execution is False
    assert config.advanced.use_priority_fees is True
    assert config.advanced.use_moonbag_strategy is True


def test_logging_config():
    """Test logging configuration"""
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_FILE"] = "test.log"
    os.environ["CONSOLE_LOG"] = "false"

    config = Config()
    assert config.logging.log_level == "DEBUG"
    assert config.logging.log_file == "test.log"
    assert config.logging.console_log is False
