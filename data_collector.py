#!/usr/bin/env python3
"""Data collection utility for backtesting and analysis"""

import asyncio
import argparse
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
import pandas as pd
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import base58
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey


@dataclass
class DataCollectionConfig:
    """Configuration for data collection"""

    start_date: datetime
    end_date: datetime
    rpc_url: str
    program_id: str
    save_dir: Path
    batch_size: int = 100
    request_delay: float = 0.1


class DataCollector:
    """Collect and process historical trading data"""

    def __init__(self, config: DataCollectionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = AsyncClient(config.rpc_url)
        self.processed_signatures: Set[str] = set()

    async def collect_data(self):
        """Collect historical data"""
        try:
            # Create save directory
            self.config.save_dir.mkdir(parents=True, exist_ok=True)

            # Collect different types of data
            await asyncio.gather(
                self._collect_pool_data(),
                self._collect_price_data(),
                self._collect_market_events(),
            )

            # Process and combine data
            await self._process_collected_data()

        except Exception as e:
            self.logger.error(f"Error collecting data: {e}")
            raise
        finally:
            await self.client.close()

    async def _collect_pool_data(self):
        """Collect historical pool creation and configuration data"""
        try:
            self.logger.info("Collecting pool data...")

            # Get program signatures
            signatures = await self._get_program_signatures()

            # Process signatures in batches
            pools_data = []
            for i in range(0, len(signatures), self.config.batch_size):
                batch = signatures[i : i + self.config.batch_size]

                # Get transaction data
                batch_data = await asyncio.gather(
                    *[self._get_transaction_data(sig) for sig in batch]
                )

                # Filter and process pool creations
                for tx_data in batch_data:
                    if tx_data and self._is_pool_creation(tx_data):
                        pool_data = await self._extract_pool_data(tx_data)
                        if pool_data:
                            pools_data.append(pool_data)

                await asyncio.sleep(self.config.request_delay)

            # Save pool data
            self._save_data(pools_data, "pool_data.json")

        except Exception as e:
            self.logger.error(f"Error collecting pool data: {e}")
            raise

    async def _collect_price_data(self):
        """Collect historical price data"""
        try:
            self.logger.info("Collecting price data...")

            # Load pool data to get pool addresses
            pools = self._load_data("pool_data.json")
            if not pools:
                return

            price_data = []
            for pool in pools:
                pool_address = pool.get("address")
                if not pool_address:
                    continue

                # Get historical account data
                historical_data = await self._get_historical_account_data(pool_address)

                # Extract price data
                pool_prices = self._extract_price_data(historical_data)
                if pool_prices:
                    price_data.extend(pool_prices)

                await asyncio.sleep(self.config.request_delay)

            # Save price data
            self._save_data(price_data, "price_data.json")

        except Exception as e:
            self.logger.error(f"Error collecting price data: {e}")
            raise

    async def _collect_market_events(self):
        """Collect market events and metadata"""
        try:
            self.logger.info("Collecting market events...")

            # Get program signatures for market events
            signatures = await self._get_program_signatures(
                until=self.config.end_date, event_type="market"
            )

            events_data = []
            for i in range(0, len(signatures), self.config.batch_size):
                batch = signatures[i : i + self.config.batch_size]

                # Get transaction data
                batch_data = await asyncio.gather(
                    *[self._get_transaction_data(sig) for sig in batch]
                )

                # Process market events
                for tx_data in batch_data:
                    if tx_data:
                        event_data = self._extract_market_event(tx_data)
                        if event_data:
                            events_data.append(event_data)

                await asyncio.sleep(self.config.request_delay)

            # Save market events
            self._save_data(events_data, "market_events.json")

        except Exception as e:
            self.logger.error(f"Error collecting market events: {e}")
            raise

    async def _get_program_signatures(
        self, until: Optional[datetime] = None, event_type: str = "pool"
    ) -> List[str]:
        """Get program transaction signatures"""
        signatures = []
        until = until or self.config.end_date

        try:
            # Get initial batch
            response = await self.client.get_signatures_for_address(
                Pubkey.from_string(self.config.program_id), limit=1000
            )

            if not response or "result" not in response:
                return signatures

            # Process signatures
            for item in response["result"]:
                sig = item.get("signature")
                timestamp = datetime.fromtimestamp(item.get("blockTime", 0))

                if timestamp < self.config.start_date:
                    break

                if timestamp <= until and sig not in self.processed_signatures:
                    signatures.append(sig)
                    self.processed_signatures.add(sig)

            return signatures

        except Exception as e:
            self.logger.error(f"Error getting program signatures: {e}")
            return signatures

    async def _get_transaction_data(self, signature: str) -> Optional[Dict]:
        """Get transaction data"""
        try:
            response = await self.client.get_transaction(
                signature, encoding="jsonParsed"
            )

            if response and "result" in response:
                return response["result"]
            return None

        except Exception as e:
            self.logger.error(f"Error getting transaction data: {e}")
            return None

    async def _get_historical_account_data(self, address: str) -> List[Dict]:
        """Get historical account data"""
        try:
            response = await self.client.get_account_info(
                Pubkey.from_string(address), encoding="jsonParsed"
            )

            if response and "result" in response:
                return response["result"].get("value", {}).get("data", [])
            return []

        except Exception as e:
            self.logger.error(f"Error getting account data: {e}")
            return []

    def _is_pool_creation(self, tx_data: Dict) -> bool:
        """Check if transaction is pool creation"""
        try:
            if not tx_data.get("meta", {}).get("logMessages"):
                return False

            logs = tx_data["meta"]["logMessages"]
            return any("initialize2" in log for log in logs)

        except Exception:
            return False

    async def _extract_pool_data(self, tx_data: Dict) -> Optional[Dict]:
        """Extract pool data from transaction"""
        try:
            timestamp = datetime.fromtimestamp(tx_data.get("blockTime", 0))

            # Extract pool address and other metadata
            pool_address = None
            creator_address = None

            for account in tx_data.get("meta", {}).get("postTokenBalances", []):
                if account.get("owner"):
                    creator_address = account["owner"]
                    break

            for account in (
                tx_data.get("transaction", {}).get("message", {}).get("accountKeys", [])
            ):
                if account.get("programId") == self.config.program_id:
                    pool_address = account.get("pubkey")
                    break

            if not pool_address:
                return None

            return {
                "timestamp": timestamp.isoformat(),
                "address": pool_address,
                "creator_address": creator_address,
                "signature": tx_data.get("transaction", {}).get("signatures", [None])[
                    0
                ],
                "type": "pool_creation",
            }

        except Exception as e:
            self.logger.error(f"Error extracting pool data: {e}")
            return None

    def _extract_price_data(self, account_data: List[Dict]) -> List[Dict]:
        """Extract price data from account data"""
        try:
            price_data = []

            for data in account_data:
                if isinstance(data, list) and len(data) >= 2:
                    # Decode and extract price
                    raw_data = base58.b58decode(data[0])
                    if len(raw_data) >= 16:
                        # Extract price from appropriate offset
                        price = int.from_bytes(raw_data[8:16], "little") / 1e9

                        price_data.append(
                            {
                                "timestamp": datetime.now().isoformat(),  # Current time as placeholder
                                "price": price,
                                "type": "price_update",
                            }
                        )

            return price_data

        except Exception as e:
            self.logger.error(f"Error extracting price data: {e}")
            return []

    def _extract_market_event(self, tx_data: Dict) -> Optional[Dict]:
        """Extract market event data"""
        try:
            timestamp = datetime.fromtimestamp(tx_data.get("blockTime", 0))

            # Extract relevant event data
            event_type = None
            if "swap" in str(tx_data):
                event_type = "swap"
            elif "deposit" in str(tx_data):
                event_type = "deposit"
            elif "withdraw" in str(tx_data):
                event_type = "withdraw"

            if not event_type:
                return None

            return {
                "timestamp": timestamp.isoformat(),
                "signature": tx_data.get("transaction", {}).get("signatures", [None])[
                    0
                ],
                "type": f"market_{event_type}",
            }

        except Exception as e:
            self.logger.error(f"Error extracting market event: {e}")
            return None

    async def _process_collected_data(self):
        """Process and combine collected data"""
        try:
            self.logger.info("Processing collected data...")

            # Load all data
            pools = self._load_data("pool_data.json")
            prices = self._load_data("price_data.json")
            events = self._load_data("market_events.json")

            if not pools:
                return

            # Combine data chronologically
            all_data = []
            all_data.extend(pools)
            all_data.extend(prices)
            all_data.extend(events)

            # Sort by timestamp
            all_data.sort(key=lambda x: x.get("timestamp", ""))

            # Save combined data
            self._save_data(all_data, "historical_data.json")

            # Create summary
            summary = {
                "total_pools": len(pools),
                "total_price_updates": len(prices),
                "total_market_events": len(events),
                "date_range": {
                    "start": self.config.start_date.isoformat(),
                    "end": self.config.end_date.isoformat(),
                },
            }

            self._save_data(summary, "data_summary.json")

        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            raise

    def _save_data(self, data: List[Dict], filename: str):
        """Save data to file"""
        try:
            filepath = self.config.save_dir / filename
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            raise

    def _load_data(self, filename: str) -> List[Dict]:
        """Load data from file"""
        try:
            filepath = self.config.save_dir / filename
            if not filepath.exists():
                return []

            with open(filepath) as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return []


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Historical Data Collector")

    parser.add_argument("--rpc-url", type=str, required=True, help="Solana RPC URL")
    parser.add_argument(
        "--program-id", type=str, required=True, help="Raydium program ID"
    )
    parser.add_argument(
        "--start-date", type=str, required=True, help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", type=str, required=True, help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--save-dir", type=str, default="data", help="Directory to save collected data"
    )
    parser.add_argument(
        "--batch-size", type=int, default=100, help="Batch size for requests"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create config
    config = DataCollectionConfig(
        start_date=datetime.fromisoformat(args.start_date),
        end_date=datetime.fromisoformat(args.end_date),
        rpc_url=args.rpc_url,
        program_id=args.program_id,
        save_dir=Path(args.save_dir),
        batch_size=args.batch_size,
    )

    # Run collection
    try:
        collector = DataCollector(config)
        asyncio.run(collector.collect_data())
    except Exception as e:
        logging.error(f"Data collection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
