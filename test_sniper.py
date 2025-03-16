"""Test script for memecoin sniper bot"""

import asyncio
import logging
from env.memecoin_sniper import MemecoinSniper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_sniper():
    """Run the sniper bot in test mode"""
    try:
        # Create and start the sniper bot
        sniper = MemecoinSniper()

        # Start the bot
        await sniper.start()

        # Run for test duration (5 minutes)
        logging.info("Running sniper bot for 5 minutes...")
        await asyncio.sleep(300)

        # Stop the bot
        await sniper.stop()

        # Log final stats
        logging.info("Test completed. Final statistics:")
        logging.info(f"Total trades: {sniper.total_trades}")
        logging.info(f"Successful trades: {sniper.successful_trades}")
        logging.info(f"Total profit: {sniper.total_profit:.6f} SOL")

    except Exception as e:
        logging.error(f"Error in test: {e}")
        raise
    finally:
        # Ensure bot is stopped
        if sniper:
            await sniper.stop()


def main():
    """Main entry point"""
    try:
        # Run the test
        asyncio.run(test_sniper())
    except KeyboardInterrupt:
        logging.info("Test interrupted by user")
    except Exception as e:
        logging.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
