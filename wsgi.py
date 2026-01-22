"""
CV AI Agent - Gunicorn WSGI Entry Point
Production entry point for scalable WSGI server deployment.
"""

import os
import sys

# -----------------------------------------------------------------------------
# ENVIRONMENT SETUP
# -----------------------------------------------------------------------------

# Add project root to Python path for reliable imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# -----------------------------------------------------------------------------
# ENVIRONMENT VARIABLE LOADING
# -----------------------------------------------------------------------------

# Load environment variables from .env file if it exists
# Production environments should set variables directly, not via .env
try:
    from dotenv import load_dotenv
    # Load .env from project root, but don't fail if missing
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=dotenv_path, verbose=False)
except ImportError:
    # python-dotenv not installed (unlikely in production)
    pass

# -----------------------------------------------------------------------------
# FLASK APPLICATION FACTORY IMPORT
# -----------------------------------------------------------------------------

# Import the Flask application factory
# Using absolute import pattern for reliability
from app import create_app

# -----------------------------------------------------------------------------
# APPLICATION INSTANCE
# -----------------------------------------------------------------------------

# Create the Flask application instance
# This object is what Gunicorn will use as the WSGI application
application = create_app()

# -----------------------------------------------------------------------------
# DIRECT EXECUTION SUPPORT (for debugging)
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    """
    Allow direct execution for debugging purposes.
    In production, Gunicorn will import 'application' directly.
    """
    # Get configuration from environment with safe defaults
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Run development server (not for production use)
    print(f"⚠️  Development server starting on http://{host}:{port}")
    print(f"⚠️  For production, use: gunicorn --bind {host}:{port} wsgi:application")
    application.run(host=host, port=port, debug=debug)