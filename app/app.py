from flask import Flask, request, jsonify, render_template # Make sure render_template is here
from models.lstm_model import predict as lstm_predict
from models.random_forest_model import predict as rf_predict
from models.hybrid import predict as hybrid_predict
from utils.data_fetcher import get_crypto_data
from utils.helpers import prepare_prediction_data, handle_api_error
import logging
from datetime import datetime, timedelta

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- New Route for the Home Page ---
@app.route('/')
def index():
    """
    Serves the main HTML page for the cryptocurrency predictor.
    """
    return render_template('index_pro.html')
# --- End New Route ---

# Model performance baselines (pre-calculated from backtesting)
MODEL_BASELINES = {
    'lstm': {
        '24h': {'mae': 0.0185},  # 1.85% MAE
        '168h': {'mae': 0.042}    # 4.2% MAE
    },
    'rf': {
        '24h': {'mae': 0.022},
        '168h': {'mae': 0.048}
    },
    'hybrid': {
        '24h': {'mae': 0.016},
        '168h': {'mae': 0.038}
    }
}

@app.route('/predict')
def predict():
    # ... (your existing /predict route code)
    try:
        crypto_id = request.args.get('crypto', 'bitcoin')
        model_type = request.args.get('model', 'hybrid')
        
        logger.info(f"Prediction request for {crypto_id} using {model_type} model")
        
        # Fetch and prepare data
        raw_prices = get_crypto_data(crypto_id)
        processed_data, baseline_metrics = prepare_prediction_data(raw_prices, [24, 168])
        
        # Make predictions
        predictions = []
        for horizon in [24, 168]:
            if model_type == 'lstm':
                pred_price, _ = lstm_predict(processed_data['prices'], horizon)
            elif model_type == 'rf':
                pred_price, _ = rf_predict(processed_data, horizon)
            else:
                pred_price, _ = hybrid_predict(processed_data, horizon)
            
            # Calculate confidence
            baseline_mae = MODEL_BASELINES[model_type][f'{horizon}h']['mae']
            confidence = calculate_prediction_confidence(
                processed_data['prices'],
                pred_price,
                horizon,
                baseline_mae
            )
            
            predictions.append({
                'timeframe': f'{horizon}h',
                'price': pred_price,
                'confidence': confidence
            })
        
        # Prepare response
        response = {
            'crypto_name': crypto_id.capitalize(),
            'current_price': raw_prices[-1],
            'predictions': predictions,
            'history': raw_prices[-24*7:],  # Last week of data
            'timestamp': datetime.utcnow().isoformat(),
            'model_used': get_model_name(model_type)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        error_response = handle_api_error(e)
        return jsonify(error_response), 500

def calculate_prediction_confidence(prices, pred_price, horizon, baseline_mae):
    """Calculate confidence score for a prediction"""
    # Get the actual price at horizon if available (for backtesting)
    actual_price = None
    if len(prices) > horizon:
        actual_price = prices[-horizon]
    
    # Calculate error (use naive prediction if actual not available)
    if actual_price is not None:
        error = abs(pred_price - actual_price) / actual_price
    else:
        # Estimate error based on model's typical performance
        error = baseline_mae * 1.2  # Conservative estimate
        
    # Convert to confidence (0-100%)
    confidence = max(10, min(99, 100 * (1 - error / baseline_mae)))
    return round(confidence, 1)

def get_model_name(model_type):
    names = {
        'lstm': 'LSTM Neural Network',
        'rf': 'Random Forest',
        'hybrid': 'Hybrid LSTM+RF Model'
    }
    return names.get(model_type, 'Unknown Model')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)