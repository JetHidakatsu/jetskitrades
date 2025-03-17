"""Tests for historical data collection and processing"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
from unittest.mock import AsyncMock, MagicMock, patch
from solders.pubkey import Pubkey
from ..data_collector import DataCollector, DataCollectionConfig

@pytest.fixture
def collection_config():
    """Create test configuration"""
    return DataCollectionConfig(
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        rpc_url="http://test.rpc.url",
        program_id="675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        save_dir=Path("test_data"),
        batch_size=10,
        request_delay=0.01
    )

@pytest.fixture
def mock_client():
    """Create mock Solana client"""
    client = AsyncMock()
    
    # Mock get_signatures_for_address
    client.get_signatures_for_address = AsyncMock(return_value={
        "result": [
            {
                "signature": f"sig_{i}",
                "blockTime": int((datetime.now() - timedelta(hours=i)).timestamp())
            }
            for i in range(5)
        ]
    })
    
    # Mock get_transaction
    client.get_transaction = AsyncMock(return_value={
        "result": {
            "meta": {
                "logMessages": ["Program invoke", "initialize2"],
                "postTokenBalances": [{"owner": "test_creator"}]
            },
            "transaction": {
                "message": {
                    "accountKeys": [
                        {"programId": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
                         "pubkey": "test_pool"}
                    ]
                },
                "signatures": ["test_sig"]
            },
            "blockTime": int(datetime.now().timestamp())
        }
    })
    
    # Mock get_account_info
    client.get_account_info = AsyncMock(return_value={
        "result": {
            "value": {
                "data": [
                    "BASE58DATA",
                    "base64"
                ]
            }
        }
    })
    
    return client

@pytest.fixture
def data_collector(collection_config, mock_client):
    """Create data collector instance with mock client"""
    collector = DataCollector(collection_config)
    collector.client = mock_client
    return collector

@pytest.mark.asyncio
async def test_collect_pool_data(data_collector, tmp_path):
    """Test pool data collection"""
    # Temporarily set save directory
    data_collector.config.save_dir = tmp_path
    
    # Collect pool data
    await data_collector._collect_pool_data()
    
    # Verify data was saved
    assert (tmp_path / 'pool_data.json').exists()
    
    # Check saved data
    with open(tmp_path / 'pool_data.json') as f:
        data = json.load(f)
        assert len(data) > 0
        assert all(isinstance(pool, dict) for pool in data)
        assert all('address' in pool for pool in data)

@pytest.mark.asyncio
async def test_collect_price_data(data_collector, tmp_path):
    """Test price data collection"""
    data_collector.config.save_dir = tmp_path
    
    # Create mock pool data
    mock_pools = [{'address': 'test_pool_1'}, {'address': 'test_pool_2'}]
    pool_data_path = tmp_path / 'pool_data.json'
    with open(pool_data_path, 'w') as f:
        json.dump(mock_pools, f)
    
    # Collect price data
    await data_collector._collect_price_data()
    
    # Verify data was saved
    assert (tmp_path / 'price_data.json').exists()
    
    with open(tmp_path / 'price_data.json') as f:
        data = json.load(f)
        assert len(data) > 0
        assert all('price' in price for price in data)

@pytest.mark.asyncio
async def test_collect_market_events(data_collector, tmp_path):
    """Test market event collection"""
    data_collector.config.save_dir = tmp_path
    
    # Mock transaction data with market events
    data_collector.client.get_transaction = AsyncMock(return_value={
        "result": {
            "meta": {"logMessages": ["swap"]},
            "transaction": {"signatures": ["test_sig"]},
            "blockTime": int(datetime.now().timestamp())
        }
    })
    
    # Collect market events
    await data_collector._collect_market_events()
    
    # Verify data was saved
    assert (tmp_path / 'market_events.json').exists()
    
    with open(tmp_path / 'market_events.json') as f:
        data = json.load(f)
        assert len(data) > 0
        assert all('type' in event for event in data)

def test_is_pool_creation(data_collector):
    """Test pool creation detection"""
    # Test positive case
    tx_data = {
        "meta": {
            "logMessages": ["Program invoke", "initialize2"]
        }
    }
    assert data_collector._is_pool_creation(tx_data) is True
    
    # Test negative case
    tx_data = {
        "meta": {
            "logMessages": ["Program invoke", "swap"]
        }
    }
    assert data_collector._is_pool_creation(tx_data) is False

@pytest.mark.asyncio
async def test_extract_pool_data(data_collector):
    """Test pool data extraction"""
    tx_data = {
        "meta": {
            "postTokenBalances": [{"owner": "test_creator"}]
        },
        "transaction": {
            "message": {
                "accountKeys": [
                    {"programId": data_collector.config.program_id,
                     "pubkey": "test_pool"}
                ]
            },
            "signatures": ["test_sig"]
        },
        "blockTime": int(datetime.now().timestamp())
    }
    
    pool_data = await data_collector._extract_pool_data(tx_data)
    
    assert pool_data is not None
    assert pool_data['address'] == "test_pool"
    assert pool_data['creator_address'] == "test_creator"
    assert pool_data['type'] == "pool_creation"

def test_extract_price_data(data_collector):
    """Test price data extraction"""
    # Mock base58 encoded data
    mock_data = [
        bytes([0] * 8 + [100, 0, 0, 0, 0, 0, 0, 0] + [0] * 16)
    ]
    
    with patch('base58.b58decode', return_value=mock_data[0]):
        price_data = data_collector._extract_price_data([["encoded_data", "base64"]])
        
        assert len(price_data) > 0
        assert all('price' in data for data in price_data)
        assert all('type' in data for data in price_data)

@pytest.mark.asyncio
async def test_process_collected_data(data_collector, tmp_path):
    """Test data processing and combination"""
    data_collector.config.save_dir = tmp_path
    
    # Create sample data files
    sample_data = {
        'pool_data.json': [{'type': 'pool_creation', 'timestamp': '2023-01-01T00:00:00'}],
        'price_data.json': [{'type': 'price_update', 'timestamp': '2023-01-01T00:01:00'}],
        'market_events.json': [{'type': 'market_swap', 'timestamp': '2023-01-01T00:02:00'}]
    }
    
    for filename, data in sample_data.items():
        with open(tmp_path / filename, 'w') as f:
            json.dump(data, f)
    
    # Process data
    await data_collector._process_collected_data()
    
    # Verify combined data
    assert (tmp_path / 'historical_data.json').exists()
    assert (tmp_path / 'data_summary.json').exists()
    
    with open(tmp_path / 'historical_data.json') as f:
        combined_data = json.load(f)
        assert len(combined_data) == 3
        assert sorted(combined_data, key=lambda x: x['timestamp']) == combined_data

@pytest.mark.asyncio
async def test_error_handling(data_collector, caplog):
    """Test error handling during data collection"""
    # Simulate RPC error
    data_collector.client.get_signatures_for_address = AsyncMock(
        side_effect=Exception("RPC Error")
    )
    
    signatures = await data_collector._get_program_signatures()
    assert len(signatures) == 0
    assert "Error getting program signatures" in caplog.text

def test_data_saving_and_loading(data_collector, tmp_path):
    """Test data saving and loading functionality"""
    data_collector.config.save_dir = tmp_path
    
    # Test saving
    test_data = [{'test': 'data'}]
    data_collector._save_data(test_data, 'test.json')
    assert (tmp_path / 'test.json').exists()
    
    # Test loading
    loaded_data = data_collector._load_data('test.json')
    assert loaded_data == test_data
    
    # Test loading non-existent file
    assert data_collector._load_data('nonexistent.json') == []

@pytest.mark.asyncio
async def test_concurrent_data_collection(data_collector, tmp_path):
    """Test concurrent data collection"""
    data_collector.config.save_dir = tmp_path
    
    # Run all collection tasks concurrently
    tasks = [
        data_collector._collect_pool_data(),
        data_collector._collect_price_data(),
        data_collector._collect_market_events()
    ]
    
    await asyncio.gather(*tasks)
    
    # Verify all data files were created
    assert (tmp_path / 'pool_data.json').exists()
    assert (tmp_path / 'price_data.json').exists()
    assert (tmp_path / 'market_events.json').exists()
