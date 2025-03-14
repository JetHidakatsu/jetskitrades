"""Mock components for sandbox testing"""

from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class MockPoolMetrics:
    """Mock pool metrics for testing"""

    liquidity: float
    volume_24h: float
    price_impact: float
    holder_count: int
    creator_score: float
    time_since_creation: int
    depth_scores: Dict[str, float]
    quantum_score: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class MockTradeMetrics:
    """Mock trade metrics for testing"""

    pool_id: str
    entry_price: float
    position_size: float
    entry_time: datetime
    quantum_score: float
    sentiment_score: float
    validation_score: float
    risk_metrics: Dict[str, Any]
    is_memecoin: bool
    stop_loss: float
    take_profit: float
    max_drawdown: float
    moonbag_size: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        d = asdict(self)
        d["entry_time"] = self.entry_time.isoformat()
        return d


class MockClient:
    async def close(self):
        pass


class MockLatencyTracker:
    def track_latency(self, operation: str, latency: float):
        pass


class MockPoolValidator:
    async def validate_pool(self, pool_id: str) -> bool:
        return True


class MockTransactionExecutor:
    def __init__(self, client, latency_tracker, pool_validator):
        self.client = client
        self.latency_tracker = latency_tracker
        self.pool_validator = pool_validator

    async def execute_swap(
        self,
        pool_id: str,
        amount: float,
        slippage: float,
        priority_fee: float,
        max_fee: float,
    ) -> Dict[str, Any]:
        metrics = MockTradeMetrics(
            pool_id=pool_id,
            entry_price=1.0,
            position_size=amount,
            entry_time=datetime.now(),
            quantum_score=0.8,
            sentiment_score=0.7,
            validation_score=0.9,
            risk_metrics={
                "mempool_congestion": 50,
                "initial_liquidity": 0.1,
                "holder_count": 100,
            },
            is_memecoin=True,
            stop_loss=0.8,
            take_profit=1.5,
            max_drawdown=0.0,
            moonbag_size=amount * 0.1,
        )
        return {"status": "success", "metrics": metrics.to_dict()}


class MockQuantumPoolSelector:
    async def select_pools(self) -> List[str]:
        return ["pool1", "pool2"]


class MockSentimentAnalyzer:
    async def analyze_sentiment(self, text: str) -> float:
        return 0.8


class MockMempoolMonitor:
    def __init__(self, websocket_url: str, latency_tracker, pool_validator):
        self.websocket_url = websocket_url
        self.latency_tracker = latency_tracker
        self.pool_validator = pool_validator
        self.known_pools = {}

    async def analyze_mempool(self, pool_id: str) -> Dict[str, Any]:
        return {
            "transaction_count": 50,
            "average_gas": 0.000001,
            "pending_volume": 0.05,
            "priority_fee": 0.0000015,
        }


class MockTradingParameters:
    def __init__(self):
        # Basic parameters
        self.initial_capital = 0.12
        self.max_position_size = 0.05
        self.risk_factor = 0.4
        self.stop_loss_pct = 0.2
        self.take_profit_pct = 0.5
        self.moonbag_pct = 0.1

        # Fee parameters
        self.min_priority_fee = 0.000001
        self.max_priority_fee = 0.000005
        self.priority_fee_multiplier = 1.2

        # Slippage parameters
        self.max_slippage = 0.05
        self.base_slippage = 0.01
        self.dynamic_slippage = True
        self.slippage_multiplier = 1.5
        self.min_pool_depth = 0.1

        # Transaction parameters
        self.min_block_confirmations = 1
        self.max_block_age = 150
        self.max_retries = 3
        self.retry_delay = 1.0

        # Pool parameters
        self.min_liquidity = 0.1
        self.min_volume = 0.05
        self.min_holder_count = 10
        self.min_creator_score = 0.7
        self.min_pool_age = 3600  # 1 hour

        # Risk management
        self.max_concurrent_positions = 3
        self.max_daily_trades = 20
        self.max_drawdown = 0.1
        self.emergency_exit_threshold = 0.15

        # Performance optimization
        self.latency_threshold = 0.5
        self.gas_price_threshold = 0.000002
        self.mempool_scan_interval = 1.0
        self.position_update_interval = 5.0

        # Advanced trading
        self.use_dynamic_sizing = True
        self.use_sentiment_analysis = True
        self.use_mempool_analysis = True
        self.use_quantum_routing = True
