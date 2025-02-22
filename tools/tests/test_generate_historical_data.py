"""Tests for historical data generator"""

import pytest
from datetime import datetime, timedelta
import json
from pathlib import Path
from ..generate_historical_data import HistoricalDataGenerator

@pytest.fixture
def date_range():
    """Test date range"""
    return (
        datetime(2024, 1, 1),
        datetime(2024, 1, 2)
    )

@pytest.fixture
def generator(date_range):
    """Create test data generator"""
    start_date, end_date = date_range
    return HistoricalDataGenerator(
        start_date=start_date,
        end_date=end_date,
        num_pools=3,
        update_frequency_seconds=300,  # 5 minutes
        base_liquidity=1000000
    )

def test_pool_generation(generator):
    """Test pool generation"""
    generator._generate_pools()
    
    assert len(generator.pools) == 3
    for pool_id, pool_data in generator.pools.items():
        assert isinstance(pool_data["initial_liquidity"], float)
        assert 500000 <= pool_data["initial_liquidity"] <= 2000000
        assert 0.01 <= pool_data["price_impact"] <= 0.03
        assert pool_data["creator_address"].startswith("creator_")
        assert pool_data["token_mint"].startswith("token_")
        assert pool_data["current_price"] == 1.0

def test_event_generation(generator):
    """Test event generation"""
    generator._generate_pools()
    generator._generate_events()
    
    assert len(generator.events) > 0
    
    # Check pool creation events
    pool_creations = [e for e in generator.events if e["type"] == "pool_creation"]
    assert len(pool_creations) == 3
    
    # Check price updates
    price_updates = [e for e in generator.events if e["type"] == "price_update"]
    assert len(price_updates) > 0
    
    # Verify event structure
    for event in generator.events:
        assert "timestamp" in event
        assert "pool_id" in event
        if event["type"] == "pool_creation":
            assert "pool_data" in event
            assert "initial_liquidity" in event["pool_data"]
            assert "price_impact" in event["pool_data"]
        elif event["type"] == "price_update":
            assert "price" in event
            assert "volume" in event
            assert "liquidity_change" in event

def test_dataset_creation(generator):
    """Test complete dataset generation"""
    data = generator.generate_data()
    
    # Check structure
    assert "metadata" in data
    assert "events" in data
    assert "summary" in data
    assert "scenarios" in data
    assert "metrics" in data
    
    # Check metadata
    assert data["metadata"]["timeframe"].startswith("2024-01-01")
    assert data["metadata"]["source"] == "Data Generator"
    
    # Check summary
    assert data["summary"]["total_pools"] == 3
    assert data["summary"]["total_events"] > 3  # At least pool creations
    assert data["summary"]["price_updates"] > 0
    assert data["summary"]["pool_creations"] == 3
    
    # Check metrics
    assert 100 <= data["metrics"]["avg_latency_ms"] <= 200
    assert 0.9 <= data["metrics"]["success_rate"] <= 0.99
    assert 0.95 <= data["metrics"]["avg_price_impact_accuracy"] <= 0.99

def test_scenario_generation(generator):
    """Test trading scenario generation"""
    data = generator.generate_data()
    
    # Should have at least one type of scenario
    assert len(data["scenarios"]) > 0
    
    for scenario_type, scenario in data["scenarios"].items():
        assert scenario_type in ["successful_trade", "failed_trade", "neutral_trade"]
        assert "pool_id" in scenario
        assert "entry_price" in scenario
        assert "exit_price" in scenario
        assert "hold_duration" in scenario
        assert any(key in scenario for key in ["profit_percentage", "loss_percentage"])

def test_data_validity(generator):
    """Test validity of generated data"""
    data = generator.generate_data()
    
    # Check event ordering
    events = data["events"]
    timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
    assert timestamps == sorted(timestamps)
    
    # Check price continuity
    for pool_id in generator.pools:
        pool_events = [
            e for e in events 
            if e["pool_id"] == pool_id and e["type"] == "price_update"
        ]
        if pool_events:
            prices = [e["price"] for e in pool_events]
            # No extreme price changes
            for p1, p2 in zip(prices[:-1], prices[1:]):
                assert abs(p2/p1 - 1) <= 0.3  # Max 30% change

def test_file_output(generator, tmp_path):
    """Test file output"""
    output_file = tmp_path / "test_data.json"
    data = generator.generate_data()
    
    with open(output_file, 'w') as f:
        json.dump(data, f)
    
    # Verify file was created and contains valid JSON
    assert output_file.exists()
    with open(output_file) as f:
        loaded_data = json.load(f)
    assert loaded_data == data

def test_custom_parameters():
    """Test generator with custom parameters"""
    generator = HistoricalDataGenerator(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
        num_pools=5,
        update_frequency_seconds=60,
        base_liquidity=2000000
    )
    
    data = generator.generate_data()
    
    assert len(generator.pools) == 5
    assert data["summary"]["total_pools"] == 5
    assert all(
        p["initial_liquidity"] >= 1000000  # At least half base liquidity
        for p in (e["pool_data"] for e in data["events"] if e["type"] == "pool_creation")
    )

def test_error_handling():
    """Test error handling"""
    # Invalid date range
    with pytest.raises(ValueError):
        HistoricalDataGenerator(
            start_date=datetime(2024, 1, 2),
            end_date=datetime(2024, 1, 1)
        )
    
    # Invalid pool count
    with pytest.raises(ValueError):
        HistoricalDataGenerator(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 2),
            num_pools=0
        )
    
    # Invalid update frequency
    with pytest.raises(ValueError):
        HistoricalDataGenerator(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 2),
            update_frequency_seconds=0
        )
