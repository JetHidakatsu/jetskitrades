# performance_dashboard

Performance Metrics Dashboard.

This module provides a dashboard for monitoring and analyzing trading bot performance metrics.

## Classes

### PerformanceDashboard

Dashboard for tracking and analyzing trading performance metrics.

#### Methods

##### `record_trade`

Record a completed trade.

Args:
    trade_data: Dictionary containing trade details including:
        - timestamp
        - token_pair
        - entry_price
        - exit_price
        - volume
        - profit_loss
        - execution_time

Parameters:
- self
- trade_data:  mod

Returns: Any

##### `record_latency`

Record operation latency.

Args:
    operation: Name of the operation being measured
    duration_ms: Duration in milliseconds

Parameters:
- self
- operation: mod
- duration_ms: dashb

Returns: Any

##### `record_system_health`

Record system health metrics.

Args:
    metrics: Dictionary containing health metrics including:
        - cpu_usage
        - memory_usage
        - network_latency
        - error_count

Parameters:
- self
- metrics: le p

Returns: Any

##### `get_summary`

Get performance summary for the specified timeframe.

Args:
    timeframe: Time period to analyze. If None, analyzes all data.

Returns:
    Dictionary containing performance metrics summary

Parameters:
- self
- timeframe: is module provides 

Returns: Any

##### `export_metrics`

Export metrics to a JSON file.

Args:
    filepath: Path to save the metrics file

Parameters:
- self
- filepath:  mo

Returns: Any

