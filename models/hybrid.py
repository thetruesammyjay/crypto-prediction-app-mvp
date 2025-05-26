from models.lstm_model import predict as lstm_predict
from models.random_forest_model import predict as rf_predict
from typing import Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def predict(data: Dict, horizon: int) -> Tuple[float, float]:
    """Combine dummy predictions"""
    try:
        # Get individual model predictions
        lstm_price, lstm_conf = lstm_predict(data['prices'], horizon)
        rf_price, rf_conf = rf_predict(data, horizon)
        
        # Weighted average
        hybrid_price = 0.6 * lstm_price + 0.4 * rf_price
        hybrid_conf = 0.6 * lstm_conf + 0.4 * rf_conf
        
        # Add some random variation
        hybrid_price *= (0.99 + 0.02 * np.random.rand())
        hybrid_conf = max(60, min(95, hybrid_conf))
        
        return float(hybrid_price), float(hybrid_conf)
        
    except Exception as e:
        logger.error(f"Dummy hybrid prediction failed: {str(e)}")
        return float(data['prices'][-1] * 1.04), 70.0  # Fallback values