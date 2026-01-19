import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'netguard-secret-key-2026')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DB = os.getenv('MONGODB_DB', 'netguard')
    
    # Models
    MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    
    # Detection thresholds
    EVIL_TWIN_THRESHOLD = 0.60  # 60% confidence to flag as evil twin
    HIGH_THREAT_THRESHOLD = 0.80  # 80% is high threat
    
    # Scanning
    DEFAULT_SCAN_DURATION = 10  # seconds
    MAX_SCAN_DURATION = 60
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')