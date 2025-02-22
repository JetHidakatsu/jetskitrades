"use strict";

// Import necessary modules
const { Connection, PublicKey, Transaction, sendAndConfirmTransaction, Keypair } = require('@solana/web3.js');
const { Liquidity, TokenAmount, Token, ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, createAssociatedTokenAccountInstruction } = require('@raydium-io/raydium-sdk-v2');
const axios = require('axios');
const dotenv = require('dotenv');
const WebSocket = require('ws');
import { getPoolInfo } from '@raydium-io/raydium-sdk-v2';
import { Connection, PublicKey } from '@solana/web3.js';


// Load environment variables
dotenv.config();

// Environment variables
const API_HOST = process.env.API_HOST || 'https://gmgn.ai';
const QUICKNODE_RPC_URL = process.env.QUICKNODE_RPC_URL || 'https://rough-yolo-field.solana-devnet.quiknode.pro/cfe6c9225dfa33924303c370a4bec1be97ca281d/';
const QUICKNODE_WS_URL = process.env.QUICKNODE_WS_URL || "wss://rough-yolo-field.solana-devnet.quiknode.pro/cfe6c9225dfa33924303c370a4bec1be97ca281d";

// Raydium API specifics
const RAYDIUM_API_HOST_SWAP = "https://transaction-v1.raydium.io/";
const RAYDIUM_API_HOST_POOLS = "https://api.raydium.io/v2/main/pools/pda";

// Solana network connection
const connection = new Connection(QUICKNODE_RPC_URL, 'confirmed');

// Token mints
const SOL_MINT = new PublicKey('So11111111111111111111111111111111111111112'); // Wrapped SOL
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'); // USDC

// Wallet setup
const WALLET_PUBLIC_KEY = new PublicKey(process.env.WALLET_PUBLIC_KEY);
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const secretKey = Uint8Array.from(Buffer.from(PRIVATE_KEY, 'base58'));
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

async function fetchPoolData(connection) { // pass in your solana connection
    try {
        // 1. Instead of fetching pool PDA addresses, we'll iterate over *known* pool addresses (you might need to hardcode these or fetch a smaller, curated list)
        const knownPoolAddresses = [
            'AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA', // RAY-SOL
            '6UmmUiYoBjSrhakAobJw8BvkmJtDVxaeBtbt7rxWo1mg'  // RAY-USDC
        ];

        const solUsdcPools = [];
        for (const poolAddress of knownPoolAddresses) {
            try {
                const poolInfo = await getPoolInfo(connection, new PublicKey(poolAddress));
                // 2. Filter for pools containing sol and usdc (this part stays the same)
                if (poolInfo.baseMint.equals(SOL_MINT) && poolInfo.quoteMint.equals(USDC_MINT)) {
                    solUsdcPools.push(poolInfo);
                }
            } catch (error) {
                console.error(`Error fetching pool info for ${poolAddress}:`, error);
            }
        }

        console.log("SOL/USDC Pools:", solUsdcPools);
    } catch (error) {
        console.error("Error fetching pool data:", error);
    }
}

// Function to perform a swap
async function performSwap() {
    try {
        const poolKeys = await Liquidity.fetchPoolKeys(connection, { baseMint: SOL_MINT, quoteMint: USDC_MINT });
        
        if (!poolKeys) {
            console.log("No pool found for the specified token pair.");
            return;
        }

        const amountIn = new TokenAmount(new Token(SOL_MINT, 9), 1); // 1 SOL
        const slippage = 0.05; // 5% slippage tolerance

        // Ensure associated token accounts exist
        const sourceTokenAccount = await ensureAssociatedTokenAccount(SOL_MINT, WALLET_PUBLIC_KEY);
        const destinationTokenAccount = await ensureAssociatedTokenAccount(USDC_MINT, WALLET_PUBLIC_KEY);

        const swapInstruction = await Liquidity.makeSwapInstruction({
            poolKeys,
            userKeys: {
                tokenAccounts: {
                    sourceToken: sourceTokenAccount,
                    destinationToken: destinationTokenAccount
                },
                owner: WALLET_PUBLIC_KEY, // Correctly define the owner property with a PublicKey
            },
            amountIn,
            amountOut: null,
            fixedSide: 'in',
            config: {
                slippage
            }
        });

        // Create transaction
        const transaction = new Transaction().add(swapInstruction);

        // Send and confirm transaction
        const signature = await sendAndConfirmTransaction(connection, transaction, [walletKeypair]);
        console.log("Transaction completed with signature:", signature);

    } catch (error) {
        console.error("Failed to perform swap:", error);
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

const solanaApiLimit = rateLimit(10, 6000); // 100 calls per minute

// Main execution
async function main() {
    await fetchPoolData();
    await performSwap();
    setupWebSocket();
    // Here you might call solanaApiLimit() before any API call to ensure rate limiting
}

main().catch(console.error);