import pytest

if __name__ == "__main__":
    pytest.main(
        [
            "env/tests/test_backtest_helius_updated.py",
            "env/tests/test_backtest_integration_updated.py",
            "env/tests/test_backtest_performance.py",
            "-v",
        ]
    )
