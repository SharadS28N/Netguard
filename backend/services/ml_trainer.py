"""
ML Model Trainer — Research-Informed Training Pipeline
---
Trains RandomForest and GradientBoosting classifiers for evil twin detection
using research-informed synthetic data that models real-world WiFi attack patterns.

Data distributions based on:
- IEEE 802.11 evil twin attack signatures
- Published WiFi security research (signal patterns, encryption downgrade)
- Real-world AP behavior characteristics
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Tuple

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("netguard.ml_trainer")

# Feature names used across the pipeline
FEATURE_NAMES = [
    "signal_strength",
    "channel_variance",
    "encryption_type",
    "vendor_consistency",
    "behavior_anomaly",
    "traffic_pattern",
    "client_count",
    "ssid_similarity",
]


class MLTrainer:
    """ML model training and evaluation pipeline."""

    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        self.models = {}
        os.makedirs(model_dir, exist_ok=True)

    # ─── Data Generation ─────────────────────────────────────

    def generate_training_data(
        self, num_samples: int = 3000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate research-informed training data for evil twin detection.
        Class distribution: ~75% legitimate, ~25% evil twin
        """
        np.random.seed(42)

        n_legit = int(num_samples * 0.75)
        n_evil = num_samples - n_legit

        # Legitimate Networks
        legit_features = self._generate_legitimate_samples(n_legit)
        legit_labels = np.zeros(n_legit, dtype=int)

        # Evil Twin / Rogue AP Networks
        evil_features = self._generate_evil_twin_samples(n_evil)
        evil_labels = np.ones(n_evil, dtype=int)

        # Combine and shuffle
        X = np.vstack([legit_features, evil_features])
        y = np.concatenate([legit_labels, evil_labels])

        # Shuffle
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]

        logger.info(
            "Generated %d training samples: %d legitimate, %d evil twin",
            len(X),
            n_legit,
            n_evil,
        )
        return X, y

    def _generate_legitimate_samples(self, n: int) -> np.ndarray:
        """Generate features for legitimate WiFi networks."""
        features = np.zeros((n, 8))

        # Signal strength: gaussian centered at -55 dBm
        features[:, 0] = np.random.normal(-55, 10, n).clip(-85, -30)
        # Channel variance: low for stable APs
        features[:, 1] = np.abs(np.random.normal(1.5, 2.0, n)).clip(0, 15)
        # Encryption type: mostly WPA2(3) and WPA3(4)
        enc_choices = [2, 3, 3, 3, 3, 3, 3, 3, 4, 4]
        features[:, 2] = np.random.choice(enc_choices, n)
        # Vendor consistency: high
        features[:, 3] = np.random.beta(8, 2, n).clip(0.5, 1.0)
        # Behavior anomaly: low
        features[:, 4] = np.random.beta(2, 8, n).clip(0, 0.4)
        # Traffic pattern: normal
        features[:, 5] = np.random.beta(2, 6, n).clip(0, 0.5)
        # Client count (normalized 0-1)
        features[:, 6] = np.random.beta(3, 5, n).clip(0, 0.8)
        # SSID similarity to known networks: low
        features[:, 7] = np.random.beta(1.5, 8, n).clip(0, 0.3)

        return features

    def _generate_evil_twin_samples(self, n: int) -> np.ndarray:
        """Generate features for evil twin / rogue AP networks."""
        features = np.zeros((n, 8))

        # Signal strength: often stronger
        strong = int(n * 0.6)
        features[:strong, 0] = np.random.normal(-40, 8, strong).clip(-60, -25)
        features[strong:, 0] = np.random.normal(-55, 15, n - strong).clip(-85, -30)
        # Channel variance: higher
        features[:, 1] = np.random.normal(12, 8, n).clip(0, 50)
        # Encryption type: often downgraded
        enc_probs = [0.40, 0.20, 0.20, 0.15, 0.05]
        features[:, 2] = np.random.choice([0, 1, 2, 3, 4], n, p=enc_probs)
        # Vendor consistency: low
        features[:, 3] = np.random.beta(2, 6, n).clip(0, 0.6)
        # Behavior anomaly: high
        features[:, 4] = np.random.beta(6, 2, n).clip(0.3, 1.0)
        # Traffic pattern: anomalous
        features[:, 5] = np.random.beta(5, 2, n).clip(0.2, 1.0)
        # Client count: varies
        features[:, 6] = np.random.beta(2, 3, n).clip(0, 1.0)
        # SSID similarity: high
        features[:, 7] = np.random.beta(7, 2, n).clip(0.4, 1.0)

        return features

    # ─── Model Training ──────────────────────────────────────

    def train_random_forest(self, X_train, y_train, X_test, y_test) -> Dict:
        """Train Random Forest with optimized hyperparameters."""
        logger.info("Training Random Forest...")
        rf = RandomForestClassifier(
            n_estimators=150,
            max_depth=15,
            min_samples_split=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        metrics = self._compute_metrics(y_test, y_pred)
        self.models["rf"] = rf
        return {
            "model": rf,
            "metrics": metrics,
            "feature_importance": self._get_feature_importance_for_model(rf),
            "model_type": "random_forest",
        }

    def train_gradient_boosting(self, X_train, y_train, X_test, y_test) -> Dict:
        """Train Gradient Boosting with optimized hyperparameters."""
        logger.info("Training Gradient Boosting...")
        gb = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            random_state=42,
        )
        gb.fit(X_train, y_train)
        y_pred = gb.predict(X_test)
        metrics = self._compute_metrics(y_test, y_pred)
        self.models["gb"] = gb
        return {
            "model": gb,
            "metrics": metrics,
            "feature_importance": self._get_feature_importance_for_model(gb),
            "model_type": "gradient_boosting",
        }

    def train_ensemble(self, X_train, y_train, X_test, y_test) -> Dict:
        """Train ensemble model combining RF and GB."""
        logger.info("Training Ensemble model...")
        rf = self.models.get("rf")
        gb = self.models.get("gb")

        # Soft voting ensemble
        rf_proba = rf.predict_proba(X_test)[:, 1]
        gb_proba = gb.predict_proba(X_test)[:, 1]
        ensemble_proba = (rf_proba + gb_proba) / 2
        ensemble_pred = (ensemble_proba > 0.5).astype(int)

        metrics = self._compute_metrics(y_test, ensemble_pred)
        return {
            "rf_model": rf,
            "gb_model": gb,
            "metrics": metrics,
            "model_type": "ensemble",
        }

    def _get_feature_importance_for_model(self, model) -> Dict[str, float]:
        """Extract feature importance from a model."""
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            return dict(zip(FEATURE_NAMES, importances.tolist()))
        return {}

    # ─── Full Pipeline ───────────────────────────────────────

    def train_full_pipeline(self, num_samples: int = 3000) -> Dict:
        """Complete training pipeline."""
        logger.info("=" * 50)
        logger.info("Starting ML training pipeline")
        logger.info("=" * 50)

        # 1. Generate data
        X, y = self.generate_training_data(num_samples)

        # 2. Split
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        # 3. Scale
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # 4. Train models
        rf_result = self.train_random_forest(
            X_train_scaled, y_train, X_test_scaled, y_test
        )
        gb_result = self.train_gradient_boosting(
            X_train_scaled, y_train, X_test_scaled, y_test
        )
        ensemble_result = self.train_ensemble(
            X_train_scaled, y_train, X_test_scaled, y_test
        )

        # 5. Cross-validation
        cv_scores = cross_val_score(
            rf_result["model"],
            X_train_scaled,
            y_train,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring="accuracy",
        )

        # 6. Save models
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        paths = self._save_models(rf_result, gb_result, ensemble_result, timestamp)

        # 7. Build results
        results = {
            "timestamp": timestamp,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "cross_validation": {
                "mean_accuracy": float(cv_scores.mean()),
                "std": float(cv_scores.std()),
            },
            "models": {
                "random_forest": {
                    "path": paths["rf"],
                    "metrics": rf_result["metrics"],
                    "feature_importance": rf_result["feature_importance"],
                },
                "gradient_boosting": {
                    "path": paths["gb"],
                    "metrics": gb_result["metrics"],
                    "feature_importance": gb_result["feature_importance"],
                },
                "ensemble": {
                    "paths": {"rf": paths["ensemble_rf"], "gb": paths["ensemble_gb"]},
                    "metrics": ensemble_result["metrics"],
                },
            },
            "scaler_path": paths["scaler"],
        }

        logger.info("Training pipeline complete")
        return results

    # ─── Model Persistence ───────────────────────────────────

    def _save_models(self, rf_result, gb_result, ensemble_result, timestamp) -> Dict:
        """Save all trained models and scaler to disk."""
        paths = {}
        paths["rf"] = os.path.join(self.model_dir, f"rf_model_{timestamp}.pkl")
        joblib.dump(rf_result["model"], paths["rf"])

        paths["gb"] = os.path.join(self.model_dir, f"gb_model_{timestamp}.pkl")
        joblib.dump(gb_result["model"], paths["gb"])

        paths["ensemble_rf"] = os.path.join(
            self.model_dir, f"ensemble_rf_{timestamp}.pkl"
        )
        joblib.dump(ensemble_result["rf_model"], paths["ensemble_rf"])

        paths["ensemble_gb"] = os.path.join(
            self.model_dir, f"ensemble_gb_{timestamp}.pkl"
        )
        joblib.dump(ensemble_result["gb_model"], paths["ensemble_gb"])

        paths["scaler"] = os.path.join(self.model_dir, f"scaler_{timestamp}.pkl")
        joblib.dump(self.scaler, paths["scaler"])

        # Also save latest versions
        joblib.dump(rf_result["model"], os.path.join(self.model_dir, "rf_model.pkl"))
        joblib.dump(gb_result["model"], os.path.join(self.model_dir, "gb_model.pkl"))
        joblib.dump(self.scaler, os.path.join(self.model_dir, "scaler.pkl"))

        return paths

    @staticmethod
    def _compute_metrics(y_true, y_pred) -> Dict:
        """Compute classification metrics."""
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        }
