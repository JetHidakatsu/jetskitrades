// Import necessary modules
const { Connection, PublicKey, Transaction, sendAndConfirmTransaction, Keypair, VersionedTransaction } = require('@solana/web3.js');
const { Liquidity, TokenAmount, Token, ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, createAssociatedTokenAccountInstruction } = require('@raydium-io/raydium-sdk-v2');
const axios = require('axios');
const dotenv = require('dotenv');
const WebSocket = require('ws');

// Load environment variables
dotenv.config();

// Environment variables
const API_HOST = process.env.API_HOST || 'https://gmgn.ai';
const QUICKNODE_RPC_URL = process.env.QUICKNODE_RPC_URL || 'https://rough-yolo-field.solana-devnet.quiknode.pro/cfe6c9225dfa33924303c370a4bec1be97ca281d';
const QUICKNODE_WS_URL = process.env.QUICKNODE_WS_URL || "wss://rough-yolo-field.solana-devnet.quiknode.pro/cfe6c9225dfa33924303c370a4bec1be97ca281d";

// Raydium API specifics
const RAYDIUM_API_HOST_POOLS = "https://api.raydium.io/v2/main/pools/pda";

// Solana network connection
const connection = new Connection(QUICKNODE_RPC_URL, 'confirmed');

// Token mints
const SOL_MINT = new PublicKey('So11111111111111111111111111111111111111112'); // Wrapped SOL
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'); // USDC

// Wallet setup
const WALLET_PUBLIC_KEY = new PublicKey(process.env.WALLET_PUBLIC_KEY);
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const secretKey = Uint8Array.from(Buffer.from(PRIVATE_KEY, 'base64'));
const walletKeypair = Keypair.fromSecretKey(secretKey);

// Function to ensure associated token account exists
async function ensureAssociatedTokenAccount(mint, owner) {
    const associatedTokenAddress = await Token.getAssociatedTokenAddress(
        ASSOCIATED_TOKEN_PROGRAM_ID, 
        TOKEN_PROGRAM_ID, 
        mint, 
        owner
    );

    const accountInfo = await connection.getAccountInfo(associatedTokenAddress);
    if (!accountInfo) {
        const transaction = new Transaction().add(
            createAssociatedTokenAccountInstruction(
                owner,
                associatedTokenAddress,
                owner,
                mint
            )
        );
        await sendAndConfirmTransaction(connection, transaction, [walletKeypair], {
            skipPreflight: true
        });
    }
    return associatedTokenAddress;
}

async function fetchPoolData() {
    try {
        // Fetch pool data from Raydium API
        const response = await axios.get(RAYDIUM_API_HOST_POOLS);
        const pools = response.data.data || [];

        // Filter for SOL/USDC pools
        const solUsdcPools = pools.filter(pool => 
            (pool.baseMint === SOL_MINT.toBase58() && pool.quoteMint === USDC_MINT.toBase58()) ||
            (pool.baseMint === USDC_MINT.toBase58() && pool.quoteMint === SOL_MINT.toBase58())
        );

        console.log("SOL/USDC Pools:", solUsdcPools);
    } catch (error) {
        console.error("Error fetching pool data:", error);
    }
}

// Function to perform a swap using GMGN
async function performSwap() {
    try {
        const amountIn = '100000000'; // 0.1 SOL in lamports
        const slippage = '0.5'; // 0.5% slippage tolerance

        const quoteUrl = `${API_HOST}/defi/router/v1/sol/tx/get_swap_route?token_in_address=${SOL_MINT.toBase58()}&token_out_address=${USDC_MINT.toBase58()}&in_amount=${amountIn}&from_address=${WALLET_PUBLIC_KEY.toBase58()}&slippage=${slippage}`;
        
        const routeResponse = await axios.get(quoteUrl);
        const routeData = routeResponse.data;

        if (routeData.code !== 0) {
            throw new Error(`Failed to get swap route: ${routeData.msg}`);
        }

        // Ensure associated token accounts exist
        await ensureAssociatedTokenAccount(SOL_MINT, WALLET_PUBLIC_KEY);
        await ensureAssociatedTokenAccount(USDC_MINT, WALLET_PUBLIC_KEY);

        const swapTransactionBuf = Buffer.from(routeData.data.raw_tx.swapTransaction, 'base64');
        const transaction = VersionedTransaction.deserialize(swapTransactionBuf);
        
        transaction.sign([walletKeypair]);

        const signedTx = Buffer.from(transaction.serialize()).toString('base64');

        // Submit transaction through GMGN
        const submitResponse = await axios.post(`${API_HOST}/defi/router/v1/sol/tx/submit_signed_transaction`, {
            signed_tx: signedTx
        });

        if (submitResponse.data.code !== 0) {
            throw new Error(`Failed to submit transaction: ${submitResponse.data.msg}`);
        }

        const transactionHash = submitResponse.data.data.hash;
        const lastValidBlockHeight = routeData.data.raw_tx.lastValidBlockHeight;

        // Check transaction status
        await checkTransactionStatus(transactionHash, lastValidBlockHeight);

        console.log("Transaction completed with hash:", transactionHash);

    } catch (error) {
        console.error("Failed to perform swap with GMGN:", error);
    }
}

// Function to check transaction status
async function checkTransactionStatus(hash, lastValidBlockHeight) {
    while (true) {
        const statusUrl = `${API_HOST}/defi/router/v1/sol/tx/get_transaction_status?hash=${hash}&last_valid_height=${lastValidBlockHeight}`;
        const statusResponse = await axios.get(statusUrl);
        const status = statusResponse.data;

        console.log('Transaction Status:', status);

        if (status.data && (status.data.success === true || status.data.expired === true)) {
            if (status.data.success) {
                console.log("Transaction succeeded!");
            } else {
                console.log("Transaction expired!");
            }
            break;
        }
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for 1 second before checking again
    }
}

// WebSocket setup function inspired by Python script
function setupWebSocket() {
    const ws = new WebSocket(QUICKNODE_WS_URL);
    
    ws.on('open', () => {
        console.log('WebSocket Connected');
        ws.send(JSON.stringify({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [
                {"mentions": [WALLET_PUBLIC_KEY.toBase58()]},
                {"commitment": "finalized"}
            ]
        }));
    });

    ws.on('message', (data) => {
        console.log(`Received: ${data}`);
    });

    ws.on('close', () => {
        console.log('WebSocket Disconnected');
        setTimeout(setupWebSocket, 10000); // Reconnection logic
    });

    ws.on('error', (error) => {
        console.log(`WebSocket Error: ${error.message}`);
    });
}

// Rate Limiting function inspired by TypeScript script
function rateLimit(calls, period) {
    let lastCallTime = 0;
    let count = 0;

    return async function() {
        const now = Date.now();
        if (now - lastCallTime > period) {
            count = 0;
            lastCallTime = now;
        }
        if (count >= calls) {
            const waitTime = period - (now - lastCallTime);
            await new Promise(resolve => setTimeout(resolve, waitTime));
            lastCallTime = Date.now();
            count = 0;
        }
        count++;
    };
}

const solanaApiLimit = rateLimit(10, 60000); // 10 calls per minute

// Main execution
async function main() {
    await fetchPoolData(); // You might want to keep this for comparison or other uses
    await performSwap();
    setupWebSocket();
    // Use rate limiting for subsequent API calls if necessary
}

main().catch(console.error);