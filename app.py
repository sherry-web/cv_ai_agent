"""
CV AI Agent - Core Application
Entry point for the CV improvement AI agent system.
"""

import os
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

# ====================
# APPLICATION FACTORY
# ====================

def create_app(config_name=None):
    """
    Application factory pattern.
    Allows different configurations for dev, test, production.
    """
    app = Flask(__name__)
    
    # ====================
    # CONFIGURATION
    # ====================
    
    # Default configuration (development)
    app.config.update(
        DEBUG=os.environ.get('FLASK_DEBUG', 'True') == 'True',
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        JSON_SORT_KEYS=False,  # Maintain dictionary order
        JSONIFY_PRETTYPRINT_REGULAR=True
    )
    
    # ====================
    # HEALTH & READINESS
    # ====================
    
    @app.route('/')
    def home():
        """Root endpoint - service greeting"""
        return jsonify({
            'service': 'CV AI Agent',
            'version': '1.0.0',
            'status': 'operational',
            'message': 'Hello! I am your baby AI agent 🤖'
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for deployment monitoring"""
        return jsonify({
            'status': 'healthy',
            'timestamp': os.environ.get('DEPLOY_TIMESTAMP', 'local-dev')
        }), 200
    
    @app.route('/ready')
    def readiness_check():
        """Readiness check for load balancers"""
        # Add dependency checks here later (database, APIs, etc.)
        return jsonify({'ready': True}), 200
    
    # ====================
    # ERROR HANDLERS
    # ====================
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 - Not Found"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource does not exist',
            'path': request.path if request else 'unknown'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 - Internal Server Error"""
        # Log the error here (to be implemented)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'reference_id': 'ERR-500'  # Add logging reference later
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all HTTP exceptions consistently"""
        return jsonify({
            'error': error.name,
            'message': error.description,
            'code': error.code
        }), error.code
    
    # ====================
    # APPLICATION HOOKS
    # ====================
    
    @app.before_request
    def before_request():
        """Execute before each request"""
        # Add request logging, authentication, etc. here
        pass
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        # Add CORS headers, response logging, etc. here
        response.headers['X-Service'] = 'CV-AI-Agent'
        response.headers['X-Version'] = '1.0.0'
        return response
    
    # ====================
    # UTILITY FUNCTIONS
    # ====================
    
    @app.route('/info')
    def app_info():
        """Display application configuration (safe info only)"""
        safe_config = {
            'debug': app.config['DEBUG'],
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'root_path': app.root_path
        }
        return jsonify(safe_config)
    
    return app


# ====================
# ENTRY POINT
# ====================

if __name__ == '__main__':
    # Create application instance
    app = create_app()
    
    # Get port from environment or default
    port = int(os.environ.get('PORT', 5000))
    
    # Get host from environment or default
    # '0.0.0.0' makes it accessible on network, '127.0.0.1' for local only
    host = os.environ.get('HOST', '127.0.0.1')
    
    # Start the server
    print(f"🚀 CV AI Agent starting on http://{host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/health")
    print(f"🔍 App info: http://{host}:{port}/info")
    print("Press CTRL+C to stop the server")
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])