from env.quantum_pool_selector import QuantumPoolSelector, PoolMetrics
from env.tests.mock_async_client import MockAsyncClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_quantum_connection():
    # Initialize mock client and quantum pool selector
    mock_client = MockAsyncClient()
    selector = QuantumPoolSelector(mock_client)

    # Create some test metrics
    test_metrics = PoolMetrics(
        liquidity=5000.0,  # 5000 SOL
        volume_24h=1000.0,  # 1000 SOL volume
        price_impact=0.05,  # 5% price impact
        holder_count=50,  # 50 holders
        creator_score=0.8,  # Good creator score
        time_since_creation=7200,  # 2 hours old
    )

    # Test scoring
    score = selector.score_pool(test_metrics)
    print(f"\nPool score: {score:.4f}")

    # Test position sizing
    position_size = selector.get_position_size(score, test_metrics, max_size=1.0)
    print(f"Recommended position size: {position_size:.4f}")


if __name__ == "__main__":
    print("Testing quantum connection...")
    test_quantum_connection()
