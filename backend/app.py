"""
Netguard Flask Application
---
Production-grade Flask application with factory pattern,
structured logging, health checks, and clean startup order.
"""

import os
import sys
import logging
import uuid
from datetime import datetime, timezone

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from dotenv import load_dotenv

from config import get_config, validate_config
from models.database import Database
from socket_server import socketio

# ─── Logging Setup ───────────────────────────────────────────


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured logging for the application."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # Reduce noise from libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging.getLogger("netguard")


# ─── Application Factory ────────────────────────────────────


def create_app(config=None) -> Flask:
    """
    Create and configure the Flask application.

    Startup order:
    1. Load environment
    2. Configure logging
    3. Validate configuration
    4. Connect to MongoDB
    5. Initialize SocketIO
    6. Register blueprints
    7. Register middleware & error handlers
    """
    load_dotenv()

    app = Flask(__name__)
    cfg = config or get_config()

    # Apply config
    app.config["SECRET_KEY"] = cfg.SECRET_KEY
    app.config["DEBUG"] = getattr(cfg, "DEBUG", False)
    app.config["TESTING"] = getattr(cfg, "TESTING", False)

    # 1. Logging
    logger = setup_logging(cfg.LOG_LEVEL)
    logger.info("=" * 60)
    logger.info("Netguard starting  [env=%s]", cfg.ENVIRONMENT)
    logger.info("=" * 60)

    # 2. Validate config
    issues = validate_config(cfg)
    for issue in issues:
        logger.warning("CONFIG: %s", issue)

    # 3. CORS
    CORS(app, origins=cfg.CORS_ORIGINS)

    # 4. MongoDB
    db_connected = Database.connect(uri=cfg.MONGODB_URI, db_name=cfg.MONGODB_DB)
    if db_connected:
        logger.info("MongoDB: connected")
    else:
        logger.error(
            "MongoDB: FAILED to connect. The app will start but DB "
            "operations will fail. Check MONGODB_URI in .env"
        )

    # 5. SocketIO
    socketio.init_app(app, cors_allowed_origins="*")

    # 6. Root Route
    @app.route("/", methods=["GET"])
    def index():
        """Root endpoint - redirect to health or show welcome."""
        return jsonify({
            "message": "Netguard Backend API is running",
            "health_check": "/health",
            "version": "1.0.0",
            "status": "online"
        }), 200

    # 7. Register blueprints
    _register_blueprints(app, logger)

    # 7. Middleware & error handlers
    _register_middleware(app)
    _register_error_handlers(app)
    _register_health_routes(app, cfg)

    logger.info("Netguard ready on http://%s:%s", cfg.HOST, cfg.PORT)
    return app


# ─── Blueprint Registration ─────────────────────────────────


def _register_blueprints(app: Flask, logger: logging.Logger):
    """Import and register all route blueprints in correct order."""
    blueprints = []

    try:
        from routes.scan_routes import scan_bp
        blueprints.append(("scan", scan_bp))
    except ImportError as e:
        logger.warning("Could not load scan_routes: %s", e)

    try:
        from routes.detection_routes import detection_bp
        blueprints.append(("detection", detection_bp))
    except ImportError as e:
        logger.warning("Could not load detection_routes: %s", e)

    try:
        from routes.logs_routes import logs_bp
        blueprints.append(("logs", logs_bp))
    except ImportError as e:
        logger.warning("Could not load logs_routes: %s", e)

    try:
        from routes.model_routes import model_bp
        blueprints.append(("model", model_bp))
    except ImportError as e:
        logger.warning("Could not load model_routes: %s", e)

    try:
        from routes.training_routes import training_bp
        blueprints.append(("training", training_bp))
    except ImportError as e:
        logger.warning("Could not load training_routes: %s", e)

    try:
        from routes.pipeline_routes import pipeline_bp
        blueprints.append(("pipeline", pipeline_bp))
    except ImportError as e:
        logger.warning("Could not load pipeline_routes: %s", e)

    try:
        from routes.phase2_routes import phase2_bp
        blueprints.append(("phase2", phase2_bp))
    except ImportError as e:
        logger.warning("Could not load phase2_routes: %s", e)

    for name, bp in blueprints:
        app.register_blueprint(bp)
        logger.info("  ✓ Blueprint: %s", name)


# ─── Middleware ──────────────────────────────────────────────


def _register_middleware(app: Flask):
    """Register request/response middleware."""

    @app.before_request
    def before_request_handler():
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = datetime.now(timezone.utc)

    @app.after_request
    def after_request_handler(response):
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id
        # Duration
        if hasattr(g, "start_time"):
            duration = (datetime.now(timezone.utc) - g.start_time).total_seconds()
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
        return response


# ─── Error Handlers ──────────────────────────────────────────


def _register_error_handlers(app: Flask):
    """Register centralized JSON error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, "description") else str(error),
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found", "path": request.path}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed",
            "method": request.method,
            "path": request.path,
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        }), 500


# ─── Health Routes ───────────────────────────────────────────


def _register_health_routes(app: Flask, cfg):
    """Register health check and system info endpoints."""

    @app.route("/health", methods=["GET"])
    def health():
        """Deep health check: DB + models + system."""
        db_ok = Database.is_connected()

        # Check if models directory has trained models
        models_dir = cfg.MODELS_DIR
        model_files = []
        if os.path.isdir(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith(".pkl")]

        status = "healthy" if db_ok else "degraded"

        return jsonify({
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": cfg.ENVIRONMENT,
            "checks": {
                "mongodb": "connected" if db_ok else "disconnected",
                "models_loaded": len(model_files),
            },
        }), 200 if db_ok else 503

    @app.route("/api/system/info", methods=["GET"])
    def system_info():
        """System resource information."""
        try:
            import psutil

            disk_path = "C:\\" if os.name == "nt" else "/"
            return jsonify({
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage(disk_path).percent,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }), 200
        except ImportError:
            return jsonify({
                "error": "psutil not installed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }), 200


# ─── Entry Point ─────────────────────────────────────────────


app = create_app()

if __name__ == "__main__":
    cfg = get_config()
    socketio.run(
        app,
        host=cfg.HOST,
        port=cfg.PORT,
        debug=getattr(cfg, "DEBUG", False),
        use_reloader=False,
    )
