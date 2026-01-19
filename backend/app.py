from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime
from socket_server import socketio

load_dotenv()

app = Flask(__name__)
CORS(app)

socketio.init_app(
    app,
    cors_allowed_origins="*"
)

# MongoDB connection
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGODB_DB", "netguard")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    client.admin.command("ping")
    print("Connected to MongoDB successfully")
except ConnectionFailure:
    print("Failed to connect to MongoDB")
    db = None

# Import routes AFTER app + socketio init
from routes.scan_routes import scan_bp
from routes.detection_routes import detection_bp
from routes.logs_routes import logs_bp
from routes.model_routes import model_bp
from routes.training_routes import training_bp

# Register blueprints
app.register_blueprint(scan_bp)
app.register_blueprint(detection_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(model_bp)
app.register_blueprint(training_bp)

from routes.phase2_routes import phase2_bp
app.register_blueprint(phase2_bp)

# Health check
@app.route("/health", methods=["GET"])
def health():
    mongo_status = "connected" if db else "disconnected"
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mongodb": mongo_status
    }), 200

# System info
@app.route("/api/system/info", methods=["GET"])
def system_info():
    import psutil
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ✅ MUST use socketio.run (NOT app.run)
if __name__ == "__main__":
    socketio.run(
        app,
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=True,
        use_reloader=False
    )
