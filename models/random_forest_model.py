import numpy as np
from typing import Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummyRF:
    """Dummy Random Forest model for development"""
    def predict(self, x):
        # Return random prediction ±3% of last price
        return np.array([x[0][0] * (0.97 + 0.06 * np.random.rand())])

def predict(data: Dict, horizon: int) -> Tuple[float, float]:
    """Make dummy prediction"""
    try:
        model = DummyRF()
        
        # Create dummy features
        features = [
            data['prices'][-1],  # current price
            np.mean(data['prices'][-24:]),  # 24h avg
            horizon  # prediction horizon
        ]
        
        # Make prediction
        predicted_price = model.predict([features])[0]
        
        # Generate plausible confidence
        confidence = 85 - horizon//24  # Decreases with longer horizon
        
        return float(predicted_price), float(confidence)
        
    except Exception as e:
        logger.error(f"Dummy prediction failed: {str(e)}")
        return float(data['prices'][-1] * 1.03), 60.0  # Fallback values