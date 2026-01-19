"""
Phase 2: Feature Extraction & Baseline Modeling
-----------------------------------------------
This service transforms raw time-series Wi-Fi scan data
into aggregated behavioral feature vectors.

STRICT RULES:
- Input: raw_scans only
- Output: features_baseline only
- No ML
- No anomaly detection
- No threat labeling
- No confidence scoring
"""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

import numpy as np

from models.database import Database


class Phase2FeatureExtractor:
    """
    Phase 2 Feature Extractor
    Aggregates raw scan data into baseline behavioral features.
    """

    def __init__(self):
        self.db = Database.get_db()
        self.raw_collection = self.db["raw_scans"]
        self.features_collection = self.db["features_baseline"]

    # -------------------------
    # Public entry point
    # -------------------------

    def run(self):
        """
        Main entry point for Phase 2 feature extraction.
        """
        # Safety Check: Do not run if no raw data exists
        if self.raw_collection.count_documents({}) == 0:
            print("[Phase2] Warning: No raw scans found. Aborting baseline generation.")
            return

        scans = self.load_raw_scans()
        grouped = self.process_data(scans)

        for key, observations in grouped.items():
            features = self.calculate_features(observations)
            self.save_features(features)

    # -------------------------
    # Data loading
    # -------------------------

    def load_raw_scans(self) -> List[Dict]:
        """
        Load all raw scan documents from MongoDB.

        Phase 2 MUST NOT modify raw data.
        """
        return list(self.raw_collection.find({}))

    # -------------------------
    # Aggregation
    # -------------------------

    def process_data(self, scans: List[Dict]) -> Dict:
        """
        Group raw scans by (ssid, bssid).
        """
        grouped = defaultdict(list)

        for scan in scans:
            ssid = scan.get("ssid")
            bssid = scan.get("bssid")

            if not ssid or not bssid:
                continue

            key = (ssid, bssid)
            grouped[key].append(scan)

        return grouped

    # -------------------------
    # Feature calculation
    # -------------------------

    def calculate_features(self, observations: List[Dict]) -> Dict:
        """
        Calculate aggregated behavioral features for a single (ssid, bssid).
        """

        ssid = observations[0].get("ssid")
        bssid = observations[0].get("bssid")

        # Collect numeric fields
        signals = []
        channels = []
        client_counts = []
        timestamps = []

        for obs in observations:
            if "signal" in obs:
                try:
                    signals.append(self._parse_int(obs["signal"]))
                except ValueError:
                    pass

            if "channel" in obs:
                try:
                    channels.append(self._parse_int(obs["channel"]))
                except ValueError:
                    pass

            if "connected_stations" in obs:
                try:
                    client_counts.append(self._parse_int(obs["connected_stations"]))
                except ValueError:
                    pass

            if "timestamp" in obs:
                timestamps.append(obs["timestamp"])

        features = {
            "ssid": ssid,
            "bssid": bssid,

            # Signal statistics
            "avg_signal": np.mean(signals) if signals else None,
            "signal_variance": np.std(signals) if signals else None,

            # Channel statistics
            "avg_channel": self._mode(channels),
            "channel_variance": np.std(channels) if len(channels) > 1 else 0,

            # Client statistics
            "client_count_avg": np.mean(client_counts) if client_counts else None,
            "client_count_max": max(client_counts) if client_counts else None,

            # Time statistics
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
            "observation_count": len(observations),

            # Metadata
            "updated_at": datetime.utcnow().isoformat()
        }

        return features

    # -------------------------
    # Persistence
    # -------------------------

    def save_features(self, features: Dict):
        """
        Save aggregated features to MongoDB.

        Rule:
        - One document per (ssid, bssid)
        - Upsert allowed
        """
        query = {
            "ssid": features["ssid"],
            "bssid": features["bssid"]
        }

        self.features_collection.update_one(
            query,
            {"$set": features},
            upsert=True
        )

    # -------------------------
    # Utility helpers
    # -------------------------

    @staticmethod
    def _parse_int(value: str) -> int:
        """
        Extract integer from strings like '87%' or 'Channel: 36'.
        """
        return int("".join(filter(str.isdigit, value)))

    @staticmethod
    def _mode(values: List[int]):
        """
        Return the most common value in a list.
        """
        if not values:
            return None
        return max(set(values), key=values.count)
