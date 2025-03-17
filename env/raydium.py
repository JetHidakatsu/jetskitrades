async def execute_swap(self, signature: str, size: float, pool_info: Dict[str, Any] = None) -> bool:
    self.latency_tracker.record_event(f"swap_start_{signature}")
    try:
        if size > self.initial_capital:
            self.logger.error(f"Size {size} exceeds capital {self.initial_capital}")
            return False
        pool_info = pool_info or await self._fetch_pool_info(signature)
        if not await self.analyze_liquidity(pool_info["pool_address"]):
            return False
        tx = await self.build_swap_transaction(pool_info, size)
        tx_id = await self._send_with_retry(tx, signature)
        self.latency_tracker.record_event(f"swap_end_{signature}")
        return True
    except Exception as e:
        self.logger.error(f"Swap failed: {e}", exc_info=True)
        return False
