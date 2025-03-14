import aiohttp
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

from config import *
from utils import *


class RaydiumSDK:
    def __init__(self):
        self.cluster = "mainnet"
        self.api = RaydiumAPI()
        self.cpmm = RaydiumCPMM()

    async def initialize(self):
        """Initialize connection to Raydium services."""
        try:
            await self.api.initialize_connection()
            await self.cpmm.setup_rpc_client()
            print(f"Raydium SDK initialized for cluster: {self.cluster}")
            return self
        except Exception as e:
            logging.error(f"Failed to initialize Raydium SDK: {e}")
            raise


class RaydiumAPI:
    async def initialize_connection(self):
        """
        Initialize the connection for Raydium API.
        """
        self.session = aiohttp.ClientSession()
        print("Raydium API connection initialized")

    async def fetch_pool_by_id(self, ids: list[str]):
        """
        Fetch pool information by their ID from the Raydium API.
        """
        url = f"{RAYDIUM_API_HOST_POOLS}/pda"
        params = {"ids": ",".join(ids)}
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                logging.error(
                    f"Failed to fetch pool by ID from Raydium. Status: {response.status}"
                )
                return []


class RaydiumCPMM:
    async def setup_rpc_client(self):
        """
        Setup the RPC client for interacting with Solana network.
        """
        self.rpc_client = AsyncClient(QUICKNODE_RPC_URL)
        print("Raydium CPMM RPC client setup")

    async def get_pool_info_from_rpc(self, pool_id: str):
        """
        Retrieve pool information directly from Solana's RPC.
        """
        # Implementation would involve querying the Solana blockchain directly
        # Here's a mock response:
        return {"poolInfo": {"id": pool_id, "locked": False, "state": "ACTIVE"}}


class RaydiumUtils:
    @staticmethod
    def is_valid_cpmm(program_id: str) -> bool:
        """
        Check if the given program ID is valid for a CPMM pool.

        :param program_id: The program ID to check.
        :return: Boolean indicating if the program ID is valid for a CPMM pool.
        """
        valid_ids = {CREATE_CPMM_POOL_PROGRAM, DEV_CREATE_CPMM_POOL_PROGRAM}
        return program_id in valid_ids


@solana_api_limit
async def get_token_price(token_address):
    api_url = f"{RAYDIUM_API_HOST_POOLS}?mint={token_address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and "data" in data and data["data"]:
                        pools = data["data"]
                        pools_sorted = sorted(
                            pools, key=lambda x: x.get("liquidity", 0), reverse=True
                        )
                        if pools_sorted:
                            price = pools_sorted[0].get("price", 0.0)
                            logging.info(
                                f"Successfully fetched price for token {token_address}: {price}"
                            )
                            return price
                        else:
                            logging.warning(
                                f"No valid price data for token {token_address}"
                            )
                            return 0.0
                else:
                    logging.warning(
                        f"Failed to fetch price from Raydium for {token_address}. Status: {response.status}"
                    )
                    return 0.0
    except aiohttp.ClientError as e:
        logging.error(
            f"Network error when fetching token price for {token_address}: {e}"
        )
        return 0.0
    except ValueError as e:
        logging.error(f"ValueError when parsing price data for {token_address}: {e}")
        return 0.0
    except Exception as e:
        logging.error(f"Unexpected error fetching token price for {token_address}: {e}")
        return 0.0
