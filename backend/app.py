from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime
from bson import ObjectId

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB connection
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGO_DB = os.getenv('MONGODB_DB', 'netguard')

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    client.admin.command('ping')
    print("Connected to MongoDB successfully")
except ConnectionFailure:
    print("Failed to connect to MongoDB")
    db = None

# Import routes
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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    mongo_status = "connected" if db else "disconnected"
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mongodb": mongo_status
    }), 200

@app.route('/api/system/info', methods=['GET'])
def system_info():
    """Get system information"""
    import psutil
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', True)
    )
