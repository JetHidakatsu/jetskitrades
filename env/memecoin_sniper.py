"""Memecoin sniper for Solana tokens"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Optional, Any
import logging
from datetime import datetime

from solana.rpc.async_api import AsyncClient

from .quantum_pool_selector import QuantumPoolSelector, PoolMetrics
from .trading_logic import TradingLogic, TradingParameters
from .sentiment_analyzer import SentimentAnalyzer
from .transaction_executor_v4 import TransactionExecutorV4, TransactionConfig
from .parallel_transaction_executor import RpcEndpoint
from .pool_validator import PoolValidator
from .latency_tracker import LatencyTracker
from .mempool_monitor import MempoolMonitor
from .config import CONFIG

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemecoinSniper:
    """Enhanced memecoin sniper with quantum analysis"""

    def __init__(
        self,
        client: AsyncClient,
        params: Optional[TradingParameters] = None
    ):
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.running = False

        # Initialize quantum selector
        self.quantum_selector = QuantumPoolSelector(
            num_qubits=4  # Optimal for memecoin analysis
        )

        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer(
            client=self.client
        )

        self.pool_validator = PoolValidator(
            client=self.client
        )

        self.latency_tracker = LatencyTracker()

        # Configure RPC endpoints for parallel execution
        rpc_endpoints = [
            RpcEndpoint(url=CONFIG.network.rpc_url, weight=1.0),
            RpcEndpoint(url=CONFIG.network.backup_rpc_url, weight=0.8)
        ] if hasattr(CONFIG.network, 'backup_rpc_url') else None

        # Initialize transaction executor with optimized config
        tx_config = TransactionConfig(
            simulation_enabled=True,
            dynamic_cu_adjustment=True,
            preflight_enabled=False,  # Skip preflight for faster execution
            max_bundle_size=3,  # Bundle up to 3 transactions
            base_compute_unit_limit=300_000,  # Higher base limit for memecoins
            min_compute_unit_price=2_000,  # Higher minimum price
            max_compute_unit_price=1_000_000,
            max_retries=5,  # Increased retries for memecoin transactions
            retry_delay=0.5  # Faster retry for memecoin opportunities
        )
        
        self.transaction_executor = TransactionExecutorV4(
            client=self.client,
            latency_tracker=self.latency_tracker,
            pool_validator=self.pool_validator,
            config=tx_config,
            rpc_endpoints=rpc_endpoints
        )

        # Initialize mempool monitor with callback
        self.mempool_monitor = MempoolMonitor(
            websocket_url=CONFIG.network.ws_url,
            latency_tracker=self.latency_tracker,
            pool_validator=self.pool_validator
        )

        # Initialize trading logic
        self.trading_logic = TradingLogic(
            quantum_selector=self.quantum_selector,
            sentiment_analyzer=self.sentiment_analyzer,
            transaction_executor=self.transaction_executor,
            pool_validator=self.pool_validator,
            latency_tracker=self.latency_tracker,
            mempool_monitor=self.mempool_monitor,
            params=params or TradingParameters()
        )

        # Track performance
        self.performance_metrics = {
            "pools_analyzed": 0,
            "opportunities_found": 0,
            "successful_entries": 0,
            "failed_entries": 0,
            "total_profit": 0.0,
            "active_positions": 0
        }

    async def start(self) -> None:
        """Start monitoring for opportunities"""
        try:
            self.running = True
            self.logger.info("Starting memecoin sniper...")

            # Start mempool monitoring
            await self.mempool_monitor.start()

            # Start analysis loop
            await self._run_analysis_loop()

        except Exception as e:
            self.logger.error(f"Error starting sniper: {e}")
            raise

    async def stop(self) -> None:
        """Stop monitoring"""
        self.running = False
        await self.mempool_monitor.stop()
        self.logger.info("Memecoin sniper stopped")

    async def _run_analysis_loop(self) -> None:
        """Main analysis loop"""
        while self.running:
            try:
                # Process new pools
                for pool_id, pool_data in self.mempool_monitor.known_pools.items():
                    if not pool_data.get("analyzed", False):
                        await self._analyze_pool(pool_id, pool_data)
                        pool_data["analyzed"] = True
                        self.performance_metrics["pools_analyzed"] += 1

                # Check exit conditions for active positions
                await self._check_active_positions()

                # Update metrics
                if self.performance_metrics["pools_analyzed"] % 10 == 0:
                    self._log_performance()

                await asyncio.sleep(CONFIG.performance.metrics_update_interval)

            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(5)

    async def _analyze_pool(self, pool_id: str, pool_data: Dict[str, Any]) -> None:
        """Analyze a new pool for trading opportunity"""
        try:
            # Create pool metrics
            pool_metrics = PoolMetrics(
                liquidity=pool_data.get("initial_liquidity", 0),
                volume_24h=0,  # New pool
                price_impact=pool_data.get("price_impact", 0),
                holder_count=0,  # Will be updated
                creator_score=0.0,  # Will be updated
                time_since_creation=0.0,
                depth_scores={},
                market_conditions=None,
                total_supply=pool_data.get("total_supply", 0)
            )

            # Evaluate opportunity
            meets_criteria, score, analysis = await self.trading_logic.evaluate_trading_opportunity(
                pool_id,
                pool_data,
                pool_data.get("creator_address", "")
            )

            if meets_criteria:
                self.performance_metrics["opportunities_found"] += 1
                self.logger.info(f"Trading opportunity found: {pool_id}")

                # Get optimal position size
                position_size = await self.quantum_selector.get_optimal_size(pool_metrics)

                # Execute entry
                result = await self.trading_logic.execute_entry(
                    pool_id=pool_id,
                    position_size=position_size,
                    pool_metrics=pool_metrics
                )

                if result["status"] == "success":
                    self.performance_metrics["successful_entries"] += 1
                    self.performance_metrics["active_positions"] += 1
                    self.logger.info(f"Successfully entered position: {pool_id}")
                else:
                    self.performance_metrics["failed_entries"] += 1
                    self.logger.warning(f"Failed to enter position: {result.get('error')}")

        except Exception as e:
            self.logger.error(f"Error analyzing pool {pool_id}: {e}")

    async def _check_active_positions(self) -> None:
        """Check and manage active positions"""
        try:
            for pool_id, position in self.trading_logic.active_positions.items():
                # Get current metrics
                pool_data = self.mempool_monitor.known_pools.get(pool_id, {})
                if not pool_data:
                    continue

                pool_metrics = PoolMetrics(
                    liquidity=pool_data.get("current_liquidity", 0),
                    volume_24h=pool_data.get("volume_24h", 0),
                    price_impact=pool_data.get("current_price_impact", 0),
                    holder_count=pool_data.get("holder_count", 0),
                    creator_score=position.validation_score,
                    time_since_creation=(datetime.now() - pool_data["creation_time"]).total_seconds(),
                    depth_scores={},
                    market_conditions=None
                )

                # Check exit conditions
                should_exit = await self.trading_logic._check_exit_conditions(
                    pool_id,
                    pool_data.get("current_price", 0),
                    pool_metrics,
                    is_memecoin=True
                )

                if should_exit:
                    # Position will be automatically updated by trading logic
                    self.performance_metrics["active_positions"] -= 1
                    profit = position.position_size * (
                        pool_data.get("current_price", 0) - position.entry_price
                    )
                    self.performance_metrics["total_profit"] += profit

        except Exception as e:
            self.logger.error(f"Error checking active positions: {e}")

    def _log_performance(self) -> None:
        """Log performance metrics"""
        self.logger.info(
            f"Performance Metrics:\n"
            f"Pools Analyzed: {self.performance_metrics['pools_analyzed']}\n"
            f"Opportunities Found: {self.performance_metrics['opportunities_found']}\n"
            f"Successful Entries: {self.performance_metrics['successful_entries']}\n"
            f"Failed Entries: {self.performance_metrics['failed_entries']}\n"
            f"Active Positions: {self.performance_metrics['active_positions']}\n"
            f"Total Profit: {self.performance_metrics['total_profit']:.4f} SOL"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        tx_metrics = self.transaction_executor.get_metrics()
        return {
            "running": self.running,
            **self.performance_metrics,
            "quantum_stats": {
                "total_pools_scored": self.quantum_selector.score_pool.__dict__.get("call_count", 0)
            },
            "transaction_stats": {
                "success_rate": tx_metrics["success_rate"],
                "avg_latency": tx_metrics["average_latency"],
                "total_transactions": tx_metrics["total_transactions"],
                "compute_unit_stats": tx_metrics.get("compute_unit_stats", {}),
                "parallel_execution": tx_metrics.get("parallel_stats", None)
            }
        }
