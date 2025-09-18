import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import precision_score, recall_score
import logging
from config import settings

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def preprocess_data(self, data):
        # Select numeric features for anomaly detection
        features = data[['cpu_usage', 'latency']].fillna(0)
        scaled_features = self.scaler.fit_transform(features)
        return scaled_features
    
    def isolation_forest(self, data):
        model = IsolationForest(
            contamination=settings.ISOLATION_FOREST_CONTAMINATION, 
            random_state=42
        )
        predictions = model.fit_predict(data)
        # Convert to 0 (normal) and 1 (anomaly)
        return [1 if x == -1 else 0 for x in predictions]
    
    def one_class_svm(self, data):
        model = OneClassSVM(nu=settings.ONE_CLASS_SVM_NU)
        predictions = model.fit_predict(data)
        return [1 if x == -1 else 0 for x in predictions]
    
    def lstm_autoencoder(self, data):
        # Reshape data for LSTM [samples, timesteps, features]
        data = data.reshape((data.shape[0], 1, data.shape[1]))
        
        # Define a simpler model
        model = Sequential()
        model.add(LSTM(32, activation='relu', input_shape=(1, data.shape[2]), return_sequences=False))
        model.add(RepeatVector(1))
        model.add(LSTM(32, activation='relu', return_sequences=True))
        model.add(TimeDistributed(Dense(data.shape[2])))
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        
        # Train with fewer epochs
        model.fit(data, data, 
                epochs=5,  # Reduced from 10 to 5
                batch_size=128,  # Increased batch size
                validation_split=0.1,
                verbose=0)
        
        # Predict and calculate reconstruction error
        predictions = model.predict(data, verbose=0, batch_size=128)
        mse = np.mean(np.power(data - predictions, 2), axis=(1,2))
        threshold = np.percentile(mse, 100 * (1 - settings.ISOLATION_FOREST_CONTAMINATION))
        return [1 if e > threshold else 0 for e in mse]
    
    def statistical_threshold(self, data):
        # Using Z-score on the scaled data (which is already standardized)
        anomalies = []
        for i in range(data.shape[0]):
            z_score_cpu = abs(data[i, 0])
            z_score_latency = abs(data[i, 1])
            if z_score_cpu > settings.Z_SCORE_THRESHOLD or \
               z_score_latency > settings.Z_SCORE_THRESHOLD:
                anomalies.append(1)
            else:
                anomalies.append(0)
        return anomalies
    
    def detect_anomalies(self, data):
        processed_data = self.preprocess_data(data)
        results = {}
        
        # Run each model
        results['isolation_forest'] = self.isolation_forest(processed_data)
        results['one_class_svm'] = self.one_class_svm(processed_data)
        results['lstm_autoencoder'] = self.lstm_autoencoder(processed_data)
        results['statistical'] = self.statistical_threshold(processed_data)
        
        # Combine results (simple voting)
        combined = np.sum([results[m] for m in results], axis=0)
        # Mark as anomaly if at least two models flag it
        results['combined'] = [1 if c >= 2 else 0 for c in combined]
        
        return results
    
    def evaluate(self, data, true_anomalies):
        # true_anomalies is a list of known anomalies (1 for anomaly, 0 for normal)
        processed_data = self.preprocess_data(data)
        results = self.detect_anomalies(data)
        
        evaluation = {}
        for model_name, preds in results.items():
            precision = precision_score(true_anomalies, preds, zero_division=0)
            recall = recall_score(true_anomalies, preds, zero_division=0)
            evaluation[model_name] = {'precision': precision, 'recall': recall}
            
        return evaluation