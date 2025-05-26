# create_dummy_models.py
import os
import pickle
import numpy as np

# Try to import TensorFlow/Keras
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    KERAS_AVAILABLE = True
except ImportError:
    print("TensorFlow/Keras not found. Dummy .h5 models will be very basic or skipped.")
    KERAS_AVAILABLE = False

# Try to import scikit-learn
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    print("Scikit-learn not found. Dummy .pkl models will be skipped.")
    SKLEARN_AVAILABLE = False

# Define the models directory
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# --- Dummy LSTM Models (.h5) ---
if KERAS_AVAILABLE:
    print("Creating dummy LSTM models...")

    # Dummy LSTM Model for 24h
    model_24h = keras.Sequential([
        layers.Input(shape=(10, 1)), # Example input shape: 10 timesteps, 1 feature
        layers.LSTM(32),
        layers.Dense(1)
    ])
    model_24h.compile(optimizer='adam', loss='mse')
    model_24h.save(os.path.join(MODELS_DIR, 'lstm_24h.h5'))
    print(f"Saved: {os.path.join(MODELS_DIR, 'lstm_24h.h5')}")

    # Dummy LSTM Model for 168h
    model_168h = keras.Sequential([
        layers.Input(shape=(20, 1)), # Example input shape: 20 timesteps, 1 feature
        layers.LSTM(64),
        layers.Dense(1)
    ])
    model_168h.compile(optimizer='adam', loss='mse')
    model_168h.save(os.path.join(MODELS_DIR, 'lstm_168h.h5'))
    print(f"Saved: {os.path.join(MODELS_DIR, 'lstm_168h.h5')}")
else:
    print("Skipping LSTM model creation due to missing TensorFlow/Keras.")


# --- Dummy Random Forest Models and Scaler (.pkl) ---
if SKLEARN_AVAILABLE:
    print("\nCreating dummy Random Forest models and Scaler...")

    # Dummy Random Forest Model for 24h
    rf_24h = RandomForestRegressor(n_estimators=10, random_state=42)
    # Simulate fitting with some dummy data
    X_dummy_rf_24h = np.random.rand(100, 5) # 100 samples, 5 features
    y_dummy_rf_24h = np.random.rand(100)
    rf_24h.fit(X_dummy_rf_24h, y_dummy_rf_24h)

    with open(os.path.join(MODELS_DIR, 'rf_24h.pkl'), 'wb') as f:
        pickle.dump(rf_24h, f)
    print(f"Saved: {os.path.join(MODELS_DIR, 'rf_24h.pkl')}")

    # Dummy Random Forest Model for 168h
    rf_168h = RandomForestRegressor(n_estimators=20, random_state=42)
    # Simulate fitting with some dummy data
    X_dummy_rf_168h = np.random.rand(100, 10) # 100 samples, 10 features
    y_dummy_rf_168h = np.random.rand(100)
    rf_168h.fit(X_dummy_rf_168h, y_dummy_rf_168h)

    with open(os.path.join(MODELS_DIR, 'rf_168h.pkl'), 'wb') as f:
        pickle.dump(rf_168h, f)
    print(f"Saved: {os.path.join(MODELS_DIR, 'rf_168h.pkl')}")

    # Dummy Scaler
    scaler = StandardScaler()
    # Simulate fitting with some dummy data
    data_for_scaler = np.random.rand(100, 5)
    scaler.fit(data_for_scaler)

    with open(os.path.join(MODELS_DIR, 'rf_scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Saved: {os.path.join(MODELS_DIR, 'rf_scaler.pkl')}")
else:
    print("Skipping Random Forest and Scaler creation due to missing scikit-learn.")

print("\nDummy model creation script finished.")
