import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import os
from datetime import datetime
from typing import Dict, Tuple, List
import json

class MLTrainer:
    """ML Model training and evaluation"""

    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        self.models = {}
        self.training_history = {}
        
        os.makedirs(model_dir, exist_ok=True)

    def generate_synthetic_training_data(self, num_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for evil twin detection"""
        
        features = []
        labels = []
        
        # Features: [signal_strength, channel_distribution, encryption_type, 
        #            vendor_consistency, behavior_anomaly, traffic_pattern]
        
        for i in range(num_samples):
            # Generate features
            signal_strength = np.random.randint(-100, -30)  # dBm
            
            # Legitimate networks tend to have consistent signal
            channel_variance = np.random.uniform(0, 10) if np.random.random() > 0.3 else np.random.uniform(0, 50)
            
            # Encryption type (0=Open, 1=WEP, 2=WPA, 3=WPA2)
            encryption_type = np.random.choice([0, 1, 2, 3], p=[0.05, 0.05, 0.1, 0.8])
            
            # Vendor consistency (1=consistent/legitimate, 0=inconsistent/suspicious)
            vendor_consistency = np.random.uniform(0.5, 1.0) if np.random.random() > 0.2 else np.random.uniform(0, 0.5)
            
            # Behavior anomaly score (0=normal, 1=suspicious)
            behavior_anomaly = np.random.uniform(0, 0.3) if np.random.random() > 0.3 else np.random.uniform(0.3, 1.0)
            
            # Traffic pattern (0=normal, 1=suspicious)
            traffic_pattern = np.random.uniform(0, 0.3) if np.random.random() > 0.25 else np.random.uniform(0.3, 1.0)
            
            # Client count ratio
            client_count = np.random.randint(0, 50)
            
            # SSID similarity to known networks (0=unique, 1=very similar)
            ssid_similarity = np.random.uniform(0, 0.2) if np.random.random() > 0.3 else np.random.uniform(0.2, 1.0)
            
            feature = [
                signal_strength,
                channel_variance,
                encryption_type,
                vendor_consistency,
                behavior_anomaly,
                traffic_pattern,
                client_count,
                ssid_similarity
            ]
            
            # Generate label based on features (simple rule-based)
            # High anomaly + low consistency = likely evil twin
            threat_score = (behavior_anomaly + traffic_pattern + ssid_similarity) / 3 - vendor_consistency
            
            if threat_score > 0.6:
                label = 1  # Evil twin/suspicious
            else:
                label = 0  # Legitimate
            
            features.append(feature)
            labels.append(label)
        
        return np.array(features), np.array(labels)

    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray, 
                          X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Train Random Forest model"""
        print("Training Random Forest model...")
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }
        
        # Feature importance
        feature_names = [
            'signal_strength', 'channel_variance', 'encryption_type',
            'vendor_consistency', 'behavior_anomaly', 'traffic_pattern',
            'client_count', 'ssid_similarity'
        ]
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        return {
            "model": model,
            "metrics": metrics,
            "feature_importance": feature_importance,
            "model_type": "random_forest"
        }

    def train_gradient_boosting(self, X_train: np.ndarray, y_train: np.ndarray,
                               X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Train Gradient Boosting model"""
        print("Training Gradient Boosting model...")
        
        model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=7,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            verbose=1
        )
        
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }
        
        # Feature importance
        feature_names = [
            'signal_strength', 'channel_variance', 'encryption_type',
            'vendor_consistency', 'behavior_anomaly', 'traffic_pattern',
            'client_count', 'ssid_similarity'
        ]
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        return {
            "model": model,
            "metrics": metrics,
            "feature_importance": feature_importance,
            "model_type": "gradient_boosting"
        }

    def train_ensemble_model(self, X_train: np.ndarray, y_train: np.ndarray,
                            X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Train ensemble model combining multiple classifiers"""
        print("Training Ensemble model...")
        
        # Train individual models
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        rf.fit(X_train, y_train)
        gb.fit(X_train, y_train)
        
        # Get predictions from both models
        rf_pred = rf.predict_proba(X_test)[:, 1]
        gb_pred = gb.predict_proba(X_test)[:, 1]
        
        # Average predictions (soft voting)
        ensemble_pred_proba = (rf_pred + gb_pred) / 2
        ensemble_pred = (ensemble_pred_proba > 0.5).astype(int)
        
        # Metrics
        metrics = {
            "accuracy": accuracy_score(y_test, ensemble_pred),
            "precision": precision_score(y_test, ensemble_pred),
            "recall": recall_score(y_test, ensemble_pred),
            "f1_score": f1_score(y_test, ensemble_pred),
            "confusion_matrix": confusion_matrix(y_test, ensemble_pred).tolist()
        }
        
        return {
            "rf_model": rf,
            "gb_model": gb,
            "metrics": metrics,
            "model_type": "ensemble"
        }

    def train_full_pipeline(self) -> Dict:
        """Complete training pipeline"""
        print("Starting full ML training pipeline...")
        
        # Generate training data
        print("Generating synthetic training data...")
        X, y = self.generate_synthetic_training_data(num_samples=2000)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train models
        rf_result = self.train_random_forest(X_train_scaled, y_train, X_test_scaled, y_test)
        gb_result = self.train_gradient_boosting(X_train_scaled, y_train, X_test_scaled, y_test)
        ensemble_result = self.train_ensemble_model(X_train_scaled, y_train, X_test_scaled, y_test)
        
        # Save models
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Save Random Forest
        rf_path = os.path.join(self.model_dir, f"rf_model_{timestamp}.pkl")
        joblib.dump(rf_result["model"], rf_path)
        
        # Save Gradient Boosting
        gb_path = os.path.join(self.model_dir, f"gb_model_{timestamp}.pkl")
        joblib.dump(gb_result["model"], gb_path)
        
        # Save Ensemble
        ensemble_path = os.path.join(self.model_dir, f"ensemble_rf_{timestamp}.pkl")
        ensemble_gb_path = os.path.join(self.model_dir, f"ensemble_gb_{timestamp}.pkl")
        joblib.dump(ensemble_result["rf_model"], ensemble_path)
        joblib.dump(ensemble_result["gb_model"], ensemble_gb_path)
        
        # Save scaler
        scaler_path = os.path.join(self.model_dir, f"scaler_{timestamp}.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        results = {
            "timestamp": timestamp,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "models": {
                "random_forest": {
                    "path": rf_path,
                    "metrics": rf_result["metrics"],
                    "feature_importance": rf_result["feature_importance"]
                },
                "gradient_boosting": {
                    "path": gb_path,
                    "metrics": gb_result["metrics"],
                    "feature_importance": gb_result["feature_importance"]
                },
                "ensemble": {
                    "paths": {"rf": ensemble_path, "gb": ensemble_gb_path},
                    "metrics": ensemble_result["metrics"]
                }
            },
            "scaler_path": scaler_path
        }
        
        return results

    def load_model(self, model_path: str):
        """Load a trained model"""
        return joblib.load(model_path)

    def save_model_metadata(self, model_info: Dict, filepath: str):
        """Save model metadata to JSON"""
        with open(filepath, 'w') as f:
            json.dump(model_info, f, indent=2)
