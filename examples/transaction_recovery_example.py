import asyncio
import logging
from datetime import datetime

from ..env.config import Config
from ..env.database_manager import DatabaseManager
from ..env.event_manager import EventManager
from ..env.rpc_manager import RPCManager
from ..env.helius_provider import HeliusProvider
from ..env.notification_manager import NotificationManager
from ..env.transaction_recovery_manager import TransactionRecoveryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_transaction_success(data):
    """Handle successful transaction events"""
    tx_id = data["tx_id"]
    logger.info(f"Transaction {tx_id} completed successfully!")
    logger.info(f"Original transaction: {data['original_tx']}")
    logger.info(f"Metadata: {data['metadata']}")

async def handle_transaction_failure(data):
    """Handle failed transaction events"""
    tx_id = data["tx_id"]
    failure_reason = data["failure_reason"]
    retry_count = data["retry_count"]
    logger.error(f"Transaction {tx_id} failed permanently")
    logger.error(f"Reason: {failure_reason}")
    logger.error(f"Attempted {retry_count} retries")

async def handle_recovery_attempt(data):
    """Handle recovery attempt notifications"""
    tx_id = data["tx_id"]
    attempt = data["attempt"]
    strategy = data["strategy"]
    logger.info(f"Attempting recovery for {tx_id}")
    logger.info(f"Attempt {attempt} using strategy: {strategy}")

async def main():
    # Initialize configuration
    config = Config({
        "recovery": {
            "max_retries": 3,
            "retry_delay_base": 5,
            "retry_delay_max": 60,
            "transaction_timeout": 90
        },
        "rpc": {
            "endpoint": "https://api.mainnet-beta.solana.com",
            "timeout": 30
        },
        "helius": {
            "api_key": "your_helius_api_key"
        }
    })

    # Initialize components
    db_manager = DatabaseManager(config)
    event_manager = EventManager(config, db_manager)
    rpc_manager = RPCManager(config)
    helius_provider = HeliusProvider(config)
    notification_manager = NotificationManager(config)

    # Initialize recovery manager
    recovery_manager = TransactionRecoveryManager(
        config,
        db_manager,
        event_manager,
        rpc_manager,
        helius_provider,
        notification_manager
    )

    # Register event handlers
    event_manager.on("transaction_success", handle_transaction_success)
    event_manager.on("transaction_failure", handle_transaction_failure)
    event_manager.on("recovery_attempt", handle_recovery_attempt)

    try:
        # Example transaction data
        transaction = {
            "instructions": [
                # Your transaction instructions here
            ],
            "signers": [
                # Your transaction signers here
            ],
            "recent_blockhash": "your_recent_blockhash"
        }

        # Example metadata
        metadata = {
            "type": "swap",
            "token_in": "SOL",
            "token_out": "USDC",
            "amount": "1.5",
            "timestamp": datetime.now().isoformat()
        }

        # Submit transaction
        tx_id = await rpc_manager.submit_transaction(transaction)
        logger.info(f"Transaction submitted with ID: {tx_id}")

        # Register transaction for recovery monitoring
        state = await recovery_manager.register_transaction(
            tx_id,
            transaction,
            metadata
        )
        logger.info(f"Transaction registered for recovery monitoring: {state.tx_id}")

        # Monitor transaction status
        while True:
            status = await recovery_manager.check_transaction_status(tx_id)
            logger.info(f"Current status: {status}")

            if status in ["confirmed", "failed"]:
                break

            await asyncio.sleep(2)

        # Get recovery statistics
        stats = await recovery_manager.get_recovery_stats()
        logger.info("Recovery Statistics:")
        logger.info(f"Total monitored: {stats['total_monitored']}")
        logger.info(f"Pending: {stats['pending']}")
        logger.info(f"Recovered: {stats['recovered']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Success rate: {stats['success_rate']}%")

    except Exception as e:
        logger.error(f"Error in transaction recovery example: {e}")
        raise

    finally:
        # Cleanup
        await recovery_manager.cleanup()

def run_example():
    """Run the example"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Example stopped by user")
    except Exception as e:
        logger.error(f"Example failed: {e}")

if __name__ == "__main__":
    run_example()
