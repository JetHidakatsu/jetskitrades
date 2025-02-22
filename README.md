# Solana Memecoin Trading Bot

A high-performance trading bot for Solana memecoins using Raydium DEX, featuring WebSocket-based pool detection, enhanced pool validation scoring, and integrated latency tracking.

## Features

- WebSocket-based pool detection system
- Enhanced pool validation scoring
- Integrated latency tracking (<200ms target)
- Position management with dynamic sizing
- Helius API integration for historical data
- Comprehensive backtesting system

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
```

3. Set up API keys and configuration:

You'll need to obtain the following API keys and credentials:

- **Helius API Key**: 
  - Sign up at https://www.helius.dev/
  - Create an API key in your dashboard
  - Add to `.env`: `HELIUS_API_KEY=your_key_here`

- **QuickNode RPC URL**: 
  - Create an account at https://www.quicknode.com/
  - Create a Solana endpoint
  - Add RPC and WebSocket URLs to `.env`

- **Solana Wallet**: 
  - Create a new wallet for the bot
  - Export the private key
  - Add to `.env`: `PRIVATE_KEY=your_private_key_here`
  - IMPORTANT: Use a dedicated wallet with only the funds you want to trade

- **IBM Quantum (Optional)**:
  - Only needed if using quantum features
  - Register at https://quantum-computing.ibm.com/
  - Get your API token
  - Add to `.env`: `IBM_QUANTUM_TOKEN=your_token_here`

4. Run tests to verify setup:
```bash
python run_backtest_tests.py
```

5. Start the bot:
```bash
python main.py
```

IMPORTANT: Never share your `.env` file or commit it to version control. It contains sensitive information that could compromise your accounts.

## Components

### Core Trading
- Pool detection and validation
- Trading strategy implementation
- Position management
- Risk management

### Data Collection
- WebSocket pool monitoring
- Helius API integration
- Historical data collection
- Price impact tracking

### Analysis
- Pool validation scoring
- Performance metrics
- Latency tracking
- Position sizing

### Backtesting
- Historical data replay
- Strategy validation
- Performance testing
- Helius data integration

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Trading Strategy](docs/STRATEGY.md)
- [Backtesting System](docs/BACKTESTING.md)
- [API Integration](docs/API.md)

## Backtesting

The bot includes a comprehensive backtesting system for strategy validation and performance testing. Features include:

### HistoricalReplay System

The HistoricalReplay system simulates memecoin market events for backtesting:

- **Purpose**: Replays pool creation events with varying liquidity/volatility conditions to test trading strategies
- **Features**:
  - Simulates deteriorating market conditions
  - Tracks latency for all operations (<200ms target)
  - Measures trade success rates and quantum pool scores
  - Validates emergency exit conditions
- **Usage**:
  ```python
  async for event in replay.replay():
      metrics = PoolMetrics(
          liquidity=event.liquidity,
          volume_24h=event.volume_24h,
          ...
      )
      position_size = await trading_logic.calculate_position_size(...)
  ```
- **Performance Metrics**:
  - Average latency (target: <1s)
  - Trade success rate (target: >50%)
  - Quantum pool score (target: >0.6)
  - Total execution time (target: <5s)

Additional Features:
- Historical data replay with Helius API integration
- Performance metrics and strategy validation
- Configurable test scenarios
- Detailed reporting and analysis

For detailed information about the backtesting system, see [Backtesting Documentation](docs/BACKTESTING.md).

## Configuration

Key configuration parameters in `.env`:

```ini
# Trading Parameters
INITIAL_CAPITAL=1000.0
RISK_FACTOR=0.02
MAX_POSITION_SIZE=0.1
MIN_POSITION_SIZE=0.01
MAX_POSITIONS=5
SLIPPAGE=0.02

# API Configuration
HELIUS_API_KEY=your_api_key
HELIUS_ENDPOINT=https://api.helius.xyz/v0
QUICKNODE_RPC_URL=your_quicknode_url
QUICKNODE_WS_URL=your_quicknode_ws_url
```

## Performance

The bot is optimized for:
- Sub-200ms latency
- Efficient memory usage
- High throughput
- Reliable execution

## Testing

Run different test categories:

```bash
# All tests
python run_backtest_tests.py

# Unit tests only
python run_backtest_tests.py --unit-only

# Integration tests
python run_backtest_tests.py --integration-only

# Performance tests
python run_backtest_tests.py --performance-only

# Generate reports
python run_backtest_tests.py --coverage --html-report
```

Test reports and metrics are available in:
- Coverage: `reports/coverage/index.html`
- Test Results: `reports/test_results/[timestamp]/report.html`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

See [Contributing Guide](docs/CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details
