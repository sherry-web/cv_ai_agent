# File: cv_ai_agent/config.py
"""
Centralized configuration loader for CV AI Agent Flask application.

Provides:
- DevelopmentConfig: local development defaults
- TestingConfig: pytest/testing defaults
- ProductionConfig: production defaults (Docker, Gunicorn, CI/CD)

Features:
- Loads environment variables from system or .env file
- Validates required environment variables
- Provides default settings for host, port, debug, logging
- Compatible with Windows/Linux, Docker, Gunicorn

Usage:
    from cv_ai_agent.config import DevelopmentConfig, TestingConfig, ProductionConfig

    app.config.from_object(DevelopmentConfig)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def require_env(var_name: str) -> str:
    """
    Retrieve an environment variable and raise an error if missing.
    
    Args:
        var_name (str): Environment variable name
    
    Returns:
        str: Environment variable value
    
    Raises:
        RuntimeError: if variable is not set
    """
    value = os.getenv(var_name)
    if value is None:
        raise RuntimeError(f"Required environment variable '{var_name}' is missing.")
    return value


class BaseConfig:
    """Base configuration with defaults and common settings."""
    APP_NAME = os.getenv("APP_NAME", "CV_AI_AGENT")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "yes"]
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Example: database URL, secret key
    SECRET_KEY = require_env("SECRET_KEY")
    DATABASE_URL = require_env("DATABASE_URL")

    # Optional settings with defaults
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    JSON_SORT_KEYS = os.getenv("JSON_SORT_KEYS", "False").lower() in ["true", "1", "yes"]


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
