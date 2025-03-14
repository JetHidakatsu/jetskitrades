import asyncio
import logging
import traceback
from env.trading_bot_v2 import TradingBot


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting the Solana Memecoin Sniper Bot")

    try:
        logger.debug("Initializing TradingBot")
        bot = TradingBot()

        logger.info("Starting the bot")
        await bot.start()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
    finally:
        if "bot" in locals():
            logger.info("Stopping the bot")
            await bot.stop()

    logger.info("Bot execution completed")


if __name__ == "__main__":
    asyncio.run(main())
