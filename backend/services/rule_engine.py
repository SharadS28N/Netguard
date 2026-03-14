"""
Netguard Rule Engine Service
---
Deterministic threat detection based on WiFi security standards,
vendor validation, and SSID/BSSID heuristics.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger("netguard.rule_engine")


class RuleEngine:
    """
    Analyzes WiFi scan results against a set of security rules.
    This provides 'Explainable AI'/Deterministic results alongside ML models.
    """

    @staticmethod
    def detect(networks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run detection rules on a list of scanned networks.

        Returns:
            List of threat objects found.
        """
        threats = []
        ssids = {}

        # Group by SSID to find duplicates (potential evil twins)
        for net in networks:
            ssid = net.get("ssid", "<HIDDEN>")
            if ssid not in ssids:
                ssids[ssid] = []
            ssids[ssid].append(net)

        for ssid, variants in ssids.items():
            # Rule 1: SSID Duplicate Detection (Same SSID, Different BSSID/Security)
            if len(variants) > 1:
                # Check for security downgrades among same SSID
                securities = [v.get("security", "OPEN") for v in variants]
                if "OPEN" in securities and any(s != "OPEN" for s in securities):
                    # Potential evil twin: one variant is OPEN while others are secure
                    for v in variants:
                        if v.get("security") == "OPEN":
                            threats.append(
                                RuleEngine._create_threat(
                                    v,
                                    "Security Downgrade",
                                    "Network with same SSID is OPEN while others are encrypted.",
                                    0.95,
                                )
                            )

            for net in variants:
                # Rule 2: Suspicious Security (OPEN or WEP)
                security = net.get("security", "OPEN").upper()
                if security in ["OPEN", "WEP"]:
                    threats.append(
                        RuleEngine._create_threat(
                            net,
                            "Insecure Protocol",
                            f"Network uses insecure {security} encryption.",
                            0.40 if security == "OPEN" else 0.60,
                        )
                    )

                # Rule 3: Hidden SSID
                if net.get("ssid") == "<HIDDEN>" or not net.get("ssid"):
                    threats.append(
                        RuleEngine._create_threat(
                            net,
                            "Hidden Network",
                            "Network is hiding its SSID, often used by attackers to stay stealthy.",
                            0.30,
                        )
                    )

                # Rule 4: Suspicious Vendor (OUI Lookup)
                vendor = net.get("vendor", "Unknown").lower()
                suspicious_vendors = [
                    "unknown",
                    "generic",
                    "espressif",
                ]  # ESP chips are common in rogue APs
                if vendor in suspicious_vendors:
                    threats.append(
                        RuleEngine._create_threat(
                            net,
                            "Untrusted Vendor",
                            f"Network hardware vendor '{vendor}' is suspicious or unknown.",
                            0.25,
                        )
                    )

        return threats

    @staticmethod
    def _create_threat(
        net: Dict[str, Any], type_str: str, desc: str, score: float
    ) -> Dict[str, Any]:
        """Helper to format a threat object."""
        return {
            "ssid": net.get("ssid", "<HIDDEN>"),
            "bssid": net.get("bssid", "00:00:00:00:00:00"),
            "threat_type": type_str,
            "description": desc,
            "confidence": score,
            "severity": "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.4 else "LOW",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "signal": net.get("signal_dbm", -100),
                "channel": net.get("channel", 0),
                "security": net.get("security", "UNKNOWN"),
            },
        }
