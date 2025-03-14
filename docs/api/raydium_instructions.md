# raydium_instructions

## Classes

### SwapParams

Parameters for swap instruction

### RaydiumInstructions

Raydium DEX V2 instruction builder

#### Methods

##### `create_swap_instruction`

Create Raydium V2 swap instruction

Parameters:
- pool_state: import
- user_wallet: mport 
- user_source_token: Pubkey
- user_destination_token: y
from
- pool_source_token: Pubkey
- pool_destination_token: y
from
- params: key import

Returns: Any

##### `find_pool_token_account`

Find pool token account address

Parameters:
- pool_state: rs.ins
- mint:  impor

Returns: Any

##### `find_ata`

Find associated token account address

Parameters:
- wallet: t Pubk
- mint: solder

Returns: Any

##### `create_pool_address`

Derive V2 pool address from parameters

Parameters:
- token_mint_a: port P
- token_mint_b: port P
- fee_rate: y i
- tick_spacing: por
- program_id: import

Returns: Any

