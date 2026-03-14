"""
Pipeline Routes — Full Detection Pipeline API
---
Exposes the complete training + detection pipeline as REST endpoints.
"""

import logging
import traceback

from flask import Blueprint, jsonify, request
from models.database import Database
from datetime import datetime, timezone

logger = logging.getLogger("netguard.routes.pipeline")

pipeline_bp = Blueprint("pipeline_bp", __name__, url_prefix="/api/pipeline")


@pipeline_bp.route("/run", methods=["POST"])
def run_full_pipeline():
    """
    Run the full training + detection pipeline.
    Returns all detected threats (not just suspicious).
    """
    try:
        from train_models import train_models, run_detection_pipeline

        db = Database.get_db()
        if db is None:
            return jsonify({"error": "Database not connected"}), 503

        # Parse options
        data = request.get_json(silent=True) or {}
        scan_duration = data.get("scan_duration", 3)
        skip_training = data.get("skip_training", False)
        clear_data = data.get("clear_data", True) # Default to fresh scan

        if clear_data:
            logger.info("Pipeline: clearing old raw scans and baseline features...")
            db["raw_scans"].delete_many({})
            db["features_baseline"].delete_many({})

        # STEP 1: Train models (unless skipped)
        if not skip_training:
            logger.info("Pipeline: training models...")
            if not train_models():
                return jsonify({
                    "status": "error",
                    "message": "Model training failed",
                }), 500

        # STEP 2: Run detection pipeline
        logger.info("Pipeline: running detection (scan=%ds)...", scan_duration)
        if not run_detection_pipeline(scan_duration=scan_duration):
            return jsonify({
                "status": "error",
                "message": "Detection pipeline failed",
            }), 500

        # STEP 3: Fetch all threats (not just suspicious)
        threats = list(
            db["threats"].find(
                {},
                {"_id": 0},
            ).sort("confidence", -1)
        )

        # Summary stats
        verdict_counts = {"danger": 0, "suspicious": 0, "safe": 0}
        total_confidence = 0
        methodology_counts = {"signature": 0, "behavior": 0, "ml": 0}

        for t in threats:
            v = t.get("verdict", "unknown")
            if v in ["confirmed_evil_twin", "likely_evil_twin"]:
                verdict_counts["danger"] += 1
            elif v == "suspicious":
                verdict_counts["suspicious"] += 1
            else:
                verdict_counts["safe"] += 1
            
            total_confidence += t.get("confidence", 0)
            
            # Aggregate methodology scores
            layer_scores = t.get("layer_scores", {})
            methodology_counts["signature"] += layer_scores.get("signature", 0)
            methodology_counts["behavior"] += layer_scores.get("behavior", 0)
            methodology_counts["ml"] += layer_scores.get("ml", 0)

        avg_confidence = total_confidence / len(threats) if threats else 0

        return jsonify({
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(threats),
            "summary": {
                **verdict_counts,
                "avg_confidence": avg_confidence,
                "methodology_averages": {
                    k: (v / len(threats) * 100) if threats else 0 
                    for k, v in methodology_counts.items()
                }
            },
            "data": threats,
        }), 200

    except Exception as exc:
        logger.error("Pipeline error: %s", exc, exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(exc),
            "traceback": traceback.format_exc() if logger.isEnabledFor(logging.DEBUG) else None,
        }), 500


@pipeline_bp.route("/quick-scan", methods=["POST"])
def quick_scan():
    """
    Quick scan: skip training, just scan + detect using existing models.
    """
    try:
        from train_models import run_detection_pipeline

        db = Database.get_db()
        if db is None:
            return jsonify({"error": "Database not connected"}), 503

        data = request.get_json(silent=True) or {}
        scan_duration = data.get("scan_duration", 3)

        if not run_detection_pipeline(scan_duration=scan_duration):
            return jsonify({
                "status": "error",
                "message": "Quick scan failed",
            }), 500

        threats = list(
            db["threats"].find({}, {"_id": 0}).sort("confidence", -1)
        )

        return jsonify({
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(threats),
            "data": threats,
        }), 200

    except Exception as exc:
        logger.error("Quick scan error: %s", exc, exc_info=True)
        return jsonify({"status": "error", "message": str(exc)}), 500
