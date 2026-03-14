"""
Netguard Configuration Module
---
Environment-based configuration for development, testing, and production.
"""

import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration shared across all environments."""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", 5001))

    # MongoDB
    MONGODB_URI = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://REPLACE_USER:REPLACE_PASSWORD@REPLACE_CLUSTER.mongodb.net/?retryWrites=true&w=majority",
    )
    MONGODB_DB = os.getenv("MONGODB_DB", "netguard")

    # Paths
    MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    # Detection thresholds
    EVIL_TWIN_THRESHOLD = 0.60
    HIGH_THREAT_THRESHOLD = 0.80

    # Scanning
    DEFAULT_SCAN_DURATION = 10  # seconds
    MAX_SCAN_DURATION = 60

    # CORS
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    DEBUG = True
    ENVIRONMENT = "development"


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    DEBUG = False
    ENVIRONMENT = "production"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    DEBUG = True
    TESTING = True
    ENVIRONMENT = "testing"
    MONGODB_DB = "netguard_test"


def get_config():
    """Return the correct config based on ENVIRONMENT env var."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    return configs.get(env, DevelopmentConfig)()


# Validate critical config on import
def validate_config(config):
    """Validate that required configuration values are set."""
    issues = []
    if "REPLACE_" in config.MONGODB_URI:
        issues.append(
            "MONGODB_URI contains placeholder values. "
            "Set your MongoDB Atlas URI in backend/.env"
        )
    if config.SECRET_KEY == "netguard-change-this-in-production-2026":
        issues.append("SECRET_KEY is using the default value. Change it in .env")
    return issues