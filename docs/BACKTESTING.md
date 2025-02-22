# Solana Memecoin Trading Bot - Backtesting System

This document describes the backtesting system for the Solana memecoin trading bot, which allows testing trading strategies using both historical data files and live Helius API data.

## Quick Start

Run a basic backtest:
```bash
python run_backtest_tests.py
```

Run specific test categories:
```bash
# Unit tests only
python run_backtest_tests.py --unit-only

# Integration tests
python run_backtest_tests.py --integration-only

# Performance tests
python run_backtest_tests.py --performance-only

# Helius API integration tests
python run_backtest_tests.py --helius-only
```

Generate reports:
```bash
# Generate coverage report
python run_backtest_tests.py --coverage

# Generate HTML test report
python run_backtest_tests.py --html-report
```

## Configuration

The backtesting system can be configured through:

1. Environment variables in `.env`
2. Test configuration in `env/tests/pytest_backtest.ini`
3. Command line arguments to `run_backtest_tests.py`

### Key Configuration Parameters

```ini
# Trading Parameters
INITIAL_CAPITAL=1000.0
RISK_FACTOR=0.02
MAX_POSITION_SIZE=0.1
MIN_POSITION_SIZE=0.01
MAX_POSITIONS=5
SLIPPAGE=0.02

# Helius API Configuration
HELIUS_API_KEY=your_api_key
HELIUS_ENDPOINT=https://api.helius.xyz/v0
```

## Data Sources

### File-based Historical Data

Place historical data files in JSON format:
```json
[
    {
        "type": "pool_creation",
        "timestamp": "2024-01-01T00:00:00Z",
        "pool_id": "pool_address",
        "pool_data": {
            "initial_liquidity": 1000000,
            "price_impact": 0.01,
            "creator_address": "creator_address",
            "price": 1.0
        }
    },
    {
        "type": "price_update",
        "timestamp": "2024-01-01T00:01:00Z",
        "pool_id": "pool_address",
        "price": 1.2
    }
]
```

### Helius API Integration

The system can fetch historical data directly from Helius API, including:
- Pool creation events
- Price impact history
- Trading activity

## Test Categories

### Unit Tests
- Basic component functionality
- Data loading and processing
- Event generation
- Position management

### Integration Tests
- Component interactions
- Trading logic integration
- Data flow between components
- State management

### Performance Tests
- Large dataset processing
- Memory usage optimization
- Concurrent processing
- Data streaming performance
- Position scaling

### Helius Integration Tests
- API connectivity
- Data transformation
- Real-world data validation
- Historical data accuracy

## Reports and Metrics

### Coverage Report
Located at `reports/coverage/index.html`, includes:
- Code coverage statistics
- Uncovered lines
- Branch coverage

### Test Results
Located at `reports/test_results/[timestamp]/report.html`, includes:
- Test execution summary
- Failure details
- Performance metrics
- Test timing information

## Performance Thresholds

The system enforces the following performance requirements:
- Maximum execution time: 5.0 seconds for 1000 events
- Maximum memory increase: 100 MB
- Maximum latency: 200 ms
- Minimum success rate: 90%

## Adding New Tests

1. Create test files in `env/tests/`
2. Use appropriate markers:
   ```python
   @pytest.mark.unit
   @pytest.mark.integration
   @pytest.mark.performance
   @pytest.mark.helius
   ```
3. Follow existing patterns for fixtures and assertions

## Common Issues

### Memory Usage
If experiencing high memory usage:
- Reduce batch sizes in data loading
- Enable streaming processing
- Clear caches regularly

### Performance
If experiencing slow execution:
- Use concurrent processing where appropriate
- Enable data streaming
- Optimize data structures

### API Integration
If experiencing Helius API issues:
- Verify API key configuration
- Check rate limits
- Use mock data for testing

## Contributing

When adding features to the backtesting system:
1. Add appropriate tests
2. Update documentation
3. Verify performance impact
4. Run full test suite
5. Update metrics thresholds if needed
