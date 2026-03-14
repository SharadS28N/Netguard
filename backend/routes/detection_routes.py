"""
Detection Routes — ML Prediction API
---
REST endpoints for ML-based threat detection and reporting.
"""

import logging
import uuid

from flask import Blueprint, request, jsonify
from services.ml_inference import MLInference
from models.database import Database
from datetime import datetime, timezone
from socket_server import socketio

logger = logging.getLogger("netguard.routes.detection")

detection_bp = Blueprint("detection", __name__, url_prefix="/api/detection")

# Singleton inference engine
_engine = None


def _get_engine() -> MLInference:
    """Get or create the singleton inference engine."""
    global _engine
    if _engine is None:
        _engine = MLInference()
        _engine.load_models()
    return _engine


@detection_bp.route("/predict", methods=["POST"])
def predict_threat():
    """Run ML prediction on provided networks."""
    try:
        data = request.get_json()
        networks = data.get("networks", [])

        if not networks:
            return jsonify({"error": "No networks provided"}), 400

        engine = _get_engine()
        if not engine.model_loaded:
            return jsonify({
                "error": "ML models not loaded. Train models first.",
                "info": engine.get_model_info(),
            }), 503

        db = Database.get_db()
        known_networks = []
        if db is not None:
            known_networks = list(db["networks"].find().limit(100))
            for net in known_networks:
                net.pop("_id", None)

        predictions = engine.predict_batch(networks, known_networks)

        # Save detection log (without ObjectId issues)
        if db is not None:
            detection_log = {
                "detection_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "networks_analyzed": len(networks),
                "predictions_summary": predictions.get("summary", {}),
            }
            db["detection_logs"].insert_one(detection_log)

            # Emit only safe data (no _id)
            socketio.emit("detection_result", {
                "detection_id": detection_log["detection_id"],
                "timestamp": detection_log["timestamp"],
                "summary": predictions.get("summary", {}),
            }, broadcast=True)

        return jsonify(predictions), 200

    except Exception as exc:
        logger.error("predict error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@detection_bp.route("/report", methods=["POST"])
def generate_report():
    """Generate detailed threat detection report."""
    try:
        data = request.get_json()
        networks = data.get("networks", [])
        threats = data.get("threats", [])

        engine = _get_engine()
        report = engine.detection_report(networks, threats)

        db = Database.get_db()
        if db is not None:
            db["detection_logs"].insert_one({
                "report_id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "report": report,
            })

        return jsonify(report), 200

    except Exception as exc:
        logger.error("report error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@detection_bp.route("/models/info", methods=["GET"])
def get_models_info():
    """Get info about loaded ML models."""
    try:
        engine = _get_engine()
        return jsonify({
            "models": engine.get_model_info(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@detection_bp.route("/models/reload", methods=["POST"])
def reload_models():
    """Force reload of ML models from disk."""
    global _engine
    try:
        _engine = MLInference()
        success = _engine.load_models()

        if success:
            return jsonify({
                "message": "Models reloaded successfully",
                "info": _engine.get_model_info(),
            }), 200
        else:
            return jsonify({"error": "Failed to reload models"}), 503

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@detection_bp.route("/history", methods=["GET"])
def get_detection_history():
    """Get detection history."""
    try:
        db = Database.get_db()
        if db is None:
            return jsonify({"error": "Database not connected"}), 503

        limit = request.args.get("limit", 50, type=int)
        detections = list(
            db["detection_logs"].find().sort("timestamp", -1).limit(limit)
        )

        for det in detections:
            det.pop("_id", None)

        return jsonify({
            "detections": detections,
            "count": len(detections),
        }), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
