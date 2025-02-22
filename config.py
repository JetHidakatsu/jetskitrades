import os
from dotenv import load_dotenv
from typing import Optional

"""
Configuration file for Solana trading bot.

This file loads environment variables and sets default values for various 
parameters used in the trading bot, including API endpoints, trading logic, 
and technical analysis settings.
"""

# Load environment variables from .env file
load_dotenv()

# API configurations
API_HOST: Optional[str] = os.getenv('API_HOST')
QUICKNODE_WS_URL: Optional[str] = os.getenv('QUICKNODE_WS_URL')
QUICKNODE_RPC_URL: Optional[str] = os.getenv('QUICKNODE_RPC_URL')
RAYDIUM_API_HOST_SWAP: Optional[str] = os.getenv('RAYDIUM_API_HOST_SWAP')
RAYDIUM_API_HOST_POOLS: Optional[str] = os.getenv('RAYDIUM_API_HOST_POOLS')
RAYDIUM_API_HOST_TOKEN_LIST: Optional[str] = os.getenv('RAYDIUM_API_HOST_TOKEN_LIST')
GMGN_ROUTER_API: Optional[str] = os.getenv('GMGN_ROUTER_API')
GMGN_SUBMIT_TX_API: Optional[str] = os.getenv('GMGN_SUBMIT_TX_API')
GMGN_SUBMIT_BUNDLE_TX_API: Optional[str] = os.getenv('GMGN_SUBMIT_BUNDLE_TX_API')
GMGN_TX_STATUS_API: Optional[str] = os.getenv('GMGN_TX_STATUS_API')

# Token trading configurations
inputToken: Optional[str] = os.getenv('INPUT_TOKEN')
outputToken: Optional[str] = os.getenv('OUTPUT_TOKEN')

# Error handling for TRADE_AMOUNT to ensure it's an integer
try:
    amount = int(os.getenv('TRADE_AMOUNT', '0'))
except ValueError:
    print("TRADE_AMOUNT must be an integer. Using default value 0.")
    amount = 0

fromAddress: Optional[str] = os.getenv('FROM_ADDRESS')

# Error handling for SLIPPAGE to ensure it's a float
try:
    slippage = float(os.getenv('SLIPPAGE', '0.01'))
except ValueError:
    print("SLIPPAGE must be a float. Using default value 0.01")
    slippage = 0.01

# Sensitive information - Ensure this is securely stored in .env and not exposed
PRIVATE_KEY: Optional[str] = os.getenv('PRIVATE_KEY')

# CPMM Pool Program IDs
CREATE_CPMM_POOL_PROGRAM: Optional[str] = os.getenv('CREATE_CPMM_POOL_PROGRAM_ID', 'INSERT_ACTUAL_ID_HERE')
# Please replace 'INSERT_ACTUAL_ID_HERE' with the actual program ID if available
DEV_CREATE_CPMM_POOL_PROGRAM: Optional[str] = os.getenv('DEV_CREATE_CPMM_POOL_PROGRAM_ID', '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin')

# Constants for trading parameters
# TODO: Consider if these values need to be configurable or if they're fixed
INITIAL_INVESTMENT = 25
RISK_PER_TRADE = 0.04
PROFIT_TARGET = 2.0
STOP_LOSS = 0.8

# API rate limits
TWITTER_API_RATE_LIMIT = 100
SOLANA_API_RATE_LIMIT = 10

# Technical Analysis parameters
SHORT_SMA_PERIOD = 10
LONG_SMA_PERIOD = 50
RSI_PERIOD = 14

# Memecoin-specific parameters
MEMECOIN_VOLATILITY_FACTOR = 2.0  
MEMECOIN_LIQUIDITY_THRESHOLD = 100000

# Quantum configuration
QUANTUM_ENABLED = bool(os.getenv("QUANTUM_ENABLED", False))
QUANTUM_BACKEND = os.getenv("QUANTUM_BACKEND", "ibmq_qasm_simulator")
QUANTUM_TIMEOUT = float(os.getenv("QUANTUM_TIMEOUT", 1.0))
QUANTUM_MAX_TIMEOUT = float(os.getenv("QUANTUM_MAX_TIMEOUT", 5.0))
QUANTUM_METRICS = os.getenv("QUANTUM_METRICS", "liquidity,slippage").split(",")
HYBRID_MODE = bool(os.getenv("HYBRID_MODE", True))

# TODO: Add validation for parameters if needed, e.g., ensuring slippage is within a reasonable range
# Example:
# if slippage < 0 or slippage > 0.1:
#     raise ValueError("Slippage must be between 0 and 0.1")

# TODO: If working in a team or for future reference, consider adding more detailed comments or docstrings for each section or important parameter
