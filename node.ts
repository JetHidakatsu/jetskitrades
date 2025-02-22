import { strict as assert } from 'assert';
import { 
  Connection, 
  PublicKey, 
  Transaction, 
  sendAndConfirmTransaction, 
  Keypair, 
  ComputeBudgetProgram, 
  TransactionInstruction 
} from '@solana/web3.js';
import { 
  getAssociatedTokenAddress, 
  createAssociatedTokenAccountInstruction,
  TOKEN_PROGRAM_ID, 
  ASSOCIATED_TOKEN_PROGRAM_ID 
} from '@solana/spl-token';
import * as dotenv from 'dotenv';
import axios from 'axios';
import bs58 from 'bs58';
import WebSocket from 'ws';
import Bottleneck from 'bottleneck';

dotenv.config();

// Environment variables
const API_HOST: string = process.env.API_HOST || 'raydium.io/api';
const QUICKNODE_RPC_URL: string = process.env.QUICKNODE_RPC_URL || 'https://api.devnet.solana.com';
const QUICKNODE_WS_URL: string = process.env.QUICKNODE_WS_URL || 'wss://api.devnet.solana.com';
const PRIVATE_KEY: string = process.env.PRIVATE_KEY!;

const connection = new Connection(QUICKNODE_RPC_URL, 'confirmed');

const SOL_MINT: PublicKey = new PublicKey('So11111111111111111111111111111111111111112');
const WALLET_PUBLIC_KEY: PublicKey = new PublicKey(process.env.WALLET_PUBLIC_KEY!);

const secretKey: Uint8Array = bs58.decode(PRIVATE_KEY);
const walletKeypair: Keypair = Keypair.fromSecretKey(secretKey);

const RAYDIUM_API_HOST_SWAP = "https://transaction-v1.raydium.io/";
const RAYDIUM_API_HOST_POOLS = "https://api.raydium.io/v2/main/pools/pda";

function log(message: string) {
    console.log(`[${new Date().toISOString()}] ${message}`);
}

// Corrected rateLimit function
function rateLimit(calls: number, period: number): () => Promise<void> {
    const limiter = new Bottleneck({
        reservoir: calls, 
        reservoirRefreshAmount: calls,
        reservoirRefreshInterval: period, // in milliseconds
        maxConcurrent: 1,
        minTime: period / calls 
    });
    return async function() {
        await limiter.schedule(() => Promise.resolve());
    };
}

const solanaApiLimit = rateLimit(10, 60000); // 10 calls per minute

// Corrected ensureAssociatedTokenAccount function
async function ensureAssociatedTokenAccount(mint: PublicKey, owner: PublicKey): Promise<PublicKey> {
    try {
        const associatedTokenAddress = await getAssociatedTokenAddress(mint, owner, false, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID);
        let accountInfo = await connection.getAccountInfo(associatedTokenAddress);
        if (!accountInfo) {
            const transaction = new Transaction().add(
                createAssociatedTokenAccountInstruction(owner, associatedTokenAddress, owner, mint, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID)
            );
            await sendAndConfirmTransaction(connection, transaction, [walletKeypair], { skipPreflight: true });
        }
        return associatedTokenAddress;
    } catch (error: unknown) {
        if (error instanceof Error) {
            log(`Error ensuring associated token account: ${error.message}`);
        } else {
            log(`Error ensuring associated token account: ${JSON.stringify(error)}`);
        }
        throw error;
    }
}

// Corrected fetchPoolData function
async function fetchPoolData(): Promise<void> {
    try {
        const response = await axios.get(`${RAYDIUM_API_HOST_POOLS}?mint=${SOL_MINT.toBase58()}`);
        log(`Fetched pool data: ${JSON.stringify(response.data)}`);
    } catch (error: unknown) {
        if (error instanceof Error) {
            log(`Error fetching pool data: ${error.message}`);
        } else {
            log(`Error fetching pool data: ${JSON.stringify(error)}`);
        }
    }
}

// Corrected performSwap function
async function performSwap(): Promise<void> {
    try {
        const swapParams = {
            inputMint: SOL_MINT.toBase58(),
            outputMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', // USDC mint address for example
            amount: '100000000', // 0.1 SOL in lamports
            fromAddress: WALLET_PUBLIC_KEY.toBase58(),
            slippage: '50'  // 0.5% slippage
        };
        
        const swapResponse = await axios.get(`${RAYDIUM_API_HOST_SWAP}/compute/swap-base-in`, {
            params: swapParams
        });
        
        if (swapResponse.data.success) {
            const transaction = Transaction.from(bs58.decode(swapResponse.data.data.swapTransaction));
            transaction.sign(walletKeypair);
            const signature = await sendAndConfirmTransaction(connection, transaction, [walletKeypair]);
            log(`Swap executed, transaction hash: ${signature}`);
        } else {
            log(`Swap failed: ${swapResponse.data.msg}`);
        }
    } catch (error: unknown) {
        if (error instanceof Error) {
            log(`Failed to perform swap: ${error.message}`);
        } else {
            log(`Failed to perform swap: ${JSON.stringify(error)}`);
        }
    }
}

// Assuming there was a missing closing brace here from the original error message
function setupWebSocket() {
    const ws = new WebSocket(QUICKNODE_WS_URL);
    
    ws.on('open', () => {
        log('WebSocket Connected');
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
        log(`Received: ${data}`);
    });

    ws.on('close', () => {
        log('WebSocket Disconnected');
        setTimeout(setupWebSocket, 10000); // Reconnection logic
    });

    ws.on('error', (error) => {
        log(`WebSocket Error: ${error.message}`);
    });
}

async function main(): Promise<void> {
    try {
        await fetchPoolData();
        await performSwap();
        setupWebSocket();
    } catch (error: unknown) {
        if (error instanceof Error) {
            log(`Error in main function: ${error.message}`);
        } else {
            log(`Error in main function: ${JSON.stringify(error)}`);
        }
    }
}

main();