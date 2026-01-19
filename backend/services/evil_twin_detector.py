#!/usr/bin/env python3
"""
Evil Twin Detector
Combines rule-based and ML-based detection
"""

from typing import Dict, List
import numpy as np
from .rule_engine import RuleEngine
from .feature_extractor import FeatureExtractor
from .ml_inference import MLInference

class EvilTwinDetector:
    """Combined detection system"""
    
    def __init__(self, models_dir: str = './models'):
        self.rule_engine = RuleEngine()
        self.feature_extractor = FeatureExtractor()
        self.ml_inference = MLInference(models_dir)
        
        # Load ML models
        self.ml_loaded = self.ml_inference.load_models()
    
    def detect(self, networks: List[Dict]) -> Dict:
        """
        Run complete detection pipeline
        
        Returns:
            Complete detection results
        """
        
        if not networks:
            return {
                'networks_scanned': 0,
                'evil_twins_detected': [],
                'suspicious_networks': [],
                'threat_level': 'safe',
                'overall_confidence': 0.0,
                'detection_methods': {
                    'rule_based': {},
                    'ml_based': {}
                }
            }
        
        # Step 1: Rule-based detection
        rule_results = self.rule_engine.detect(networks)
        
        # Step 2: ML-based detection (if models loaded)
        ml_results = {'predictions': [], 'confidences': []}
        
        if self.ml_loaded:
            features = self.feature_extractor.extract_features_batch(networks)
            ml_results = self.ml_inference.predict(features)
        
        # Step 3: Combine results
        combined_results = self._combine_results(
            networks,
            rule_results,
            ml_results
        )
        
        return combined_results
    
    def _combine_results(self, networks: List[Dict], 
                        rule_results: Dict, 
                        ml_results: Dict) -> Dict:
        """Combine rule-based and ML-based results"""
        
        evil_twins = []
        suspicious = []
        
        # Networks flagged by rules
        rule_evil_twins = {n['bssid']: n for n in rule_results.get('evil_twins', [])}
        rule_suspicious = {n['bssid']: n for n in rule_results.get('suspicious_networks', [])}
        
        # Networks flagged by ML
        ml_predictions = ml_results.get('predictions', [])
        ml_confidences = ml_results.get('confidences', [])
        
        for i, network in enumerate(networks):
            bssid = network['bssid']
            
            # Get ML prediction for this network
            ml_pred = ml_predictions[i] if i < len(ml_predictions) else 0
            ml_conf = ml_confidences[i] if i < len(ml_confidences) else 0.0
            
            # Get rule-based detection
            in_rule_evil = bssid in rule_evil_twins
            in_rule_suspicious = bssid in rule_suspicious
            
            # Combine scores
            rule_score = 0.85 if in_rule_evil else (0.55 if in_rule_suspicious else 0.0)
            ml_score = ml_conf if ml_pred == 1 else 0.0
            
            # Weighted combination (60% rules, 40% ML)
            combined_score = (rule_score * 0.6) + (ml_score * 0.4)
            
            network_result = {
                **network,
                'detection_score': combined_score,
                'detected_by_rules': in_rule_evil or in_rule_suspicious,
                'detected_by_ml': ml_pred == 1,
                'ml_confidence': ml_score,
                'rule_confidence': rule_score
            }
            
            # Classify based on combined score
            if combined_score >= 0.70:
                evil_twins.append(network_result)
            elif combined_score >= 0.40:
                suspicious.append(network_result)
        
        # Determine overall threat level
        threat_level = 'safe'
        if len(evil_twins) > 0:
            threat_level = 'danger'
        elif len(suspicious) > 0:
            threat_level = 'suspicious'
        
        # Calculate overall confidence
        all_detections = evil_twins + suspicious
        overall_conf = 0.0
        if all_detections:
            overall_conf = sum(d['detection_score'] for d in all_detections) / len(all_detections)
        
        return {
            'networks_scanned': len(networks),
            'evil_twins_detected': evil_twins,
            'suspicious_networks': suspicious,
            'threat_level': threat_level,
            'overall_confidence': overall_conf,
            'detection_methods': {
                'rule_based': {
                    'triggered_rules': len(rule_results.get('rule_triggers', [])),
                    'confidence': rule_results.get('overall_confidence', 0.0)
                },
                'ml_based': {
                    'predictions_made': len(ml_predictions),
                    'average_confidence': np.mean(ml_confidences) if ml_confidences else 0.0
                }
            },
            'recommendations': self._generate_recommendations(evil_twins, suspicious)
        }
    
    def _generate_recommendations(self, evil_twins: List[Dict], 
                                  suspicious: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if evil_twins:
            recommendations.append("⚠️ CRITICAL: Evil twin attack detected!")
            recommendations.append("Do NOT connect to the following networks:")
            for net in evil_twins:
                recommendations.append(f"  • {net['ssid']} ({net['bssid']})")
            recommendations.append("Recommended action: Use VPN, verify network with administrator")
        
        if suspicious:
            recommendations.append("⚠️ WARNING: Suspicious networks detected")
            recommendations.append("Exercise caution with these networks:")
            for net in suspicious:
                recommendations.append(f"  • {net['ssid']} ({net['bssid']})")
            recommendations.append("Recommended action: Verify network authenticity before connecting")
        
        if not evil_twins and not suspicious:
            recommendations.append("✅ No threats detected")
            recommendations.append("All scanned networks appear legitimate")
            recommendations.append("Still recommended: Use VPN on public networks")
        
        return recommendations

# Test
if __name__ == "__main__":
    detector = EvilTwinDetector()
    
    test_networks = [
        {'ssid': 'TestNet', 'bssid': 'AA:BB:CC:DD:EE:FF', 'signal_strength': -45, 
         'channel': 6, 'encryption': 'WPA2', 'vendor': 'TP-Link', 'is_hidden': False, 
         'frequency': 2437},
        {'ssid': 'TestNet', 'bssid': '11:22:33:44:55:66', 'signal_strength': -40, 
         'channel': 6, 'encryption': 'Open', 'vendor': 'Unknown', 'is_hidden': False, 
         'frequency': 2437},
    ]
    
    results = detector.detect(test_networks)
    
    print(f"Networks scanned: {results['networks_scanned']}")
    print(f"Threat level: {results['threat_level']}")
    print(f"Evil twins: {len(results['evil_twins_detected'])}")
    print(f"Suspicious: {len(results['suspicious_networks'])}")
    print(f"\nRecommendations:")
    for rec in results['recommendations']:
        print(f"  {rec}")