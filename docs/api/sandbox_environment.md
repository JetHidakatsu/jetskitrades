# sandbox_environment

Sandbox environment for testing trading strategies

## Classes

### SandboxConfig

Configuration for sandbox environment

### SandboxMetrics

Metrics for sandbox performance tracking

### EnhancedJSONEncoder

Custom JSON encoder to handle TradeMetrics

#### Methods

##### `default`

Parameters:
- self
- obj

Returns: Any

### SandboxEnvironment

Sandbox for testing trading strategies

#### Methods

##### `get_metrics`

Get current sandbox metrics

Parameters:
- self

Returns: Any

##### `save_transaction_history`

Save transaction history to file

Parameters:
- self
- filename: gie

Returns: Any

##### `reset`

Reset sandbox state

Parameters:
- self

Returns: Any

