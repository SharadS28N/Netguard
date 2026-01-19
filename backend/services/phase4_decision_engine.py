"""
Phase 4: Decision & Confidence Engine
--------------------------------------
This service is the REASONING LAYER that aggregates multi-layer evidence
from Phase 3 and produces final verdicts with confidence scores and explanations.

STRICT RULES:
- Input: anomaly_signals only (Phase 3 output)
- Output: threats (final verdicts) + detection_logs (audit trail)
- No scanning, no feature extraction, no ML training
- Pure policy-based reasoning

Architecture:
  Phase 3 suspects.
  Phase 4 decides.
"""

from typing import Dict, List, Optional
from datetime import datetime
from models.database import Database


class Phase4DecisionEngine:
    """
    Core engine for making final threat decisions based on aggregated signals.
    """

    # Evidence weighting configuration
    WEIGHTS = {
        "signature": 0.4,  # Deterministic, high precision
        "behavior": 0.3,   # Statistical, context-dependent
        "ml": 0.3          # Unsupervised, catches unknowns
    }

    # Verdict thresholds
    VERDICT_THRESHOLDS = {
        "benign": (0.0, 0.3),
        "suspicious": (0.3, 0.6),
        "likely_evil_twin": (0.6, 0.8),
        "confirmed_evil_twin": (0.8, 1.0)
    }

    # Threat level mapping
    THREAT_LEVELS = {
        "benign": "low",
        "suspicious": "medium",
        "likely_evil_twin": "high",
        "confirmed_evil_twin": "critical"
    }

    # Human-readable explanations for each signal
    SIGNAL_EXPLANATIONS = {
        # Layer 1 - Signature
        "ssid_reuse": "SSID reused across multiple BSSIDs",
        "encryption_weak": "Weak or no encryption detected",
        "vendor_mismatch": "Vendor OUI inconsistency detected",
        "channel_instability": "Frequent channel changes observed",
        
        # Layer 2 - Behavior
        "signal_variance_high": "Unstable signal behavior observed",
        "client_spike": "Unusual client count spike detected",
        "unstable_presence": "Network appears and disappears frequently",
        
        # Layer 3 - ML
        "is_outlier": "ML model flagged this AP as anomalous"
    }

    def __init__(self):
        """
        Initialize database connections.
        """
        self.db = Database.get_db()
        self.anomaly_collection = self.db["anomaly_signals"]
        self.threats_collection = self.db["threats"]
        self.detection_logs_collection = self.db["detection_logs"]

    def run(self):
        """
        Main execution pipeline:
        1. Load all anomaly signals from Phase 3
        2. Group by (ssid, bssid)
        3. Aggregate evidence from all 3 layers
        4. Compute confidence scores
        5. Decide verdict
        6. Generate explanations
        7. Save to threats + detection_logs
        """
        print("[Phase 4] Starting Decision Engine...")
        
        # Load all signals
        signals = self.load_anomaly_signals()
        
        if not signals:
            print("[Phase 4] No anomaly signals found. Nothing to decide.")
            return
        
        print(f"[Phase 4] Processing {len(signals)} anomaly signals...")
        
        # Group signals by network
        grouped_signals = self.group_signals_by_network(signals)
        
        # Process each network
        decisions = []
        for network_key, network_signals in grouped_signals.items():
            decision = self.make_decision(network_key, network_signals)
            decisions.append(decision)
        
        # Save all decisions
        self.save_decisions(decisions)
        
        print(f"[Phase 4] Completed. {len(decisions)} decisions made.")
        
        # Log summary
        self.log_detection_summary(decisions)

    def load_anomaly_signals(self) -> List[Dict]:
        """
        Fetch all anomaly signals from Phase 3 output.
        """
        return list(self.anomaly_collection.find({}))

    def group_signals_by_network(self, signals: List[Dict]) -> Dict[tuple, List[Dict]]:
        """
        Group signals by (ssid, bssid) to aggregate evidence per network.
        
        Returns:
            Dict mapping (ssid, bssid) -> [list of signal documents]
        """
        grouped = {}
        
        for signal in signals:
            ssid = signal.get("ssid")
            bssid = signal.get("bssid")
            
            if not ssid or not bssid:
                continue
            
            key = (ssid, bssid)
            if key not in grouped:
                grouped[key] = []
            
            grouped[key].append(signal)
        
        return grouped

    def make_decision(self, network_key: tuple, signals: List[Dict]) -> Dict:
        """
        Core decision-making logic for a single network.
        
        Args:
            network_key: (ssid, bssid) tuple
            signals: List of signal documents from all 3 layers
        
        Returns:
            Decision document with verdict, confidence, and explanation
        """
        ssid, bssid = network_key
        
        # Aggregate signals from all layers
        layer_scores = self.compute_layer_scores(signals)
        
        # Compute weighted confidence
        confidence = self.compute_confidence(layer_scores)
        
        # Determine verdict based on confidence
        verdict = self.determine_verdict(confidence)
        
        # Generate human-readable explanation
        explanation = self.generate_explanation(signals)
        
        # Map to threat level
        threat_level = self.THREAT_LEVELS.get(verdict, "unknown")
        
        return {
            "ssid": ssid,
            "bssid": bssid,
            "verdict": verdict,
            "confidence": round(confidence, 4),
            "threat_level": threat_level,
            "explanation": explanation,
            "layer_scores": layer_scores,
            "timestamp": datetime.utcnow().isoformat()
        }

    def compute_layer_scores(self, signals: List[Dict]) -> Dict[str, float]:
        """
        Compute individual scores for each layer (Signature, Behavior, ML).
        
        Returns:
            {
                "signature": 0.75,
                "behavior": 0.67,
                "ml": 1.0
            }
        """
        scores = {
            "signature": 0.0,
            "behavior": 0.0,
            "ml": 0.0
        }
        
        for signal in signals:
            layer = signal.get("layer")
            
            if layer == "signature":
                # Count TRUE signals in Layer 1
                sig_signals = signal.get("signals", {})
                true_count = sum(1 for v in sig_signals.values() if v is True)
                total_count = len(sig_signals)
                scores["signature"] = true_count / total_count if total_count > 0 else 0.0
            
            elif layer == "behavior":
                # Count TRUE signals in Layer 2
                beh_signals = signal.get("signals", {})
                true_count = sum(1 for v in beh_signals.values() if v is True)
                total_count = len(beh_signals)
                scores["behavior"] = true_count / total_count if total_count > 0 else 0.0
            
            elif layer == "ml":
                # Binary: outlier or not
                is_outlier = signal.get("is_outlier", False)
                scores["ml"] = 1.0 if is_outlier else 0.0
        
        return scores

    def compute_confidence(self, layer_scores: Dict[str, float]) -> float:
        """
        Compute weighted confidence score from all layers.
        
        Formula:
            confidence = (signature × 0.4) + (behavior × 0.3) + (ml × 0.3)
        
        Returns:
            Float between 0.0 and 1.0
        """
        confidence = (
            layer_scores["signature"] * self.WEIGHTS["signature"] +
            layer_scores["behavior"] * self.WEIGHTS["behavior"] +
            layer_scores["ml"] * self.WEIGHTS["ml"]
        )
        
        return min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]

    def determine_verdict(self, confidence: float) -> str:
        """
        Map confidence score to verdict category.
        
        Thresholds:
            0.0 - 0.3: benign
            0.3 - 0.6: suspicious
            0.6 - 0.8: likely_evil_twin
            0.8 - 1.0: confirmed_evil_twin
        """
        for verdict, (low, high) in self.VERDICT_THRESHOLDS.items():
            if low <= confidence < high:
                return verdict
        
        # Edge case: confidence == 1.0
        if confidence >= 0.8:
            return "confirmed_evil_twin"
        
        return "benign"

    def generate_explanation(self, signals: List[Dict]) -> List[str]:
        """
        Generate human-readable explanations for the decision.
        
        Returns:
            List of explanation strings, e.g.:
            [
                "SSID reused across multiple BSSIDs",
                "Weak encryption detected",
                "ML model flagged this AP as anomalous"
            ]
        """
        explanations = []
        
        for signal in signals:
            layer = signal.get("layer")
            
            if layer == "signature":
                sig_signals = signal.get("signals", {})
                for key, value in sig_signals.items():
                    if value is True and key in self.SIGNAL_EXPLANATIONS:
                        explanations.append(self.SIGNAL_EXPLANATIONS[key])
            
            elif layer == "behavior":
                beh_signals = signal.get("signals", {})
                for key, value in beh_signals.items():
                    if value is True and key in self.SIGNAL_EXPLANATIONS:
                        explanations.append(self.SIGNAL_EXPLANATIONS[key])
            
            elif layer == "ml":
                is_outlier = signal.get("is_outlier", False)
                if is_outlier:
                    explanations.append(self.SIGNAL_EXPLANATIONS["is_outlier"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_explanations = []
        for exp in explanations:
            if exp not in seen:
                seen.add(exp)
                unique_explanations.append(exp)
        
        return unique_explanations

    def save_decisions(self, decisions: List[Dict]):
        """
        Save all decisions to the threats collection.
        """
        if not decisions:
            return
        
        for decision in decisions:
            # Upsert based on (ssid, bssid)
            self.threats_collection.update_one(
                {
                    "ssid": decision["ssid"],
                    "bssid": decision["bssid"]
                },
                {"$set": decision},
                upsert=True
            )
        
        print(f"[Phase 4] Saved {len(decisions)} decisions to 'threats' collection")

    def log_detection_summary(self, decisions: List[Dict]):
        """
        Save a summary log to detection_logs for audit trail.
        """
        # Count verdicts
        verdict_counts = {}
        for decision in decisions:
            verdict = decision["verdict"]
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        summary = {
            "event_type": "phase4_decision_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "total_decisions": len(decisions),
            "verdict_breakdown": verdict_counts,
            "high_confidence_threats": [
                {
                    "ssid": d["ssid"],
                    "bssid": d["bssid"],
                    "verdict": d["verdict"],
                    "confidence": d["confidence"]
                }
                for d in decisions if d["confidence"] >= 0.6
            ]
        }
        
        self.detection_logs_collection.insert_one(summary)
        print(f"[Phase 4] Logged summary to 'detection_logs' collection")
