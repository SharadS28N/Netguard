import numpy as np
import joblib
import os
from typing import Dict, List, Tuple
from datetime import datetime
import json

class MLInference:
    """ML Model inference engine for threat detection"""

    def __init__(self, models_dir: str = "./models"):
        self.models_dir = models_dir
        self.rf_model = None
        self.gb_model = None
        self.scaler = None
        self.model_loaded = False
        self.model_info = {}

    def load_models(self, model_dir: str = None) -> bool:
        """Load trained models from disk"""
        if model_dir:
            self.models_dir = model_dir
        
        try:
            # Find latest models
            model_files = sorted([f for f in os.listdir(self.models_dir) if f.endswith('.pkl')])
            
            if not model_files:
                print("No model files found")
                return False
            
            # Load the latest versions
            for f in reversed(model_files):
                if 'rf_model' in f and self.rf_model is None:
                    model_path = os.path.join(self.models_dir, f)
                    self.rf_model = joblib.load(model_path)
                    print(f"Loaded RF model: {f}")
                
                elif 'gb_model' in f and self.gb_model is None and 'ensemble' not in f:
                    model_path = os.path.join(self.models_dir, f)
                    self.gb_model = joblib.load(model_path)
                    print(f"Loaded GB model: {f}")
                
                elif 'scaler' in f and self.scaler is None:
                    model_path = os.path.join(self.models_dir, f)
                    self.scaler = joblib.load(model_path)
                    print(f"Loaded scaler: {f}")
            
            if self.rf_model and self.scaler:
                self.model_loaded = True
                print("Models loaded successfully")
                return True
            else:
                print("Failed to load required models")
                return False
        
        except Exception as e:
            print(f"Error loading models: {e}")
            return False

    def extract_features_from_network(self, network: Dict, known_networks: List[Dict] = None) -> np.ndarray:
        """Extract ML features from network data"""
        
        signal_strength = network.get("signal_strength", -80)
        
        # Channel variance (simplified - in real scenario would track over time)
        channel_variance = 0 if network.get("channel") else 10
        
        # Encryption type to numeric (0=Open, 1=WEP, 2=WPA, 3=WPA2)
        encryption_map = {"Open": 0, "WEP": 1, "WPA": 2, "WPA2": 3}
        encryption_type = encryption_map.get(network.get("encryption", "Open"), 0)
        
        # Vendor consistency check
        known_vendors = {"Apple": 0.95, "Linksys": 0.85, "TP-Link": 0.80, "Unknown": 0.40}
        vendor = network.get("vendor", "Unknown")
        vendor_consistency = known_vendors.get(vendor, 0.5)
        
        # Behavior anomaly (placeholder)
        behavior_anomaly = 0.2 if network.get("is_hidden") else 0.1
        
        # Traffic pattern anomaly (based on client count)
        client_count = network.get("client_count", 0)
        traffic_pattern = 0.7 if client_count > 30 else (0.4 if client_count > 10 else 0.1)
        
        # Client count ratio
        client_count_feature = min(client_count / 50, 1.0)
        
        # SSID similarity to known networks
        ssid_similarity = 0.0
        if known_networks:
            ssid = network.get("ssid", "")
            for known in known_networks:
                known_ssid = known.get("ssid", "")
                if ssid and known_ssid:
                    similarity = self._string_similarity(ssid, known_ssid)
                    ssid_similarity = max(ssid_similarity, similarity)
        
        features = np.array([
            signal_strength,
            channel_variance,
            encryption_type,
            vendor_consistency,
            behavior_anomaly,
            traffic_pattern,
            client_count_feature,
            ssid_similarity
        ])
        
        return features

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (Levenshtein-based)"""
        if not s1 or not s2:
            return 0.0
        
        # Simple similarity metric
        matches = sum(1 for a, b in zip(s1, s2) if a == b)
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 0.0
        
        return matches / max_len

    def predict_single_network(self, network: Dict, known_networks: List[Dict] = None) -> Dict:
        """Predict if a single network is an evil twin"""
        
        if not self.model_loaded:
            return {
                "error": "Models not loaded",
                "network": network.get("bssid")
            }
        
        try:
            # Extract features
            features = self.extract_features_from_network(network, known_networks)
            
            # Scale features
            features_scaled = self.scaler.transform([features])[0]
            
            # Get predictions from both models
            rf_pred_proba = self.rf_model.predict_proba([features_scaled])[0]
            gb_pred_proba = self.gb_model.predict_proba([features_scaled])[0] if self.gb_model else rf_pred_proba
            
            # Ensemble vote
            rf_threat_score = rf_pred_proba[1]
            gb_threat_score = gb_pred_proba[1]
            ensemble_threat_score = (rf_threat_score + gb_threat_score) / 2
            
            # Determine threat level
            if ensemble_threat_score > 0.7:
                threat_level = "critical"
            elif ensemble_threat_score > 0.5:
                threat_level = "high"
            elif ensemble_threat_score > 0.3:
                threat_level = "medium"
            else:
                threat_level = "low"
            
            return {
                "bssid": network.get("bssid"),
                "ssid": network.get("ssid"),
                "threat_level": threat_level,
                "confidence_score": float(ensemble_threat_score),
                "model_scores": {
                    "random_forest": float(rf_threat_score),
                    "gradient_boosting": float(gb_threat_score),
                    "ensemble": float(ensemble_threat_score)
                },
                "is_threat": ensemble_threat_score > 0.5,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "network": network.get("bssid")
            }

    def predict_batch(self, networks: List[Dict], known_networks: List[Dict] = None) -> Dict:
        """Predict threats for multiple networks"""
        
        predictions = {
            "predictions": [],
            "summary": {
                "total_networks": len(networks),
                "threats_detected": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for network in networks:
            pred = self.predict_single_network(network, known_networks)
            predictions["predictions"].append(pred)
            
            if not pred.get("error"):
                if pred.get("is_threat"):
                    predictions["summary"]["threats_detected"] += 1
                
                threat_level = pred.get("threat_level")
                predictions["summary"][threat_level] += 1
        
        return predictions

    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            "models_loaded": self.model_loaded,
            "rf_model": "Random Forest" if self.rf_model else None,
            "gb_model": "Gradient Boosting" if self.gb_model else None,
            "scaler": "StandardScaler" if self.scaler else None,
            "models_directory": self.models_dir,
            "timestamp": datetime.utcnow().isoformat()
        }

    def detection_report(self, networks: List[Dict], threats: List[Dict]) -> Dict:
        """Generate detailed detection report"""
        
        report = {
            "report_timestamp": datetime.utcnow().isoformat(),
            "total_networks": len(networks),
            "threats_detected": len(threats),
            "networks_analysis": {
                "by_encryption": {},
                "by_signal_strength": {"strong": 0, "medium": 0, "weak": 0},
                "by_vendor": {},
                "hidden_networks": 0
            },
            "threat_analysis": {
                "by_type": {},
                "by_level": {"critical": 0, "high": 0, "medium": 0, "low": 0}
            },
            "recommendations": []
        }
        
        # Analyze networks
        for network in networks:
            # Encryption analysis
            enc = network.get("encryption", "Unknown")
            report["networks_analysis"]["by_encryption"][enc] = \
                report["networks_analysis"]["by_encryption"].get(enc, 0) + 1
            
            # Signal strength analysis
            signal = network.get("signal_strength", -100)
            if signal > -60:
                report["networks_analysis"]["by_signal_strength"]["strong"] += 1
            elif signal > -80:
                report["networks_analysis"]["by_signal_strength"]["medium"] += 1
            else:
                report["networks_analysis"]["by_signal_strength"]["weak"] += 1
            
            # Vendor analysis
            vendor = network.get("vendor", "Unknown")
            report["networks_analysis"]["by_vendor"][vendor] = \
                report["networks_analysis"]["by_vendor"].get(vendor, 0) + 1
            
            # Hidden networks
            if network.get("is_hidden"):
                report["networks_analysis"]["hidden_networks"] += 1
        
        # Analyze threats
        for threat in threats:
            threat_type = threat.get("threat_type", "unknown")
            report["threat_analysis"]["by_type"][threat_type] = \
                report["threat_analysis"]["by_type"].get(threat_type, 0) + 1
            
            level = threat.get("threat_level", "low")
            report["threat_analysis"]["by_level"][level] += 1
        
        # Generate recommendations
        if report["threat_analysis"]["by_level"]["critical"] > 0:
            report["recommendations"].append("CRITICAL: Disconnect from detected evil twins immediately")
        
        if report["threat_analysis"]["by_level"]["high"] > 0:
            report["recommendations"].append("WARNING: High threat networks detected. Avoid connecting to suspicious networks")
        
        weak_enc = report["networks_analysis"]["by_encryption"].get("WEP", 0) + \
                   report["networks_analysis"]["by_encryption"].get("Open", 0)
        if weak_enc > 0:
            report["recommendations"].append(f"NOTICE: {weak_enc} networks using weak encryption")
        
        if report["networks_analysis"]["hidden_networks"] > 0:
            report["recommendations"].append(f"INFO: {report['networks_analysis']['hidden_networks']} hidden networks detected")
        
        return report
