from flask import Blueprint, request, jsonify
from services.ml_trainer import MLTrainer
from models.database import Database
from datetime import datetime
import threading
import uuid

training_bp = Blueprint('training', __name__, url_prefix='/api/training')

# Track training jobs
training_jobs = {}

@training_bp.route('/start', methods=['POST'])
def start_training():
    """Start model training"""
    try:
        job_id = str(uuid.uuid4())
        
        def train_models():
            try:
                training_jobs[job_id] = {
                    "status": "in_progress",
                    "started_at": datetime.utcnow().isoformat(),
                    "progress": 0
                }
                
                trainer = MLTrainer()
                
                # Run training
                results = trainer.train_full_pipeline()
                
                # Save results to database
                db = Database.get_db()
                
                for model_type, model_data in results["models"].items():
                    model_doc = {
                        "model_name": f"{model_type}_{results['timestamp']}",
                        "model_type": model_type,
                        "version": results['timestamp'],
                        "accuracy": model_data.get("metrics", {}).get("accuracy", 0),
                        "precision": model_data.get("metrics", {}).get("precision", 0),
                        "recall": model_data.get("metrics", {}).get("recall", 0),
                        "f1_score": model_data.get("metrics", {}).get("f1_score", 0),
                        "training_samples": results["training_samples"],
                        "test_samples": results["test_samples"],
                        "created_at": datetime.utcnow().isoformat(),
                        "model_path": model_data.get("path"),
                        "feature_importance": model_data.get("feature_importance", {})
                    }
                    db['models'].insert_one(model_doc)
                
                training_jobs[job_id] = {
                    "status": "completed",
                    "started_at": training_jobs[job_id]["started_at"],
                    "completed_at": datetime.utcnow().isoformat(),
                    "results": results,
                    "progress": 100
                }
                
            except Exception as e:
                training_jobs[job_id] = {
                    "status": "failed",
                    "error": str(e),
                    "started_at": training_jobs[job_id]["started_at"],
                    "failed_at": datetime.utcnow().isoformat(),
                    "progress": 0
                }
        
        # Start training in background
        thread = threading.Thread(target=train_models, daemon=True)
        thread.start()
        
        return jsonify({
            "job_id": job_id,
            "message": "Training started",
            "status": "queued",
            "timestamp": datetime.utcnow().isoformat()
        }), 202
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/status/<job_id>', methods=['GET'])
def get_training_status(job_id):
    """Get training job status"""
    try:
        if job_id not in training_jobs:
            return jsonify({"error": "Job not found"}), 404
        
        return jsonify({
            "job_id": job_id,
            **training_jobs[job_id],
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/history', methods=['GET'])
def get_training_history():
    """Get training history"""
    try:
        db = Database.get_db()
        
        limit = request.args.get('limit', 20, type=int)
        trainings = list(db['models'].find({}).sort("created_at", -1).limit(limit))
        
        for training in trainings:
            training.pop('_id', None)
        
        return jsonify({
            "trainings": trainings,
            "count": len(trainings),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/data/add', methods=['POST'])
def add_training_data():
    """Add new training data"""
    try:
        data = request.get_json()
        
        features = data.get('features')
        label = data.get('label')  # 'evil_twin' or 'legitimate'
        confidence = data.get('confidence', 0.9)
        
        if not features or not label:
            return jsonify({"error": "Features and label required"}), 400
        
        db = Database.get_db()
        
        training_doc = {
            "features": features,
            "label": label,
            "confidence": confidence,
            "source": "manual",
            "timestamp": datetime.utcnow().isoformat(),
            "validated": False
        }
        
        result = db['training_data'].insert_one(training_doc)
        
        return jsonify({
            "message": "Training data added",
            "id": str(result.inserted_id),
            "timestamp": datetime.utcnow().isoformat()
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/data/list', methods=['GET'])
def list_training_data():
    """List training data"""
    try:
        db = Database.get_db()
        
        limit = request.args.get('limit', 100, type=int)
        label = request.args.get('label')
        validated = request.args.get('validated', type=lambda x: x.lower() == 'true')
        
        query = {}
        if label:
            query['label'] = label
        if validated is not None:
            query['validated'] = validated
        
        data = list(db['training_data'].find(query).sort("timestamp", -1).limit(limit))
        
        for doc in data:
            doc.pop('_id', None)
        
        stats = {
            "total": db['training_data'].count_documents({}),
            "by_label": {
                "evil_twin": db['training_data'].count_documents({"label": "evil_twin"}),
                "legitimate": db['training_data'].count_documents({"label": "legitimate"})
            }
        }
        
        return jsonify({
            "data": data,
            "statistics": stats,
            "count": len(data),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/data/validate/<data_id>', methods=['PUT'])
def validate_training_data(data_id):
    """Validate training data"""
    try:
        from bson import ObjectId
        
        db = Database.get_db()
        
        result = db['training_data'].update_one(
            {"_id": ObjectId(data_id)},
            {"$set": {"validated": True, "validated_at": datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Data not found"}), 404
        
        return jsonify({
            "message": "Data validated",
            "id": data_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/recommendations', methods=['GET'])
def get_training_recommendations():
    """Get recommendations for model improvement"""
    try:
        db = Database.get_db()
        
        recommendations = {
            "data_insights": {},
            "model_suggestions": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check data balance
        evil_twin_count = db['training_data'].count_documents({"label": "evil_twin"})
        legit_count = db['training_data'].count_documents({"label": "legitimate"})
        total_data = evil_twin_count + legit_count
        
        recommendations["data_insights"] = {
            "total_samples": total_data,
            "evil_twin_samples": evil_twin_count,
            "legitimate_samples": legit_count,
            "balance_ratio": f"{evil_twin_count}:{legit_count}" if legit_count > 0 else "0:0"
        }
        
        # Recommendations
        if total_data < 1000:
            recommendations["model_suggestions"].append(
                "Increase training data. Current samples are below recommended minimum (1000)"
            )
        
        if legit_count < evil_twin_count * 0.5:
            recommendations["model_suggestions"].append(
                "Imbalanced dataset. Add more legitimate network samples for better model accuracy"
            )
        
        if evil_twin_count < legit_count * 0.5:
            recommendations["model_suggestions"].append(
                "Imbalanced dataset. Add more evil twin/threat samples"
            )
        
        if not recommendations["model_suggestions"]:
            recommendations["model_suggestions"].append("Dataset looks well-balanced. Ready for training!")
        
        return jsonify(recommendations), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
