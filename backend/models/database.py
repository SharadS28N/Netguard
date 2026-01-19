from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from datetime import datetime

class Database:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        """Connect to MongoDB"""
        try:
            uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
            dbname = os.getenv('MONGODB_DB', 'netguard')
            cls._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            cls._db = cls._client[dbname]
            cls._client.admin.command('ping')
            print("Database connected successfully")
            cls.create_collections()
            return True
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False

    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            cls.connect()
        return cls._db

    @classmethod
    def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls._client:
            cls._client.close()

    @classmethod
    def create_collections(cls):
        """Create collections with schema validation"""
        db = cls.get_db()

        # Networks collection
        if 'networks' not in db.list_collection_names():
            db.create_collection('networks')
            db['networks'].create_index('bssid', unique=True)
            db['networks'].create_index('timestamp')
            print("Created 'networks' collection")

        # Threats collection
        if 'threats' not in db.list_collection_names():
            db.create_collection('threats')
            db['threats'].create_index('network_id')
            db['threats'].create_index('timestamp')
            db['threats'].create_index('threat_type')
            print("Created 'threats' collection")

        # Scans collection
        if 'scans' not in db.list_collection_names():
            db.create_collection('scans')
            db['scans'].create_index('timestamp')
            db['scans'].create_index('status')
            print("Created 'scans' collection")

        # Detection logs collection
        if 'detection_logs' not in db.list_collection_names():
            db.create_collection('detection_logs')
            db['detection_logs'].create_index('timestamp')
            db['detection_logs'].create_index('threat_level')
            db['detection_logs'].create_index('scan_id')
            print("Created 'detection_logs' collection")

        # ML models collection
        if 'models' not in db.list_collection_names():
            db.create_collection('models')
            db['models'].create_index('model_name', unique=True)
            db['models'].create_index('created_at')
            print("Created 'models' collection")

        # Training data collection
        if 'training_data' not in db.list_collection_names():
            db.create_collection('training_data')
            db['training_data'].create_index('timestamp')
            db['training_data'].create_index('label')
            print("Created 'training_data' collection")

# Schema definitions
NETWORK_SCHEMA = {
    "bssid": str,  # MAC address
    "ssid": str,
    "channel": int,
    "signal_strength": int,  # dBm
    "frequency": str,
    "encryption": str,
    "is_hidden": bool,
    "vendor": str,
    "client_count": int,
    "timestamp": str,
    "location": {
        "latitude": float,
        "longitude": float
    }
}

THREAT_SCHEMA = {
    "network_id": str,
    "threat_type": str,  # evil_twin, rogue_ap, known_attacker, suspicious
    "confidence": float,  # 0-1
    "threat_level": str,  # critical, high, medium, low
    "features": {},  # ML features used for detection
    "model_version": str,
    "timestamp": str,
    "details": str
}

SCAN_SCHEMA = {
    "scan_id": str,
    "scan_type": str,  # active, passive
    "duration": int,  # seconds
    "networks_found": int,
    "threats_detected": int,
    "status": str,  # completed, in_progress, failed
    "timestamp": str,
    "results": {
        "networks": [],
        "threats": [],
        "statistics": {}
    }
}

DETECTION_LOG_SCHEMA = {
    "scan_id": str,
    "event_type": str,
    "threat_level": str,
    "detection_result": {
        "overall_threat": str,
        "confidence_scores": {
            "signature": float,
            "behavior": float,
            "traffic": float,
            "ensemble": float
        },
        "networks": []
    },
    "timestamp": str
}

MODEL_SCHEMA = {
    "model_name": str,
    "model_type": str,  # random_forest, xgboost, neural_network, ensemble
    "version": str,
    "accuracy": float,
    "precision": float,
    "recall": float,
    "f1_score": float,
    "training_samples": int,
    "test_samples": int,
    "created_at": str,
    "updated_at": str,
    "features": [],
    "model_path": str
}

TRAINING_DATA_SCHEMA = {
    "features": {},
    "label": str,  # evil_twin, legitimate, unknown
    "source": str,
    "confidence": float,
    "timestamp": str,
    "validated": bool
}
