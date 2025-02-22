# Contributing to Solana Memecoin Trading Bot

Thank you for your interest in contributing! This guide will help you understand how to work with the codebase, especially the backtesting system.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/solana-memecoin-bot.git
cd solana-memecoin-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Code Structure

```
solana-memecoin-bot/
├── env/
│   ├── tests/
│   │   ├── test_backtest.py          # Base backtest tests
│   │   ├── test_backtest_helius.py   # Helius integration tests
│   │   ├── test_backtest_integration.py  # Component integration tests
│   │   └── test_backtest_performance.py  # Performance tests
│   ├── helius_provider.py            # Helius API integration
│   ├── trading_bot.py                # Main bot implementation
│   └── ...
├── docs/
│   ├── BACKTESTING.md               # Backtesting documentation
│   └── CONTRIBUTING.md              # This file
├── backtest.py                      # Backtesting engine
└── run_backtest_tests.py           # Test runner script
```

## Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes, following our coding standards

3. Add tests for new functionality:
- Unit tests in appropriate test file
- Integration tests if needed
- Performance tests for critical paths

4. Run tests:
```bash
python run_backtest_tests.py --coverage
```

5. Submit a pull request

## Adding New Features to Backtesting System

### 1. Adding New Test Cases

Create test functions with appropriate markers:
```python
@pytest.mark.unit
async def test_your_feature():
    # Test implementation
    pass
```

### 2. Adding New Data Sources

1. Create provider class:
```python
class YourDataProvider:
    async def get_historical_data(self):
        # Implementation
        pass
```

2. Add integration tests:
```python
@pytest.mark.integration
async def test_your_provider_integration():
    # Test implementation
    pass
```

### 3. Performance Considerations

- Monitor execution time
- Check memory usage
- Test with large datasets
- Verify concurrent processing

## Testing Guidelines

### Unit Tests
- Test single components
- Mock dependencies
- Focus on edge cases
- Keep tests focused

### Integration Tests
- Test component interactions
- Use realistic data
- Verify data flow
- Test error handling

### Performance Tests
- Use large datasets
- Measure execution time
- Monitor resource usage
- Test concurrent operations

## Code Style

- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions focused
- Write clear commit messages

## Documentation

When adding features:
1. Update relevant documentation
2. Add code comments
3. Include usage examples
4. Document performance implications

## Performance Requirements

Your changes should maintain:
- Sub-200ms latency
- Efficient memory usage
- High throughput
- Reliable execution

## Common Issues

### Memory Usage
- Use generators for large datasets
- Clear caches regularly
- Monitor memory allocation
- Profile memory usage

### Performance
- Use async where appropriate
- Optimize data structures
- Minimize network calls
- Cache frequently used data

### Testing
- Mock external services
- Use appropriate fixtures
- Clean up test data
- Handle async properly

## Review Process

Pull requests should:
1. Pass all tests
2. Meet performance requirements
3. Include documentation
4. Follow code style
5. Have clear commit history

## Getting Help

- Check existing issues
- Review documentation
- Ask in discussions
- Join our Discord

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
