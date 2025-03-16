# Volume Analysis

The volume analysis system provides real-time monitoring and risk assessment of token trading volumes. It integrates with the token safety analyzer to provide comprehensive risk assessment.

## Features

- Real-time volume monitoring
- Volume spike detection
- Buy/sell pattern analysis
- Large transaction tracking
- Historical volume comparison
- Risk scoring based on volume patterns

## Components

### VolumeAnalyzer

The VolumeAnalyzer class (`volume_analyzer.py`) provides the core volume analysis functionality:

```python
analyzer = VolumeAnalyzer(
    client,
    cache_duration=3600,      # 1 hour cache
    volume_window=24,         # 24 hour analysis window
    large_tx_threshold=10000, # USDC value
    spike_threshold=200.0,    # 200% increase
    max_concurrent=5          # Rate limiting
)
```

#### Key Methods

- `analyze_volume(token_mint, pool_address)`: Main analysis method
- `_detect_volume_spikes(volume_history)`: Detects unusual volume patterns
- `_analyze_transaction_patterns(token_mint)`: Analyzes buy vs sell ratios
- `_calculate_risk_score(...)`: Computes volume-based risk score

### Integration with TokenSafetyAnalyzer

The volume analysis is integrated into the token safety system (`token_safety_analyzer.py`):

```python
safety_weights = {
    "honeypot": 0.35,
    "rugpull": 0.30,
    "sentiment": 0.20,
    "volume": 0.15    # Volume component weight
}
```

## Risk Scoring

Volume-based risk factors include:

1. Volume Change Risk
   - >500%: High risk (0.4)
   - >200%: Medium risk (0.3)
   - >100%: Low risk (0.2)

2. Volume Spike Risk
   - Each spike adds 0.2 (max 0.4)

3. Buy/Sell Ratio Risk
   - Imbalanced ratios (<0.5 or >2.0): 0.1

4. Large Transaction Risk
   - Proportional to ratio of large transactions

## Usage Example

```python
# Initialize analyzers
client = AsyncClient(endpoint)
volume_analyzer = VolumeAnalyzer(client)
safety_analyzer = TokenSafetyAnalyzer(client)

# Analyze token
result = await safety_analyzer.analyze_token(
    token_mint="token123",
    pool_address="pool456",
    creator_address="creator789"
)

# Check volume metrics
volume_metrics = result["volume_metrics"]
volume_score = result["component_scores"]["volume"]

if volume_score > 0.7:
    print("High volume-based risk detected")
    print(f"Risk factors: {result['risk_factors']}")
```

## Caching

Both analyzers implement caching to reduce RPC calls:

- Results are cached for 1 hour by default
- Volume history is maintained for 48 hours
- Cache can be cleared manually using `clear_cache()`

## Rate Limiting

To prevent excessive RPC usage:

- Maximum 5 concurrent analyses
- Minimum 5 seconds between analyses of the same token
- Cached results returned for rate-limited requests

## Error Handling

The system handles various error cases:

- API errors return maximum risk score (1.0)
- Missing data falls back to conservative estimates
- Rate limiting errors return cached data when available

## Testing

Comprehensive tests are provided in:
- `tests/test_volume_analyzer.py`
- `tests/test_token_safety_analyzer.py`

Run tests with:
```bash
pytest tests/test_volume_analyzer.py -v
pytest tests/test_token_safety_analyzer.py -v
```

## Future Improvements

Planned enhancements:

1. Machine learning-based pattern detection
2. Cross-pool volume correlation
3. Whale wallet tracking
4. Volume-based price impact estimation
5. Real-time volume alerts
6. Custom volume thresholds per token

## Configuration

The volume analysis system can be configured through environment variables:

```env
VOLUME_CACHE_DURATION=3600
VOLUME_WINDOW_HOURS=24
LARGE_TX_THRESHOLD=10000
VOLUME_SPIKE_THRESHOLD=200
MAX_CONCURRENT_ANALYSES=5
```

Or through the constructor:

```python
analyzer = VolumeAnalyzer(
    client,
    cache_duration=int(os.getenv("VOLUME_CACHE_DURATION", 3600)),
    volume_window=int(os.getenv("VOLUME_WINDOW_HOURS", 24)),
    large_tx_threshold=float(os.getenv("LARGE_TX_THRESHOLD", 10000)),
    spike_threshold=float(os.getenv("VOLUME_SPIKE_THRESHOLD", 200.0)),
    max_concurrent=int(os.getenv("MAX_CONCURRENT_ANALYSES", 5))
)
