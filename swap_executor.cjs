const { connection, publickey, keypair, transaction, sendandconfirmtransaction } = require('@solana/web3.js');
const { Liquidity, Token, TokenAmount, ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, createAssociatedTokenAccountInstruction } = require('@raydium-io/raydium-sdk');
const bs58 = require('bs58');

// Function to execute a swap
async function swap(pool_address, input_token_mint, output_token_mint, amount_in, private_key, quicknode_rpc_url) {
    try {
        // 1. Setup connection and wallet
        const connection = new Connection(quicknode_rpc_url, 'confirmed');
        const secretKey = bs58.decode(private_key);
        const walletKeypair = Keypair.fromSecretKey(secretKey);
        const walletPublicKey = walletKeypair.publicKey;

        // 2. Define token and pool addresses
        const poolKeys = await Liquidity.fetchInfo({
            connection,
            poolId: new PublicKey(pool_address)
        });

        if (!poolKeys) {
            throw new Error("No pool found for the specified token pair.");
        }

        const amountIn = new TokenAmount(new Token(new PublicKey(input_token_mint), 9), amount_in); // Assuming 9 decimals
        const slippage = 0.05; // 5% slippage tolerance

        // Ensure associated token accounts exist
        const sourceTokenAccount = await ensureAssociatedTokenAccount(new PublicKey(input_token_mint), walletPublicKey, connection, walletKeypair);
        const destinationTokenAccount = await ensureAssociatedTokenAccount(new PublicKey(output_token_mint), walletPublicKey, connection, walletKeypair);

        const { instructions, signers } = await Liquidity.makeSwapInstruction({
            poolKeys,
            userKeys: {
                tokenAccounts: {
                    source: sourceTokenAccount,
                    destination: destinationTokenAccount
                },
                owner: walletPublicKey,
            },
            amountIn,
            amountOut: null,
            fixedSide: 'in',
            config: {
                slippage
            }
        });

        // Create transaction
        const transaction = new Transaction();
        instructions.forEach(instruction => transaction.add(instruction));

        // Send and confirm transaction
        const signature = await sendAndConfirmTransaction(connection, transaction, [walletKeypair, ...signers], { skipPreflight: true });
        console.log("Transaction completed with signature:", signature);

        return { success: true, signature: signature };

    } catch (error) {
        console.error("Failed to perform swap:", error);
        return { success: false, error: error.message };
    }
}

// Function to ensure associated token account exists
async function ensureAssociatedTokenAccount(mint, owner, connection, walletKeypair) {
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
      await sendAndConfirmTransaction(connection, transaction, [walletKeypair], { skipPreflight: true });
  }
  return associatedTokenAddress;
}

const express = require('express');
const app = express();
const port = 3000;

app.use(express.json()); // to support JSON-encoded bodies

app.post('/swap', async (req, res) => {
    const { pool_address, input_token_mint, output_token_mint, amount_in, private_key, quicknode_rpc_url } = req.body;
    const result = await swap(pool_address, input_token_mint, output_token_mint, amount_in, private_key, quicknode_rpc_url);
    res.json(result);
});

app.listen(port, () => {
    console.log(`Swap executor listening at http://localhost:${port}`);
});