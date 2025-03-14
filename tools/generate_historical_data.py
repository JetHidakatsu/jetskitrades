#!/usr/bin/env python3
"""Tool to generate historical data files for backtesting"""

import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class HistoricalDataGenerator:
    """Generator for historical trading data"""

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        num_pools: int = 5,
        update_frequency_seconds: int = 60,
        base_liquidity: float = 1000000,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.num_pools = num_pools
        self.update_frequency = update_frequency_seconds
        self.base_liquidity = base_liquidity
        self.pools: Dict[str, Dict] = {}
        self.events: List[Dict] = []

    def generate_data(self) -> Dict[str, Any]:
        """Generate complete historical dataset"""
        self._generate_pools()
        self._generate_events()
        return self._create_dataset()

    def _generate_pools(self):
        """Generate pool configurations"""
        for i in range(self.num_pools):
            pool_id = f"pool_{i}"
            creator = f"creator_{random.randint(1, 3)}"  # 3 possible creators

            self.pools[pool_id] = {
                "initial_liquidity": self.base_liquidity * random.uniform(0.5, 2.0),
                "price_impact": round(random.uniform(0.01, 0.03), 3),
                "creator_address": creator,
                "token_mint": f"token_{i}",
                "current_price": 1.0,
                "creation_time": self.start_date
                + timedelta(
                    minutes=random.randint(
                        0, int((self.end_date - self.start_date).total_seconds() / 60)
                    )
                ),
            }

    def _generate_events(self):
        """Generate trading events"""
        # Add pool creation events
        for pool_id, pool_data in self.pools.items():
            self.events.append(
                {
                    "type": "pool_creation",
                    "timestamp": pool_data["creation_time"].isoformat(),
                    "pool_id": pool_id,
                    "pool_data": {
                        "initial_liquidity": pool_data["initial_liquidity"],
                        "price_impact": pool_data["price_impact"],
                        "creator_address": pool_data["creator_address"],
                        "token_mint": pool_data["token_mint"],
                        "price": pool_data["current_price"],
                    },
                }
            )

        # Generate price updates
        current_time = self.start_date
        while current_time < self.end_date:
            for pool_id, pool_data in self.pools.items():
                if current_time > pool_data["creation_time"]:
                    # Simulate price movement
                    price_change = random.uniform(-0.2, 0.3)  # -20% to +30%
                    new_price = pool_data["current_price"] * (1 + price_change)

                    # Add volume and liquidity changes
                    volume = pool_data["initial_liquidity"] * random.uniform(0.01, 0.1)
                    liquidity_change = volume * random.uniform(-0.5, 0.5)

                    self.events.append(
                        {
                            "type": "price_update",
                            "timestamp": current_time.isoformat(),
                            "pool_id": pool_id,
                            "price": round(new_price, 4),
                            "volume": round(volume, 2),
                            "liquidity_change": round(liquidity_change, 2),
                        }
                    )

                    self.pools[pool_id]["current_price"] = new_price

            current_time += timedelta(seconds=self.update_frequency)

    def _create_dataset(self) -> Dict[str, Any]:
        """Create final dataset with metadata"""
        # Sort events by timestamp
        self.events.sort(key=lambda x: x["timestamp"])

        # Calculate summary statistics
        price_updates = [e for e in self.events if e["type"] == "price_update"]
        pool_creations = [e for e in self.events if e["type"] == "pool_creation"]

        # Generate scenarios
        scenarios = self._generate_scenarios()

        # Calculate metrics
        metrics = {
            "avg_latency_ms": random.uniform(100, 200),
            "min_latency_ms": 100,
            "max_latency_ms": 200,
            "success_rate": random.uniform(0.9, 0.99),
            "avg_price_impact_accuracy": random.uniform(0.95, 0.99),
        }

        return {
            "metadata": {
                "description": "Generated historical data for backtesting",
                "timeframe": f"{self.start_date.isoformat()} to {self.end_date.isoformat()}",
                "source": "Data Generator",
                "version": "1.0.0",
            },
            "events": self.events,
            "summary": {
                "total_pools": len(self.pools),
                "total_events": len(self.events),
                "price_updates": len(price_updates),
                "pool_creations": len(pool_creations),
                "avg_initial_liquidity": sum(
                    p["initial_liquidity"] for p in self.pools.values()
                )
                / len(self.pools),
                "avg_price_impact": sum(p["price_impact"] for p in self.pools.values())
                / len(self.pools),
                "unique_creators": len(
                    set(p["creator_address"] for p in self.pools.values())
                ),
            },
            "scenarios": scenarios,
            "metrics": metrics,
        }

    def _generate_scenarios(self) -> Dict[str, Any]:
        """Generate example trading scenarios"""
        scenarios = {}

        for pool_id, pool_data in self.pools.items():
            # Find price updates for this pool
            pool_updates = [
                e
                for e in self.events
                if e["type"] == "price_update" and e["pool_id"] == pool_id
            ]

            if len(pool_updates) > 1:
                # Calculate profit/loss scenario
                entry_price = pool_updates[0]["price"]
                exit_price = pool_updates[-1]["price"]
                duration = datetime.fromisoformat(
                    pool_updates[-1]["timestamp"]
                ) - datetime.fromisoformat(pool_updates[0]["timestamp"])

                profit_percentage = ((exit_price / entry_price) - 1) * 100

                scenario_type = (
                    "successful_trade"
                    if profit_percentage > 10
                    else "failed_trade" if profit_percentage < -10 else "neutral_trade"
                )

                scenarios[scenario_type] = {
                    "pool_id": pool_id,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "hold_duration": str(duration),
                    (
                        "profit_percentage"
                        if profit_percentage > 0
                        else "loss_percentage"
                    ): abs(profit_percentage),
                }

        return scenarios


def main():
    parser = argparse.ArgumentParser(description="Generate historical trading data")

    parser.add_argument(
        "--start-date",
        type=str,
        default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--num-pools", type=int, default=5, help="Number of pools to generate"
    )
    parser.add_argument(
        "--update-frequency", type=int, default=60, help="Update frequency in seconds"
    )
    parser.add_argument(
        "--base-liquidity", type=float, default=1000000, help="Base liquidity amount"
    )
    parser.add_argument(
        "--output", type=str, default="historical_data.json", help="Output file path"
    )

    args = parser.parse_args()

    # Parse dates
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    # Generate data
    generator = HistoricalDataGenerator(
        start_date=start_date,
        end_date=end_date,
        num_pools=args.num_pools,
        update_frequency_seconds=args.update_frequency,
        base_liquidity=args.base_liquidity,
    )

    data = generator.generate_data()

    # Save to file
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated historical data saved to: {output_path}")
    print(f"Total events: {len(data['events'])}")
    print(f"Pools created: {data['summary']['pool_creations']}")
    print(f"Price updates: {data['summary']['price_updates']}")


if __name__ == "__main__":
    main()
