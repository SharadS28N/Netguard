from flask import Blueprint, request, jsonify
from services.ml_inference import MLInference
from models.database import Database
from datetime import datetime
import os

model_bp = Blueprint('model', __name__, url_prefix='/api/models')

@model_bp.route('/list', methods=['GET'])
def list_models():
    """List all available models"""
    try:
        models_dir = "./models"
        models = []
        
        if os.path.exists(models_dir):
            for filename in os.listdir(models_dir):
                if filename.endswith('.pkl'):
                    filepath = os.path.join(models_dir, filename)
                    file_size = os.path.getsize(filepath)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    models.append({
                        "filename": filename,
                        "size_kb": round(file_size / 1024, 2),
                        "created": file_mtime.isoformat(),
                        "path": filepath
                    })
        
        return jsonify({
            "models": sorted(models, key=lambda x: x['created'], reverse=True),
            "count": len(models),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_bp.route('/status', methods=['GET'])
def get_model_status():
    """Get current model status"""
    try:
        engine = MLInference()
        engine.load_models()
        
        status = engine.get_model_info()
        
        return jsonify({
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_bp.route('/performance', methods=['GET'])
def get_model_performance():
    """Get model performance metrics"""
    try:
        db = Database.get_db()
        
        # Get performance metrics from database
        models_collection = db['models'].find({})
        models_list = []
        
        for model in models_collection:
            model.pop('_id', None)
            models_list.append(model)
        
        if not models_list:
            return jsonify({
                "message": "No model metrics found",
                "models": []
            }), 200
        
        return jsonify({
            "models": sorted(models_list, key=lambda x: x.get('created_at', ''), reverse=True),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_bp.route('/features', methods=['GET'])
def get_model_features():
    """Get feature information"""
    try:
        features = {
            "input_features": [
                {
                    "name": "signal_strength",
                    "description": "WiFi signal strength in dBm",
                    "range": "-100 to -30",
                    "type": "numerical"
                },
                {
                    "name": "channel_variance",
                    "description": "Channel stability variance",
                    "range": "0 to 100",
                    "type": "numerical"
                },
                {
                    "name": "encryption_type",
                    "description": "Encryption protocol",
                    "values": ["Open (0)", "WEP (1)", "WPA (2)", "WPA2 (3)"],
                    "type": "categorical"
                },
                {
                    "name": "vendor_consistency",
                    "description": "MAC vendor consistency score",
                    "range": "0 to 1",
                    "type": "numerical"
                },
                {
                    "name": "behavior_anomaly",
                    "description": "Network behavior anomaly score",
                    "range": "0 to 1",
                    "type": "numerical"
                },
                {
                    "name": "traffic_pattern",
                    "description": "Traffic pattern anomaly",
                    "range": "0 to 1",
                    "type": "numerical"
                },
                {
                    "name": "client_count",
                    "description": "Number of connected clients",
                    "range": "0 to 50+",
                    "type": "numerical"
                },
                {
                    "name": "ssid_similarity",
                    "description": "Similarity to known SSIDs",
                    "range": "0 to 1",
                    "type": "numerical"
                }
            ],
            "output_classes": [
                {
                    "name": "Legitimate",
                    "value": 0,
                    "description": "Network appears to be legitimate"
                },
                {
                    "name": "Suspicious/Evil Twin",
                    "value": 1,
                    "description": "Network appears to be a threat"
                }
            ]
        }
        
        return jsonify(features), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_bp.route('/compare', methods=['GET'])
def compare_models():
    """Compare different model types"""
    try:
        db = Database.get_db()
        models = list(db['models'].find({}))
        
        comparison = {
            "models": [],
            "best_by_metric": {
                "accuracy": None,
                "precision": None,
                "recall": None,
                "f1_score": None
            }
        }
        
        for model in models:
            model.pop('_id', None)
            comparison["models"].append(model)
            
            # Track best models
            if comparison["best_by_metric"]["accuracy"] is None or \
               model.get("accuracy", 0) > comparison["best_by_metric"]["accuracy"]:
                comparison["best_by_metric"]["accuracy"] = model.get("model_name")
        
        return jsonify({
            "comparison": comparison,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
