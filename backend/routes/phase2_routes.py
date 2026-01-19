from flask import Blueprint, jsonify
from services.phase2_feature_extractor import Phase2FeatureExtractor
from models.database import Database

phase2_bp = Blueprint('phase2', __name__, url_prefix='/api/phase2')

@phase2_bp.route('/run', methods=['POST'])
def run_phase2():
    """
    Trigger Phase 2 feature extraction manually.
    """
    try:
        extractor = Phase2FeatureExtractor()
        extractor.run()
        return jsonify({"status": "success", "message": "Phase 2 feature extraction completed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@phase2_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about generated baselines.
    """
    try:
        db = Database.get_db()
        count = db.features_baseline.count_documents({})
        
        # Get last update timestamp
        last_update = None
        if count > 0:
            latest = db.features_baseline.find_one(sort=[("updated_at", -1)])
            if latest:
                last_update = latest.get("updated_at")

        return jsonify({
            "baseline_count": count,
            "last_updated": last_update
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
