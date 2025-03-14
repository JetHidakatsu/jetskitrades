# utils

## Classes

### RateLimiter

Rate limiter implementation

### MetricsCollector

Collect and store performance metrics

#### Methods

##### `add_trade_metric`

Add trade performance metric

Parameters:
- self
- trade_data: rom typing imp

Returns: Any

##### `add_latency_metric`

Add latency metric

Parameters:
- self
- operation: om 
- latency: rt An

Returns: Any

##### `add_error_metric`

Add error metric

Parameters:
- self
- error_type: rom
- error_msg: t A

Returns: Any

##### `get_metrics_summary`

Get summary of collected metrics

Parameters:
- self

Returns: Any

## Functions

### `setup_logger`

Configure logger with standard format

Parameters:
- name: ing
- level: syn

Returns: Any

### `retry_with_backoff`

Retry decorator with exponential backoff

Parameters:
- retries: mpo
- backoff_in_seconds: ng
im
- max_backoff: t log

Returns: Any

### `measure_latency`

Decorator to measure function execution time

Parameters:
- func: 
import asyncio


Returns: Any

### `safe_divide`

Safely divide two numbers

Parameters:
- a: loggi
- b: port 
- default: m typ

Returns: Any

### `normalize_price_data`

Normalize price data to range [0,1]

Parameters:
- prices:  asyncio
f

Returns: Any

### `calculate_volatility`

Calculate price volatility

Parameters:
- prices:  asyncio
f
- window:  im

Returns: Any

### `format_pubkey`

Format Solana public key for display

Parameters:
- pubkey: 
impor

Returns: Any

### `load_json_file`

Safely load JSON file

Parameters:
- filepath: port

Returns: Any

### `save_json_file`

Safely save JSON file

Parameters:
- data: g
import async
- filepath: ng i

Returns: Any

### `get_utc_timestamp`

Get current UTC timestamp in milliseconds

Returns: Any

### `format_amount`

Format token amount with proper decimal places

Parameters:
- amount: 
impo
- decimals: rom

Returns: Any

### `lamports_to_sol`

Convert lamports to SOL

Parameters:
- lamports: ort

Returns: Any

### `sol_to_lamports`

Convert SOL to lamports

Parameters:
- sol: g
imp

Returns: Any

### `calculate_price_impact`

Calculate price impact of a trade

Parameters:
- input_amount:  logg
- input_reserve: loggi
- output_reserve: oggin

Returns: Any

### `validate_slippage`

Validate if trade slippage is within limits

Parameters:
- expected_price: oggin
- execution_price: gging
- max_slippage:  logg

Returns: Any

