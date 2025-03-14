# position_manager

## Classes

### Position

Represents a trading position

#### Methods

##### `update`

Update position metrics

Parameters:
- self
- current_price: ct, O

Returns: Any

##### `should_exit`

Check if position should be closed

Parameters:
- self
- current_price: ption

Returns: Any

##### `close`

Close the position

Parameters:
- self
- exit_price: t Dic

Returns: Any

### PositionManager

Manages trading positions and risk

#### Methods

##### `get_position_size`

Calculate position size based on risk parameters

Parameters:
- self
- balance: ption
- risk_pct: m dec
- pool_score: cimal

Returns: Any

##### `get_metrics`

Get performance metrics

Parameters:
- self

Returns: Any

