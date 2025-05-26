import pytest
from unittest.mock import patch
from utils.data_fetcher import get_crypto_data
from typing import List

@pytest.mark.parametrize("crypto_id,expected_length", [
    ("bitcoin", 720),  # 30 days * 24 hours
    ("ethereum", 720),
    ("binancecoin", 720),
    ("solana", 720),
    ("unknown_coin", 720)  # Test default case
])
def test_get_crypto_data_returns_correct_length(crypto_id: str, expected_length: int):
    """Test that generated data has correct length"""
    result = get_crypto_data(crypto_id)
    assert isinstance(result, list)
    assert len(result) == expected_length

def test_get_crypto_data_returns_floats():
    """Test all returned values are floats"""
    result = get_crypto_data("bitcoin")
    assert all(isinstance(x, float) for x in result)

@pytest.mark.parametrize("crypto_id,expected_range", [
    ("bitcoin", (27000, 33000)),    # ~10% around $30k base
    ("ethereum", (1800, 2200)),     # ~10% around $2k base
    ("binancecoin", (270, 330)),    # ~10% around $300 base
    ("solana", (45, 55))            # ~10% around $50 base
])
def test_get_crypto_data_returns_plausible_values(crypto_id: str, expected_range: tuple):
    """Test values fall within expected ranges"""
    result = get_crypto_data(crypto_id)
    assert all(expected_range[0] <= x <= expected_range[1] for x in result[:24])  # Check first day

def test_get_crypto_data_generates_realistic_volatility():
    """Test data shows realistic price movements"""
    result = get_crypto_data("bitcoin")
    changes = [abs(result[i] - result[i-1])/result[i-1] for i in range(1, 24)]
    assert all(0 <= x <= 0.1 for x in changes)  # No single-hour moves >10%
    assert 0.001 < sum(changes)/len(changes) < 0.05  # Avg hourly change between 0.1%-5%

def test_get_crypto_data_has_upward_bias():
    """Test generated data has slight upward trend"""
    result = get_crypto_data("bitcoin")
    first_day_avg = sum(result[:24])/24
    last_day_avg = sum(result[-24:])/24
    assert 1.0 < last_day_avg/first_day_avg < 1.2  # 0-20% increase over 30 days

@patch('utils.data_fetcher.logger')
def test_get_crypto_data_logs_correctly(mock_logger):
    """Test proper logging occurs"""
    get_crypto_data("bitcoin")
    assert mock_logger.info.called
    assert "Generating dummy data" in mock_logger.info.call_args[0][0]

def test_get_crypto_data_fallback_behavior():
    """Test fallback when exception occurs"""
    with patch('utils.data_fetcher.random.random', side_effect=Exception("Test error")):
        result = get_crypto_data("bitcoin")
        assert len(result) == 720  # Falls back to linear data
        assert all(100 <= x <= 100 + 720 for x in result)  # Linear increase