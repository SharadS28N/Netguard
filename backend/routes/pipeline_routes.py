from flask import Blueprint, jsonify
from models.database import Database
from train_models import train_models, run_detection_pipeline
import traceback

# Create Blueprint
pipeline_bp = Blueprint(
    "pipeline_bp",
    __name__,
    url_prefix="/api/pipeline"
)

@pipeline_bp.route("/run", methods=["POST"])
def run_full_pipeline():
    """
    Runs the full training + detection pipeline
    and returns ONLY suspicious threats.
    """
    try:
        # Get database
        db = Database.get_db()
        if db is None:
            return jsonify({"error": "Database not connected"}), 500


        # STEP 1: Train models
        train_ok = train_models()
        if not train_ok:
            return jsonify({"error": "Model training failed"}), 500

        # STEP 2: Run detection pipeline (Phase 1 → Phase 4)
        detect_ok = run_detection_pipeline()
        if not detect_ok:
            return jsonify({"error": "Detection pipeline failed"}), 500

        # STEP 3: Fetch ONLY suspicious threats
        threats_col = db["threats"]

        suspicious = list(
            threats_col.find(
                {"verdict": "suspicious"},
                {"_id": 0}  # hide Mongo ObjectId
            )
        )

        return jsonify({
            "status": "success",
            "count": len(suspicious),
            "data": suspicious
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
