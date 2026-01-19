#!/usr/bin/env python3
"""
Feature Extractor
Extracts ML features from WiFi network data
"""

import numpy as np
from typing import Dict, List
from collections import Counter

class FeatureExtractor:
    """Extract features from network data for ML models"""
    
    def __init__(self):
        self.feature_names = [
            'signal_strength',
            'channel',
            'encryption_type',
            'is_hidden',
            'vendor_trust_score',
            'signal_variance',
            'duplicate_ssid_count',
            'channel_congestion',
            'frequency_band',
            'encryption_strength'
        ]
    
    def extract_features(self, network: Dict, all_networks: List[Dict]) -> np.ndarray:
        """
        Extract feature vector from a single network
        
        Args:
            network: Network to extract features from
            all_networks: All scanned networks (for context)
        
        Returns:
            Feature vector as numpy array
        """
        
        features = []
        
        # Feature 1: Signal strength (-100 to 0 dBm)
        signal = network.get('signal_strength', -80)
        features.append(signal)
        
        # Feature 2: Channel number
        channel = network.get('channel', 0)
        features.append(channel)
        
        # Feature 3: Encryption type (numeric)
        encryption_map = {
            'Open': 0,
            'WEP': 1,
            'WPA': 2,
            'WPA2': 3,
            'WPA3': 4,
            'WPA/WPA2': 2.5
        }
        encryption = network.get('encryption', 'Open')
        encryption_type = encryption_map.get(encryption, 0)
        features.append(encryption_type)
        
        # Feature 4: Is hidden network
        is_hidden = 1 if network.get('is_hidden', False) else 0
        features.append(is_hidden)
        
        # Feature 5: Vendor trust score
        vendor = network.get('vendor', 'Unknown')
        vendor_trust = self._get_vendor_trust_score(vendor)
        features.append(vendor_trust)
        
        # Feature 6: Signal variance (stability)
        signal_variance = self._calculate_signal_variance(network, all_networks)
        features.append(signal_variance)
        
        # Feature 7: Duplicate SSID count
        ssid = network.get('ssid', '')
        duplicate_count = sum(1 for n in all_networks if n.get('ssid') == ssid) - 1
        features.append(duplicate_count)
        
        # Feature 8: Channel congestion
        channel_congestion = self._calculate_channel_congestion(network, all_networks)
        features.append(channel_congestion)
        
        # Feature 9: Frequency band (2.4GHz=0, 5GHz=1)
        frequency = network.get('frequency', 2437)
        frequency_band = 1 if frequency > 5000 else 0
        features.append(frequency_band)
        
        # Feature 10: Encryption strength score
        encryption_strength = self._get_encryption_strength(encryption)
        features.append(encryption_strength)
        
        return np.array(features)
    
    def extract_features_batch(self, networks: List[Dict]) -> np.ndarray:
        """
        Extract features for multiple networks
        
        Returns:
            2D array of shape (n_networks, n_features)
        """
        feature_matrix = []
        
        for network in networks:
            features = self.extract_features(network, networks)
            feature_matrix.append(features)
        
        return np.array(feature_matrix)
    
    def _get_vendor_trust_score(self, vendor: str) -> float:
        """
        Get trust score for vendor (0-1)
        Known/reputable vendors get higher scores
        """
        trusted_vendors = {
            'Apple': 0.95,
            'Cisco': 0.95,
            'Linksys': 0.85,
            'TP-Link': 0.85,
            'Netgear': 0.85,
            'Asus': 0.85,
            'D-Link': 0.80,
            'Belkin': 0.80,
            'Ubiquiti': 0.90,
            'Unknown': 0.30,
            'VMware': 0.50,
            'VirtualBox': 0.50
        }
        
        return trusted_vendors.get(vendor, 0.50)
    
    def _calculate_signal_variance(self, network: Dict, all_networks: List[Dict]) -> float:
        """
        Calculate signal strength variance
        High variance = unstable signal = suspicious
        """
        # In a real system, this would track signal over time
        # For now, we use a simplified version
        
        ssid = network.get('ssid', '')
        same_ssid_networks = [n for n in all_networks if n.get('ssid') == ssid]
        
        if len(same_ssid_networks) <= 1:
            return 0.0
        
        signals = [n.get('signal_strength', -80) for n in same_ssid_networks]
        variance = np.var(signals)
        
        # Normalize to 0-1 range
        normalized_variance = min(variance / 100.0, 1.0)
        
        return normalized_variance
    
    def _calculate_channel_congestion(self, network: Dict, all_networks: List[Dict]) -> float:
        """
        Calculate how congested the channel is
        More networks on same channel = higher congestion
        """
        channel = network.get('channel', 0)
        networks_on_channel = sum(1 for n in all_networks if n.get('channel') == channel)
        
        # Normalize: 0 networks = 0, 10+ networks = 1
        congestion = min(networks_on_channel / 10.0, 1.0)
        
        return congestion
    
    def _get_encryption_strength(self, encryption: str) -> float:
        """
        Get encryption strength score (0-1)
        Open = 0, WPA3 = 1
        """
        strength_map = {
            'Open': 0.0,
            'WEP': 0.2,
            'WPA': 0.5,
            'WPA2': 0.8,
            'WPA3': 1.0,
            'WPA/WPA2': 0.7
        }
        
        return strength_map.get(encryption, 0.5)
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names"""
        return self.feature_names

# Test function
if __name__ == "__main__":
    extractor = FeatureExtractor()
    
    # Test networks
    networks = [
        {
            'ssid': 'TestNet',
            'bssid': 'AA:BB:CC:DD:EE:FF',
            'signal_strength': -45,
            'channel': 6,
            'encryption': 'WPA2',
            'vendor': 'TP-Link',
            'is_hidden': False,
            'frequency': 2437
        },
        {
            'ssid': 'TestNet',  # Duplicate SSID
            'bssid': '11:22:33:44:55:66',
            'signal_strength': -40,
            'channel': 6,
            'encryption': 'Open',
            'vendor': 'Unknown',
            'is_hidden': False,
            'frequency': 2437
        }
    ]
    
    print("Feature names:", extractor.get_feature_names())
    print("\nExtracting features...")
    
    features = extractor.extract_features_batch(networks)
    
    print(f"\nFeature matrix shape: {features.shape}")
    print("\nNetwork 1 features:", features[0])
    print("Network 2 features:", features[1])