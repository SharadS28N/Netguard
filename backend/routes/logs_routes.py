from flask import Blueprint, request, jsonify
from models.database import Database
from datetime import datetime, timedelta

logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')

@logs_bp.route('/detection', methods=['GET'])
def get_detection_logs():
    """Get detection logs with filtering"""
    try:
        db = Database.get_db()
        
        # Query parameters
        limit = request.args.get('limit', 50, type=int)
        threat_level = request.args.get('threat_level')
        hours = request.args.get('hours', 24, type=int)
        
        # Build query
        query = {}
        if threat_level and threat_level != 'all':
            query["threat_level"] = threat_level
        
        # Filter by time
        since = datetime.utcnow() - timedelta(hours=hours)
        query["timestamp"] = {"$gte": since.isoformat()}
        
        # Get logs
        logs = list(db['detection_logs'].find(query).sort("timestamp", -1).limit(limit))
        
        for log in logs:
            log.pop('_id', None)
        
        return jsonify({
            "logs": logs,
            "count": len(logs),
            "filters": {
                "threat_level": threat_level,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@logs_bp.route('/threats', methods=['GET'])
def get_threat_logs():
    """Get threat detection logs"""
    try:
        db = Database.get_db()
        
        limit = request.args.get('limit', 100, type=int)
        threat_type = request.args.get('threat_type')
        
        query = {}
        if threat_type:
            query["threat_type"] = threat_type
        
        threats = list(db['threats'].find(query).sort("timestamp", -1).limit(limit))
        
        for threat in threats:
            threat.pop('_id', None)
        
        # Statistics
        stats = {
            "total_threats": db['threats'].count_documents({}),
            "threat_types": {}
        }
        
        for threat in threats:
            threat_type = threat.get('threat_type', 'unknown')
            stats["threat_types"][threat_type] = stats["threat_types"].get(threat_type, 0) + 1
        
        return jsonify({
            "threats": threats,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@logs_bp.route('/network', methods=['GET'])
def get_network_logs():
    """Get network discovery logs"""
    try:
        db = Database.get_db()
        
        limit = request.args.get('limit', 100, type=int)
        encryption = request.args.get('encryption')
        
        query = {}
        if encryption:
            query["encryption"] = encryption
        
        networks = list(db['networks'].find(query).sort("timestamp", -1).limit(limit))
        
        for network in networks:
            network.pop('_id', None)
        
        return jsonify({
            "networks": networks,
            "count": len(networks),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@logs_bp.route('/export', methods=['GET'])
def export_logs():
    """Export logs as JSON"""
    try:
        db = Database.get_db()
        
        export_type = request.args.get('type', 'detection')  # detection, threats, networks
        hours = request.args.get('hours', 24, type=int)
        
        since = datetime.utcnow() - timedelta(hours=hours)
        query = {"timestamp": {"$gte": since.isoformat()}}
        
        if export_type == 'detection':
            logs = list(db['detection_logs'].find(query))
        elif export_type == 'threats':
            logs = list(db['threats'].find(query))
        elif export_type == 'networks':
            logs = list(db['networks'].find(query))
        else:
            return jsonify({"error": "Invalid export type"}), 400
        
        for log in logs:
            log.pop('_id', None)
        
        return jsonify({
            "export_type": export_type,
            "records": logs,
            "count": len(logs),
            "exported_at": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@logs_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get statistics from logs"""
    try:
        db = Database.get_db()
        
        hours = request.args.get('hours', 24, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        stats = {
            "total_scans": db['scans'].count_documents({}),
            "total_networks": db['networks'].count_documents({}),
            "total_threats": db['threats'].count_documents({}),
            "total_detections": db['detection_logs'].count_documents({}),
            "recent_scans": db['scans'].count_documents({"started_at": {"$gte": since.isoformat()}}),
            "threat_levels": {},
            "threat_types": {},
            "encryption_stats": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Threat level distribution
        for level in ['critical', 'high', 'medium', 'low']:
            stats["threat_levels"][level] = db['threats'].count_documents({"threat_level": level})
        
        # Threat type distribution
        threats = db['threats'].find({})
        for threat in threats:
            threat_type = threat.get('threat_type', 'unknown')
            stats["threat_types"][threat_type] = stats["threat_types"].get(threat_type, 0) + 1
        
        # Encryption distribution
        networks = db['networks'].find({})
        for network in networks:
            enc = network.get('encryption', 'unknown')
            stats["encryption_stats"][enc] = stats["encryption_stats"].get(enc, 0) + 1
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@logs_bp.route('/clear', methods=['POST'])
def clear_logs():
    """Clear old logs (older than specified hours)"""
    try:
        db = Database.get_db()
        
        data = request.get_json()
        hours = data.get('hours', 168)  # Default 1 week
        
        before = datetime.utcnow() - timedelta(hours=hours)
        query = {"timestamp": {"$lt": before.isoformat()}}
        
        # Delete from collections
        detection_result = db['detection_logs'].delete_many(query)
        threat_result = db['threats'].delete_many(query)
        network_result = db['networks'].delete_many(query)
        
        return jsonify({
            "message": f"Logs older than {hours} hours cleared",
            "deleted": {
                "detection_logs": detection_result.deleted_count,
                "threats": threat_result.deleted_count,
                "networks": network_result.deleted_count
            },
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
