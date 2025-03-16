# Transaction Recovery System

The transaction recovery system provides robust error handling and automatic recovery for failed transactions. It implements various strategies to handle different types of failures and ensures maximum transaction reliability.

## Features

- Automatic transaction monitoring and status tracking
- Multiple recovery strategies for different failure types
- Exponential backoff retry mechanism
- Transaction validation before retry attempts
- Comprehensive error analysis and categorization
- Real-time notifications of recovery attempts
- Recovery statistics and performance metrics

## Configuration

The recovery system can be configured through the following settings in your config file:

```json
{
  "recovery": {
    "max_retries": 3,
    "retry_delay_base": 5,
    "retry_delay_max": 60,
    "transaction_timeout": 90
  }
}
```

### Settings Explained

- `max_retries`: Maximum number of retry attempts for a failed transaction
- `retry_delay_base`: Base delay (in seconds) between retry attempts
- `retry_delay_max`: Maximum delay (in seconds) between retry attempts
- `transaction_timeout`: Time (in seconds) after which a pending transaction is considered expired

## Failure Types

The system recognizes and handles the following types of failures:

1. **Insufficient Funds**
   - Occurs when wallet balance is too low
   - Recovery: Adjusts transaction amount or waits for funds

2. **Slippage Error**
   - Price moved beyond slippage tolerance
   - Recovery: Adjusts slippage parameters and retries

3. **Invalid Blockhash**
   - Transaction blockhash expired
   - Recovery: Refreshes blockhash and rebuilds transaction

4. **Network Error**
   - RPC node or network connectivity issues
   - Recovery: Retries with exponential backoff

5. **Simulation Error**
   - Transaction fails simulation
   - Recovery: Validates and rebuilds transaction

## Recovery Strategies

### 1. Adjust Amount
```python
# Example of amount adjustment
new_amount = original_amount * 0.95  # Reduce by 5%
new_tx = rebuild_transaction(new_amount)
```

### 2. Adjust Slippage
```python
# Example of slippage adjustment
new_slippage = original_slippage * 1.5  # Increase by 50%
new_tx = rebuild_transaction_with_slippage(new_slippage)
```

### 3. Refresh Blockhash
```python
# Example of blockhash refresh
new_blockhash = await get_latest_blockhash()
new_tx = rebuild_transaction_with_blockhash(new_blockhash)
```

### 4. Retry with Backoff
```python
# Example of exponential backoff
delay = min(base_delay * (2 ** retry_count), max_delay)
await asyncio.sleep(delay)
```

## Usage Example

```python
from transaction_recovery_manager import TransactionRecoveryManager

# Initialize the manager
recovery_manager = TransactionRecoveryManager(
    config,
    db_manager,
    event_manager,
    rpc_manager,
    helius_provider,
    notification_manager
)

# Register a transaction for monitoring
tx_id = "your_transaction_id"
transaction = {
    "instructions": [...],
    "signers": [...],
    # ... other transaction data
}
metadata = {
    "type": "swap",
    "token": "SOL/USDC",
    "amount": "100"
}

state = await recovery_manager.register_transaction(
    tx_id,
    transaction,
    metadata
)

# Transaction will be automatically monitored and recovered if needed
```

## Event Handling

The system emits various events that you can listen to:

```python
# Example of event handling
@event_manager.on("transaction_success")
async def handle_success(data):
    tx_id = data["tx_id"]
    print(f"Transaction {tx_id} confirmed successfully")

@event_manager.on("transaction_failure")
async def handle_failure(data):
    tx_id = data["tx_id"]
    reason = data["failure_reason"]
    print(f"Transaction {tx_id} failed: {reason}")
```

## Recovery Statistics

You can monitor recovery performance through statistics:

```python
stats = await recovery_manager.get_recovery_stats()
print(f"Total monitored: {stats['total_monitored']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average recovery time: {stats['avg_recovery_time']}s")
```

## Best Practices

1. **Configure Timeouts Appropriately**
   - Set transaction_timeout based on network conditions
   - Consider block time and confirmation requirements

2. **Monitor Recovery Stats**
   - Track success rates and failure patterns
   - Adjust strategies based on performance data

3. **Handle Notifications**
   - Set up alerts for critical failures
   - Monitor recovery attempts in real-time

4. **Manage Resources**
   - Clean up expired recovery states
   - Monitor memory usage for long-running operations

5. **Validate Transactions**
   - Always simulate before submitting
   - Check gas estimates and account states

## Error Handling

The system provides detailed error information:

```python
try:
    await recovery_manager.attempt_recovery(tx_id)
except Exception as e:
    logger.error(f"Recovery failed: {str(e)}")
    # Handle the error appropriately
```

## Integration with Other Components

The recovery system integrates with:

- Database Manager: Persists recovery states
- Event Manager: Broadcasts recovery events
- RPC Manager: Handles transaction submission
- Notification Manager: Sends alerts and updates
- Helius Provider: Gets transaction status

## Monitoring and Maintenance

Regular monitoring tasks:

1. Check recovery success rates
2. Monitor retry patterns
3. Analyze failure reasons
4. Review resource usage
5. Update recovery strategies

## Troubleshooting

Common issues and solutions:

1. **High Failure Rates**
   - Check network conditions
   - Verify account balances
   - Review slippage settings

2. **Slow Recovery Times**
   - Adjust retry delays
   - Check RPC node performance
   - Monitor network latency

3. **Resource Usage**
   - Clean up old recovery states
   - Monitor memory consumption
   - Optimize database queries

4. **Missing Notifications**
   - Verify notification settings
   - Check notification service status
   - Review error logs

## Future Improvements

Planned enhancements:

1. Machine learning-based recovery strategies
2. Advanced failure prediction
3. Dynamic strategy adjustment
4. Performance optimization
5. Enhanced monitoring tools

## Contributing

When adding new features:

1. Add appropriate tests
2. Update documentation
3. Follow error handling patterns
4. Consider backward compatibility
5. Review performance impact
