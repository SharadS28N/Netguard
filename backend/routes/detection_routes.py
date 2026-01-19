from flask import Blueprint, request, jsonify
from services.ml_inference import MLInference
from models.database import Database
from datetime import datetime
import uuid
from socket_server import socketio

detection_bp = Blueprint('detection', __name__, url_prefix='/api/detection')

# Global inference engine
inference_engine = None

def get_inference_engine():
    """Get or create inference engine"""
    global inference_engine
    if inference_engine is None:
        inference_engine = MLInference()
        inference_engine.load_models()
    return inference_engine

@detection_bp.route('/predict', methods=['POST'])
def predict_threat():
    """Predict threat for given networks"""
    try:
        data = request.get_json()
        networks = data.get('networks', [])
        
        if not networks:
            return jsonify({"error": "No networks provided"}), 400
        
        engine = get_inference_engine()
        
        if not engine.model_loaded:
            return jsonify({
                "error": "ML models not loaded",
                "info": engine.get_model_info()
            }), 503
        
        # Get known networks for context
        db = Database.get_db()
        known_networks = list(db['networks'].find().limit(100))
        for net in known_networks:
            net.pop('_id', None)
        
        # Run predictions
        predictions = engine.predict_batch(networks, known_networks)
        
        # Save predictions to database
        detection_log = {
            "detection_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "networks_analyzed": len(networks),
            "predictions": predictions,
            "model_info": engine.get_model_info()
        }
        db['detection_logs'].insert_one(detection_log)
        socketio.emit(
            'detection_result',
            detection_log,
            broadcast=True
        )
        return jsonify(predictions), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@detection_bp.route('/report', methods=['POST'])
def generate_report():
    """Generate detailed threat detection report"""
    try:
        data = request.get_json()
        networks = data.get('networks', [])
        threats = data.get('threats', [])
        
        engine = get_inference_engine()
        report = engine.detection_report(networks, threats)
        
        # Save report to database
        db = Database.get_db()
        report_doc = {
            "report_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "report": report
        }
        db['detection_logs'].insert_one(report_doc)
        
        return jsonify(report), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@detection_bp.route('/models/info', methods=['GET'])
def get_models_info():
    """Get information about loaded models"""
    try:
        engine = get_inference_engine()
        info = engine.get_model_info()
        
        return jsonify({
            "models": info,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@detection_bp.route('/models/reload', methods=['POST'])
def reload_models():
    """Reload models from disk"""
    global inference_engine
    
    try:
        inference_engine = MLInference()
        success = inference_engine.load_models()
        
        if success:
            return jsonify({
                "message": "Models reloaded successfully",
                "info": inference_engine.get_model_info(),
                "timestamp": datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Failed to reload models",
                "timestamp": datetime.utcnow().isoformat()
            }), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@detection_bp.route('/history', methods=['GET'])
def get_detection_history():
    """Get detection history"""
    try:
        db = Database.get_db()
        limit = request.args.get('limit', 50, type=int)
        threat_level = request.args.get('threat_level')
        
        query = {}
        if threat_level:
            query["report.threat_analysis.by_level"] = threat_level
        
        detections = list(db['detection_logs'].find(query).sort("timestamp", -1).limit(limit))
        
        for det in detections:
            det.pop('_id', None)
        
        return jsonify({
            "detections": detections,
            "count": len(detections),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
