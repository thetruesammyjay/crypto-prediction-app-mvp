import pytest
import numpy as np
from models.lstm_model import predict as lstm_predict
from models.random_forest_model import predict as rf_predict
from models.hybrid import predict as hybrid_predict
from typing import Tuple

@pytest.fixture
def sample_data() -> dict:
    """Fixture providing sample price data"""
    return {
        'prices': [30000.0, 30100.0, 30250.0, 30300.0, 30450.0],
        'returns': [0.0033, 0.0050, 0.0017, 0.0049],
        'volatility': [0.0025, 0.0030, 0.0028]
    }

@pytest.mark.parametrize("horizon", [24, 168])
def test_lstm_predict_returns_valid_values(sample_data: dict, horizon: int):
    """Test LSTM dummy returns plausible predictions"""
    prices = sample_data['prices']
    prediction, confidence = lstm_predict(prices, horizon)
    
    assert isinstance(prediction, float)
    assert isinstance(confidence, float)
    assert 0.9 * prices[-1] < prediction < 1.1 * prices[-1]  # ±10% of last price
    assert 50 <= confidence <= 100  # Confidence in reasonable range

@pytest.mark.parametrize("horizon", [24, 168])
def test_rf_predict_returns_valid_values(sample_data: dict, horizon: int):
    """Test Random Forest dummy returns plausible predictions"""
    prediction, confidence = rf_predict(sample_data, horizon)
    
    assert isinstance(prediction, float)
    assert isinstance(confidence, float)
    assert 0.9 * sample_data['prices'][-1] < prediction < 1.1 * sample_data['prices'][-1]
    assert 50 <= confidence <= 100

@pytest.mark.parametrize("horizon", [24, 168])
def test_hybrid_predict_returns_valid_values(sample_data: dict, horizon: int):
    """Test Hybrid model returns weighted average of predictions"""
    lstm_pred, _ = lstm_predict(sample_data['prices'], horizon)
    rf_pred, _ = rf_predict(sample_data, horizon)
    hybrid_pred, hybrid_conf = hybrid_predict(sample_data, horizon)
    
    # Should be between LSTM and RF predictions
    assert min(lstm_pred, rf_pred) <= hybrid_pred <= max(lstm_pred, rf_pred)
    assert 60 <= hybrid_conf <= 95

def test_lstm_confidence_decreases_with_horizon(sample_data: dict):
    """Test longer horizons have lower confidence"""
    _, conf_24h = lstm_predict(sample_data['prices'], 24)
    _, conf_168h = lstm_predict(sample_data['prices'], 168)
    assert conf_168h < conf_24h

def test_rf_uses_proper_features(sample_data: dict):
    """Test RF uses expected features"""
    with pytest.raises(KeyError):
        # Should fail if required keys are missing
        rf_predict({'prices': [1,2,3]}, 24)

def test_models_handle_short_data():
    """Test models handle insufficient data gracefully"""
    short_data = {'prices': [30000, 30100], 'returns': [], 'volatility': []}
    pred, conf = rf_predict(short_data, 24)
    assert isinstance(pred, float)
    assert isinstance(conf, float)

@pytest.mark.parametrize("model_func", [lstm_predict, rf_predict, hybrid_predict])
def test_models_return_tuples(model_func, sample_data: dict):
    """Test all models return (float, float) tuples"""
    if model_func == lstm_predict:
        result = model_func(sample_data['prices'], 24)
    else:
        result = model_func(sample_data, 24)
    
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(x, float) for x in result)

def test_model_output_distribution(sample_data: dict):
    """Test predictions show reasonable variance"""
    predictions = [lstm_predict(sample_data['prices'], 24)[0] for _ in range(100)]
    mean_pred = np.mean(predictions)
    std_dev = np.std(predictions)
    
    # Check predictions stay within 2 standard deviations
    assert 0.95 * mean_pred < sample_data['prices'][-1] < 1.05 * mean_pred
    assert 0.005 < std_dev/sample_data['prices'][-1] < 0.05  # 0.5%-5% std dev