"""
Scan Routes — WiFi Network Scanning API
---
REST endpoints for WiFi scanning using cross-platform WiFiScanner.
"""

import logging
import uuid
import threading

from flask import Blueprint, request, jsonify
from services.wifi_scanner import WiFiScanner
from models.database import Database
from datetime import datetime, timezone
from socket_server import socketio

logger = logging.getLogger("netguard.routes.scan")

scan_bp = Blueprint("scan", __name__, url_prefix="/api/scan")

# Global scanner instance
_scanner = None


def _get_scanner() -> WiFiScanner:
    """Get or create the singleton WiFi scanner."""
    global _scanner
    if _scanner is None:
        _scanner = WiFiScanner()
    return _scanner


@scan_bp.route("/start", methods=["POST"])
def start_scan():
    """Start a WiFi network scan."""
    try:
        data = request.get_json(silent=True) or {}
        duration = min(data.get("duration", 10), 60)

        scan_id = str(uuid.uuid4())
        db = Database.get_db()

        # Record scan start
        scan_doc = {
            "scan_id": scan_id,
            "status": "in_progress",
            "duration": duration,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "networks_found": 0,
            "threats_detected": 0,
        }
        if db is not None:
            db["scans"].insert_one(scan_doc)

        socketio.emit("scan_status", {
            "scan_id": scan_id,
            "status": "in_progress",
            "duration": duration,
        }, broadcast=True)

        # Run scan in background
        def _run():
            try:
                scanner = _get_scanner()
                networks = scanner.scan(duration=duration)

                completed_at = datetime.now(timezone.utc).isoformat()

                if db is not None:
                    # Save networks
                    for net in networks:
                        try:
                            db["networks"].update_one(
                                {"bssid": net["bssid"]},
                                {"$set": net},
                                upsert=True,
                            )
                        except Exception:
                            pass

                    # Update scan record
                    db["scans"].update_one(
                        {"scan_id": scan_id},
                        {"$set": {
                            "status": "completed",
                            "completed_at": completed_at,
                            "networks_found": len(networks),
                            "results": {"networks": networks},
                        }},
                    )

                socketio.emit("scan_status", {
                    "scan_id": scan_id,
                    "status": "completed",
                    "networks_found": len(networks),
                    "completed_at": completed_at,
                }, broadcast=True)

            except Exception as exc:
                logger.error("Scan %s failed: %s", scan_id, exc)
                if db is not None:
                    db["scans"].update_one(
                        {"scan_id": scan_id},
                        {"$set": {
                            "status": "failed",
                            "error": str(exc),
                        }},
                    )
                socketio.emit("scan_status", {
                    "scan_id": scan_id,
                    "status": "failed",
                    "error": str(exc),
                }, broadcast=True)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        return jsonify({
            "scan_id": scan_id,
            "status": "started",
            "message": f"Scan started for {duration} seconds",
        }), 200

    except Exception as exc:
        logger.error("start_scan error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@scan_bp.route("/quick", methods=["POST"])
def quick_scan():
    """Run a quick synchronous scan and return results immediately."""
    try:
        scanner = _get_scanner()
        networks = scanner.scan(duration=5)

        # Analyze for basic threats
        threats = _analyze_threats(networks)

        # Save to DB
        db = Database.get_db()
        scan_id = str(uuid.uuid4())
        if db is not None:
            db["scans"].insert_one({
                "scan_id": scan_id,
                "status": "completed",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "networks_found": len(networks),
                "threats_detected": len(threats),
            })

        return jsonify({
            "scan_id": scan_id,
            "networks": networks,
            "threats": threats,
            "summary": {
                "total_networks": len(networks),
                "threats_detected": len(threats),
                "scan_method": scanner.scan_method,
            },
        }), 200

    except Exception as exc:
        logger.error("quick_scan error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@scan_bp.route("/interfaces", methods=["GET"])
def get_interfaces():
    """Get available WiFi scanning method and status."""
    try:
        scanner = _get_scanner()
        return jsonify({
            "scan_method": scanner.scan_method,
            "platform": __import__("platform").system(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@scan_bp.route("/status/<scan_id>", methods=["GET"])
def get_scan_status(scan_id):
    """Get scan status by ID."""
    try:
        db = Database.get_db()
        if db is None:
            return jsonify({"error": "Database not connected"}), 503

        scan = db["scans"].find_one({"scan_id": scan_id})
        if not scan:
            return jsonify({"error": "Scan not found"}), 404

        scan.pop("_id", None)
        return jsonify(scan), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@scan_bp.route("/results/<scan_id>", methods=["GET"])
def get_scan_results(scan_id):
    """Get completed scan results."""
    try:
        db = Database.get_db()
        if db is None:
            return jsonify({"error": "Database not connected"}), 503

        scan = db["scans"].find_one({"scan_id": scan_id})
        if not scan:
            return jsonify({"error": "Scan not found"}), 404

        if scan.get("status") != "completed":
            return jsonify({
                "error": "Scan not completed",
                "status": scan.get("status"),
            }), 400

        return jsonify({
            "scan_id": scan_id,
            "networks": scan.get("results", {}).get("networks", []),
            "summary": {
                "total_networks": scan.get("networks_found", 0),
                "threats_detected": scan.get("threats_detected", 0),
            },
        }), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@scan_bp.route("/history", methods=["GET"])
def get_scan_history():
    """Get recent scan history."""
    try:
        db = Database.get_db()
        if db is None:
            return jsonify({"error": "Database not connected"}), 503

        limit = request.args.get("limit", 10, type=int)
        scans = list(db["scans"].find().sort("started_at", -1).limit(limit))

        for s in scans:
            s.pop("_id", None)
            # Remove heavy results data from history listing
            s.pop("results", None)

        return jsonify({"scans": scans, "count": len(scans)}), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def _analyze_threats(networks):
    """Quick rule-based threat analysis."""
    threats = []
    ssid_map = {}

    for net in networks:
        ssid = net.get("ssid", "")
        if ssid and ssid not in ("[Hidden]", ""):
            ssid_map.setdefault(ssid, []).append(net)

    for ssid, nets in ssid_map.items():
        if len(nets) > 1:
            for net in nets:
                threats.append({
                    "bssid": net["bssid"],
                    "ssid": ssid,
                    "threat_type": "evil_twin",
                    "confidence": 0.7,
                    "reason": f"Duplicate SSID ({len(nets)} APs)",
                })

    for net in networks:
        if net.get("encryption") in ("Open", "WEP", "None", ""):
            threats.append({
                "bssid": net["bssid"],
                "ssid": net.get("ssid"),
                "threat_type": "weak_encryption",
                "confidence": 0.6,
                "reason": f"Weak encryption: {net.get('encryption', 'Open')}",
            })

    return threats
