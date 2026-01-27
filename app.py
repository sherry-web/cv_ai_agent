"""
CV AI Agent - Core Application
Updated to integrate centralized environment configuration loader.
"""

import os
import logging
import logging.config
from pathlib import Path
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from .config import DevelopmentConfig, TestingConfig, ProductionConfig


# ====================
# LOGGING CONFIGURATION
# ====================

def setup_logging(level=None):
    """
    Initialize logging configuration from logging.conf.
    Falls back to basic config if file not found.
    Uses level from configuration if provided.
    """
    try:
        config_path = Path(__file__).parent / 'logging.conf'
        if config_path.exists():
            logging.config.fileConfig(config_path, disable_existing_loggers=False)
            logger = logging.getLogger("app")
            logger.info(f"Loaded logging configuration from: {config_path}")
        else:
            logging.basicConfig(
                level=level or logging.INFO,
                format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            logger = logging.getLogger("app")
            logger.warning(f"logging.conf not found at {config_path}, using basic logging")
        return logger
    except Exception as e:
        logging.basicConfig(level=logging.WARNING)
        logger = logging.getLogger("app")
        logger.error(f"Failed to setup logging: {str(e)}")
        return logger

# ====================
# CONFIGURATION LOADER
# ====================

def get_config():
    """
    Select configuration class based on environment variable:
    FLASK_ENV or APP_ENV (development, testing, production)
    Defaults to DevelopmentConfig.
    """
    env = os.environ.get("FLASK_ENV") or os.environ.get("APP_ENV", "development")
    env = env.lower()
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig

# Initialize config and logging
ConfigClass = get_config()
logger = setup_logging(getattr(ConfigClass, "LOG_LEVEL", None))

# ====================
# APPLICATION FACTORY
# ====================

def create_app(config_class=None):
    """
    Flask application factory.
    Automatically applies selected configuration and logging.
    """
    app = Flask(__name__)

    # Apply configuration
    config_class = config_class or ConfigClass
    try:
        app.config.from_object(config_class)
    except RuntimeError as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    logger.info(f"Starting CV AI Agent with config: {config_class.__name__}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', os.environ.get('APP_ENV', 'development'))}")

    # ====================
    # HEALTH & READINESS
    # ====================
    @app.route("/")
    def home():
        logger.debug("Root endpoint accessed")
        return jsonify({
            "service": "CV AI Agent",
            "version": "1.0.0",
            "status": "operational",
            "message": "Hello! I am your baby AI agent 🤖"
        })

    @app.route("/health")
    def health_check():
        logger.debug("Health check requested")
        return jsonify({"status": "healthy"}), 200

    @app.route("/ready")
    def readiness_check():
        logger.debug("Readiness check requested")
        return jsonify({"ready": True}), 200

    # ====================
    # ERROR HANDLERS
    # ====================
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 Not Found: {request.path}")
        return jsonify({"error": "Not Found", "message": "Resource does not exist", "path": request.path}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error: {error}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": "Unexpected error occurred"}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        if error.code >= 500:
            logger.error(f"HTTP {error.code}: {error.name} - {error.description}")
        elif error.code >= 400:
            logger.warning(f"HTTP {error.code}: {error.name} - {error.description}")
        return jsonify({"error": error.name, "message": error.description, "code": error.code}), error.code

    # ====================
    # HOOKS
    # ====================
    @app.before_request
    def before_request():
        logger.debug(f"Incoming request: {request.method} {request.path}")

    @app.after_request
    def after_request(response):
        response.headers['X-Service'] = 'CV-AI-Agent'
        response.headers['X-Version'] = '1.0.0'
        if response.status_code >= 500:
            logger.error(f"Response {response.status_code} for {request.method} {request.path}")
        elif response.status_code >= 400:
            logger.warning(f"Response {response.status_code} for {request.method} {request.path}")
        else:
            logger.debug(f"Response {response.status_code} for {request.method} {request.path}")
        return response

    return app


# ====================
# ENTRY POINT
# ====================
if __name__ == "__main__":
    app = create_app()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    startup_msg = f"🚀 CV AI Agent starting on http://{host}:{port} ({ConfigClass.__name__})"
    print(startup_msg)
    logger.info(startup_msg)
    app.run(host=host, port=port, debug=app.config.get("DEBUG", True))
