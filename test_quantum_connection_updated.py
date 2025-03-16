from env.quantum_pool_selector import QuantumPoolSelector, PoolMetrics
from env.tests.mock_async_client import MockAsyncClient
import logging
import asyncio
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class MarketConditions:
    """Market conditions for testing"""
    def __init__(self):
        self.avg_liquidity = 10000.0
        self.liquidity_volatility = 0.2
        self.volume_24h = 5000.0
        self.global_volatility = 0.3
        self.cross_chain_correlation = 0.4

async def test_quantum_connection():
    # Initialize mock client and quantum pool selector
    mock_client = MockAsyncClient()
    selector = QuantumPoolSelector(mock_client)

    # Create test metrics with depth scores and market conditions
    test_metrics = PoolMetrics(
        liquidity=5000.0,  # 5000 SOL
        volume_24h=1000.0,  # 1000 SOL volume
        price_impact=0.05,  # 5% price impact
        holder_count=50,  # 50 holders
        creator_score=0.8,  # Good creator score
        time_since_creation=7200,  # 2 hours old
        depth_scores={
            "1%": 0.9,   # Good depth at 1% price impact
            "2%": 0.8,   # Good depth at 2% price impact
            "5%": 0.6,   # Moderate depth at 5% price impact
            "10%": 0.4   # Lower depth at 10% price impact
        },
        market_conditions=MarketConditions(),
        total_supply=1000000.0  # 1M tokens
    )

    # Test pool scoring
    score = selector.score_pool(test_metrics)
    print(f"\nPool score: {score:.4f}")
    assert 0 <= score <= 1.0, "Score should be between 0 and 1"
    assert score > 0.5, "Score should be good for these metrics"

    # Test optimal position sizing
    optimal_size = await selector.get_optimal_size(test_metrics)
    print(f"Optimal position size: {optimal_size:.4f}")
    assert 0.1 <= optimal_size <= 1.0, "Position size should be between 10% and 100%"

    # Test with high risk metrics
    high_risk_metrics = PoolMetrics(
        liquidity=1000.0,  # Lower liquidity
        volume_24h=5000.0,  # High volume relative to liquidity
        price_impact=0.15,  # High price impact
        holder_count=10,    # Few holders
        creator_score=0.4,  # Lower creator score
        time_since_creation=1800,  # Only 30 minutes old
        depth_scores={
            "1%": 0.3,
            "2%": 0.2,
            "5%": 0.1,
            "10%": 0.05
        },
        market_conditions=MarketConditions(),
        total_supply=1000000.0
    )

    high_risk_score = selector.score_pool(high_risk_metrics)
    print(f"High risk pool score: {high_risk_score:.4f}")
    assert high_risk_score < score, "High risk pool should score lower"

    high_risk_size = await selector.get_optimal_size(high_risk_metrics)
    print(f"High risk position size: {high_risk_size:.4f}")
    assert high_risk_size < optimal_size, "High risk pool should have smaller position size"

    # Test with excellent metrics
    excellent_metrics = PoolMetrics(
        liquidity=10000.0,  # High liquidity
        volume_24h=2000.0,  # Good volume
        price_impact=0.02,  # Low price impact
        holder_count=200,   # Many holders
        creator_score=0.95, # Excellent creator score
        time_since_creation=86400,  # 24 hours old
        depth_scores={
            "1%": 0.95,
            "2%": 0.9,
            "5%": 0.85,
            "10%": 0.8
        },
        market_conditions=MarketConditions(),
        total_supply=1000000.0
    )

    excellent_score = selector.score_pool(excellent_metrics)
    print(f"Excellent pool score: {excellent_score:.4f}")
    assert excellent_score > score, "Excellent pool should score higher"

    excellent_size = await selector.get_optimal_size(excellent_metrics)
    print(f"Excellent position size: {excellent_size:.4f}")
    assert excellent_size > high_risk_size, "Excellent pool should have larger position size"

    # Test smart contract verification
    contract_info = selector.verify_smart_contract("mock_pool_id")
    print(f"\nSmart contract verification: {contract_info}")
    assert contract_info.get("is_verified") is True, "Contract should be verified in mock"
    assert contract_info.get("rugpull_risk", 1.0) < 0.5, "Rugpull risk should be low"

    # Test volume analysis
    volume_info = selector.analyze_trading_volume("mock_pool_id")
    print(f"Volume analysis: {volume_info}")
    assert isinstance(volume_info, dict), "Volume analysis should return metrics"

    print("\nAll quantum connection tests passed!")

if __name__ == "__main__":
    print("Testing quantum connection...")
    asyncio.run(test_quantum_connection())
