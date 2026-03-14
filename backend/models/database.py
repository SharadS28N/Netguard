"""
Netguard Database Module
---
Thread-safe MongoDB connection manager with Atlas support,
connection pooling, retry logic, and index management.
"""

import os
import time
import logging
from threading import Lock
from typing import Optional

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
)

logger = logging.getLogger("netguard.database")


class Database:
    """
    Thread-safe singleton MongoDB connection manager.

    Usage:
        db = Database.get_db()
        if db:
            db["collection"].find({})
    """

    _client: Optional[MongoClient] = None
    _db = None
    _uri: str = ""
    _db_name: str = ""
    _lock = Lock()

    # ─── Connection Lifecycle ────────────────────────────────

    @classmethod
    def connect(
        cls,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        max_retries: int = 3,
    ) -> bool:
        """
        Connect to MongoDB with retry logic. This method is thread-safe.

        Args:
            uri: MongoDB connection URI (defaults to env var)
            db_name: Database name (defaults to env var)
            max_retries: Number of connection attempts

        Returns:
            True if connected successfully
        """
        with cls._lock:
            if cls._client and cls.is_connected():
                logger.debug("Already connected to MongoDB.")
                return True

            cls._uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            cls._db_name = db_name or os.getenv("MONGODB_DB", "netguard")

            for attempt in range(1, max_retries + 1):
                try:
                    logger.info("MongoDB connection attempt %d/%d...", attempt, max_retries)

                    cls._client = MongoClient(
                        cls._uri,
                        serverSelectionTimeoutMS=10000,
                        connectTimeoutMS=10000,
                        socketTimeoutMS=20000,
                        maxPoolSize=50,
                        minPoolSize=5,
                        retryWrites=True,
                        retryReads=True,
                        tls="mongodb+srv" in cls._uri or "tls=true" in cls._uri.lower(),
                    )

                    # Verify connection
                    cls._client.admin.command("ping")
                    cls._db = cls._client[cls._db_name]

                    logger.info(
                        "Connected to MongoDB: %s (database: %s)",
                        cls._uri.split("@")[-1].split("/")[0] if "@" in cls._uri else "localhost",
                        cls._db_name,
                    )

                    # Create collections and indexes
                    cls._ensure_collections()
                    return True

                except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
                    wait = 2 ** attempt
                    logger.warning(
                        "Connection attempt %d failed: %s. Retrying in %ds...",
                        attempt,
                        exc,
                        wait,
                    )
                    if attempt < max_retries:
                        time.sleep(wait)
                    else:
                        logger.error("Failed to connect to MongoDB after %d attempts", max_retries)
                        cls._client = None # Ensure client is None on failure
                        cls._db = None
                        return False

                except Exception as exc:
                    logger.error("Unexpected database error during connection: %s", exc)
                    cls._client = None # Ensure client is None on failure
                    cls._db = None
                    return False
        return False

    @classmethod
    def get_db(cls):
        """
        Get the database instance. Auto-connects if needed in a thread-safe manner.
        """
        if cls._db is None:
            # Use a lock to ensure connect is only called once during initialization
            with cls._lock:
                # Double-check locking pattern
                if cls._db is None:
                    cls.connect()
        return cls._db

    @classmethod
    def disconnect(cls):
        """Gracefully close the MongoDB connection."""
        with cls._lock:
            if cls._client:
                cls._client.close()
                cls._client = None
                cls._db = None
                logger.info("MongoDB connection closed")

    @classmethod
    def is_connected(cls) -> bool:
        """Check if the database connection is alive."""
        if cls._client is None:
            return False
        try:
            cls._client.admin.command("ping")
            return True
        except ConnectionFailure:
            return False

    # ─── Collection & Index Management ───────────────────────

    @classmethod
    def _ensure_collections(cls):
        """Create collections and indexes if they don't exist."""
        if cls._db is None:
            logger.warning("Cannot ensure collections, database not connected.")
            return

        db = cls._db
        existing = set(db.list_collection_names())

        # Define collections and their indexes
        collection_indexes = {
            "networks": [
                ([("bssid", ASCENDING)], {"unique": True}),
                ([("timestamp", DESCENDING)], {}),
                ([("ssid", ASCENDING)], {}),
            ],
            "threats": [
                ([("ssid", ASCENDING), ("bssid", ASCENDING)], {}),
                ([("timestamp", DESCENDING)], {}),
                ([("threat_level", ASCENDING)], {}),
                ([("verdict", ASCENDING)], {}),
            ],
            "scans": [
                ([("scan_id", ASCENDING)], {"unique": True}),
                ([("timestamp", DESCENDING)], {}),
                ([("status", ASCENDING)], {}),
            ],
            "detection_logs": [
                ([("timestamp", DESCENDING)], {}),
                ([("threat_level", ASCENDING)], {}),
                ([("scan_id", ASCENDING)], {}),
            ],
            "models": [
                ([("model_name", ASCENDING)], {"unique": True}),
                ([("created_at", DESCENDING)], {}),
            ],
            "training_data": [
                ([("timestamp", DESCENDING)], {}),
                ([("label", ASCENDING)], {}),
            ],
            "raw_scans": [
                ([("timestamp", DESCENDING)], {}),
            ],
            "features_baseline": [
                ([("ssid", ASCENDING), ("bssid", ASCENDING)], {"unique": True}),
            ],
            "anomaly_signals": [
                ([("ssid", ASCENDING), ("bssid", ASCENDING)], {}),
                ([("layer", ASCENDING)], {}),
            ],
        }

        for collection_name, indexes in collection_indexes.items():
            if collection_name not in existing:
                try:
                    db.create_collection(collection_name)
                    logger.info("Created collection: %s", collection_name)
                except OperationFailure as e:
                    logger.warning("Could not create collection %s: %s", collection_name, e)


            for index_keys, index_opts in indexes:
                try:
                    db[collection_name].create_index(index_keys, **index_opts)
                except OperationFailure as exc:
                    # Index may already exist with different options
                    logger.debug(
                        "Index on %s: %s (may already exist)", collection_name, exc
                    )

        logger.info("Database indexes verified")

