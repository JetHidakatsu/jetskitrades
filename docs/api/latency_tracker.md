# latency_tracker

Latency tracking and performance metrics for swap execution

## Classes

### SwapMetrics

Metrics for a single swap operation

### LatencyTracker

Track and analyze swap execution latency

#### Methods

##### `start_event`

Start tracking a new event

Parameters:
- self
- event_id: met

Returns: Any

##### `start_swap`

Start tracking a new swap operation

Parameters:
- self
- pool_id: e m

Returns: Any

##### `end_event`

End tracking for an event

Parameters:
- self
- event_id: e m
- success: swap
- error: mport time
fr

Returns: Any

##### `end_swap`

End tracking for a swap operation

Parameters:
- self
- swap_id: nce
- success: r sw
- error: 
import time


Returns: Any

##### `get_recent_latencies`

Get recent latencies of active swaps.

Parameters:
- self

Returns: Any

##### `get_metrics`

Get current performance metrics

Parameters:
- self

Returns: Any

##### `reset_metrics`

Reset all metrics

Parameters:
- self

Returns: Any

