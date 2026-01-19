from flask import Blueprint, request, jsonify
from services.network_scanner import NetworkScanner
from models.database import Database
from datetime import datetime
import threading
import uuid
from socket_server import socketio

scan_bp = Blueprint('scan', __name__, url_prefix='/api/scan')

# Global scanner instance
scanner = None
current_scan = None

def get_scanner():
    """Get or create scanner instance"""
    global scanner
    if scanner is None:
        scanner = NetworkScanner()
    return scanner

@scan_bp.route('/interfaces', methods=['GET'])
def get_interfaces():
    """Get available network interfaces"""
    try:
        scanner = get_scanner()
        interfaces = scanner.get_available_interfaces()
        
        return jsonify({
            "interfaces": interfaces,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scan_bp.route('/start', methods=['POST'])
def start_scan():
    """Start network scan"""
    global current_scan
    
    try:
        data = request.get_json()
        interface = data.get('interface')
        duration = data.get('duration', 30)
        scan_type = data.get('scan_type', 'passive')  # passive or active
        
        if not interface:
            return jsonify({"error": "Interface not specified"}), 400
        
        # Create scan ID
        scan_id = str(uuid.uuid4())
        
        # Save scan to database
        db = Database.get_db()
        scan_doc = {
            "scan_id": scan_id,
            "interface": interface,
            "scan_type": scan_type,
            "duration": duration,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "networks_found": 0,
            "threats_detected": 0
        }
        db['scans'].insert_one(scan_doc)
        socketio.emit(
            'scan_status',
            {
                "scan_id": scan_id,
                "status": "in_progress",
                "interface": interface,
                "scan_type": scan_type,
                "duration": duration,
                "started_at": scan_doc["started_at"]
            },
            broadcast=True
        )
        
        # Run scan in background thread
        def run_scan():
            try:
                scanner = get_scanner()
                scanner.interface = interface
                
                if scan_type == 'active':
                    results = scanner.start_active_scan(interface, duration)
                else:
                    results = scanner.start_scan(interface, duration)
                
                # Analyze for threats
                threats = scanner.analyze_for_threats(results.get('networks', []))
                
                # Save results
                db['scans'].update_one(
                    {"scan_id": scan_id},
                    {"$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow().isoformat(),
                        "networks_found": len(results.get('networks', [])),
                        "threats_detected": len(threats),
                        "results": results,
                        "threats": threats
                    }}
                )
                socketio.emit(
                    'scan_status',
                    {
                        "scan_id": scan_id,
                        "status": "completed",
                        "networks_found": len(results.get('networks', [])),
                        "threats_detected": len(threats),
                        "completed_at": datetime.utcnow().isoformat()
                    },
                    broadcast=True
                )
                
            except Exception as e:
                print(f"Scan error: {e}")
                db['scans'].update_one(
                    {"scan_id": scan_id},
                    {"$set": {
                        "status": "failed",
                        "error": str(e),
                        "completed_at": datetime.utcnow().isoformat()
                    }}
                )
                socketio.emit(
                    'scan_status',
                    {
                        "scan_id": scan_id,
                        "status": "failed",
                        "error": str(e),
                        "completed_at": datetime.utcnow().isoformat()
                    },
                    broadcast=True
                )
        
        scan_thread = threading.Thread(target=run_scan, daemon=True)
        scan_thread.start()
        
        return jsonify({
            "scan_id": scan_id,
            "status": "started",
            "message": f"Scan started on {interface} for {duration} seconds",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scan_bp.route('/status/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    """Get scan status"""
    try:
        db = Database.get_db()
        scan = db['scans'].find_one({"scan_id": scan_id})
        
        if not scan:
            return jsonify({"error": "Scan not found"}), 404
        
        # Remove MongoDB ObjectId
        scan.pop('_id', None)
        
        return jsonify(scan), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scan_bp.route('/results/<scan_id>', methods=['GET'])
def get_scan_results(scan_id):
    """Get scan results"""
    try:
        db = Database.get_db()
        scan = db['scans'].find_one({"scan_id": scan_id})
        
        if not scan:
            return jsonify({"error": "Scan not found"}), 404
        
        if scan.get('status') != 'completed':
            return jsonify({
                "error": "Scan not completed",
                "status": scan.get('status')
            }), 400
        
        results = {
            "scan_id": scan_id,
            "networks": scan.get('results', {}).get('networks', []),
            "threats": scan.get('threats', []),
            "summary": {
                "total_networks": scan.get('networks_found', 0),
                "threats_detected": scan.get('threats_detected', 0),
                "scan_duration": scan.get('duration', 0),
                "timestamp": scan.get('completed_at')
            }
        }
        
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scan_bp.route('/history', methods=['GET'])
def get_scan_history():
    """Get recent scans"""
    try:
        db = Database.get_db()
        limit = request.args.get('limit', 10, type=int)
        
        scans = list(db['scans'].find().sort("started_at", -1).limit(limit))
        
        # Remove MongoDB ObjectIds
        for scan in scans:
            scan.pop('_id', None)
        
        return jsonify({
            "scans": scans,
            "count": len(scans),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scan_bp.route('/cancel/<scan_id>', methods=['POST'])
def cancel_scan(scan_id):
    """Cancel an ongoing scan"""
    try:
        db = Database.get_db()
        
        result = db['scans'].update_one(
            {"scan_id": scan_id, "status": "in_progress"},
            {"$set": {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow().isoformat()
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Scan not found or already completed"}), 404
        
        return jsonify({
            "message": "Scan cancelled",
            "scan_id": scan_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
