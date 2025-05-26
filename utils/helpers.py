import numpy as np
from sklearn.metrics import mean_absolute_error
from typing import Tuple, List

def calculate_confidence(y_true: List[float], y_pred: List[float], baseline_error: float) -> float:
    """
    Calculate prediction confidence score based on error relative to baseline
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        baseline_error: Baseline MAE to compare against
        
    Returns:
        Confidence score between 0-100%
    """
    mae = mean_absolute_error(y_true, y_pred)
    
    # Normalize error relative to baseline
    error_ratio = mae / baseline_error
    
    # Convert to confidence (0-100%)
    confidence = max(0, min(100, 100 * (1 - error_ratio)))
    
    return round(confidence, 2)

def prepare_prediction_data(prices: List[float], prediction_horizons: List[int]) -> Tuple[List[float], dict]:
    """
    Prepare data for prediction and calculate baseline metrics
    
    Args:
        prices: List of historical prices
        prediction_horizons: List of prediction horizons in hours (e.g., [24, 168])
        
    Returns:
        Tuple of (processed_data, baseline_metrics)
    """
    # Calculate baseline metrics
    baseline_metrics = {
        '24h': {
            'mae': calculate_baseline_mae(prices, horizon=24)
        },
        '168h': {
            'mae': calculate_baseline_mae(prices, horizon=168)
        }
    }
    
    # Prepare data for model input
    processed_data = {
        'prices': prices,
        'returns': calculate_returns(prices),
        'volatility': calculate_volatility(prices, window=24)
    }
    
    return processed_data, baseline_metrics

def calculate_baseline_mae(prices: List[float], horizon: int) -> float:
    """
    Calculate baseline MAE using naive prediction (last observed value)
    
    Args:
        prices: List of historical prices
        horizon: Prediction horizon in hours
        
    Returns:
        Baseline MAE
    """
    if len(prices) <= horizon:
        return np.mean(prices) * 0.05  # Default 5% if not enough data
    
    errors = []
    for i in range(horizon, len(prices)):
        naive_pred = prices[i - horizon]
        actual = prices[i]
        errors.append(abs(naive_pred - actual))
    
    return np.mean(errors)

def calculate_returns(prices: List[float]) -> List[float]:
    """Calculate hourly returns from price data"""
    returns = []
    for i in range(1, len(prices)):
        returns.append((prices[i] - prices[i-1]) / prices[i-1])
    return returns

def calculate_volatility(prices: List[float], window: int = 24) -> List[float]:
    """Calculate rolling volatility"""
    returns = calculate_returns(prices)
    volatility = []
    for i in range(window, len(returns)):
        window_returns = returns[i-window:i]
        volatility.append(np.std(window_returns))
    return volatility

def handle_api_error(error: Exception) -> dict:
    """Standardize API error responses"""
    error_messages = {
        'ConnectionError': 'Failed to connect to data source',
        'Timeout': 'Request timed out',
        'RateLimit': 'API rate limit exceeded',
        'InvalidData': 'Received invalid data format'
    }
    
    error_type = type(error).__name__
    message = error_messages.get(error_type, 'An unknown error occurred')
    
    return {
        'error': True,
        'type': error_type,
        'message': message,
        'details': str(error)
    }