import numpy as np
from tensorflow.keras.models import load_model
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummyLSTM:
    """Dummy LSTM model for development"""
    def predict(self, x):
        # Return random prediction ±5% of last price
        last_price = x[0][-1][0]
        return np.array([[last_price * (0.95 + 0.1 * np.random.rand())]])

def predict(prices: list, horizon: int) -> Tuple[float, float]:
    """Make dummy prediction"""
    try:
        # Load dummy model
        model = DummyLSTM()
        
        # Create dummy input
        seq_length = 24
        last_prices = np.array(prices[-seq_length:]).reshape(1, seq_length, 1)
        
        # Make prediction
        predicted_price = model.predict(last_prices)[0][0]
        
        # Generate plausible confidence
        confidence = 80 - horizon//24  # Decreases with longer horizon
        
        return float(predicted_price), float(confidence)
        
    except Exception as e:
        logger.error(f"Dummy prediction failed: {str(e)}")
        return float(prices[-1] * 1.05), 50.0  # Fallback values