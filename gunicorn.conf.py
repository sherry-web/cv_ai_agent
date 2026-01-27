"""
Gunicorn Production Configuration
Optimized for CV AI Agent Flask application in containerized environments.
"""

import os
import multiprocessing

# ====================
# SERVER SOCKET
# ====================

# Bind address and port
# Use environment variable or default to 8080 (common for containers)
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8080')

# ====================
# WORKER PROCESSES
# ====================

# Determine optimal worker count
# Formula: (2 * CPU cores) + 1 (for I/O bound applications)
try:
    # Use environment variable if set, otherwise calculate
    cores = multiprocessing.cpu_count()
    default_workers = (2 * cores) + 1
except:
    default_workers = 3  # Fallback for CPU count failure

# Set worker count from environment or calculated default
workers = int(os.environ.get('GUNICORN_WORKERS', default_workers))

# Worker type for Flask/IOLoop applications
# sync: Traditional synchronous workers (safe default)
# gthread: Thread-based workers for I/O bound apps
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')

# Threads per worker (only for gthread worker class)
threads = int(os.environ.get('GUNICORN_THREADS', 1))

# ====================
# TIMEOUT & KEEPALIVE
# ====================

# Worker timeout (seconds)
# Terminate workers that hang for longer than this
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 30))

# Graceful shutdown timeout
# How long to wait for workers to finish before force kill
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 30))

# Keepalive for client connections (seconds)
# Time to wait for next request on persistent connection
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', 2))

# ====================
# LOGGING CONFIGURATION
# ====================

# Access log - HTTP requests
# '-' means log to stdout (container-friendly)
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')

# Error log - Application errors
# '-' means log to stderr (container-friendly)
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')

# Log level
# debug, info, warning, error, critical
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Access log format
# Custom format with request timing
access_log_format = os.environ.get(
    'GUNICORN_ACCESS_LOG_FORMAT',
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'
)

# ====================
# PROCESS MANAGEMENT
# ====================

# Process name (visible in ps, top, htop)
proc_name = os.environ.get('GUNICORN_PROC_NAME', 'cv_ai_agent')

# Maximum requests per worker before restart
# Helps prevent memory leaks
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))

# Jitter for max_requests to prevent all workers restarting simultaneously
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 50))

# ====================
# SECURITY & PERFORMANCE
# ====================

# Maximum pending connections
backlog = int(os.environ.get('GUNICORN_BACKLOG', 2048))

# Restart workers after this many seconds (prevents stale workers)
worker_ttl = int(os.environ.get('GUNICORN_WORKER_TTL', 3600))

# Daemon mode (not recommended for containerized deployments)
daemon = os.environ.get('GUNICORN_DAEMON', 'False').lower() == 'true'

# ====================
# DEBUG & DEVELOPMENT
# ====================

# Reload on code changes (development only - disable in production)
reload = os.environ.get('GUNICORN_RELOAD', 'False').lower() == 'true'

# Preload application code before forking workers
# Reduces memory usage but can cause issues with some libraries
preload_app = os.environ.get('GUNICORN_PRELOAD', 'False').lower() == 'true'

# ====================
# ENVIRONMENT VARIABLES
# ====================

# Pass these environment variables to worker processes
raw_env = [
    'FLASK_ENV',
    'SECRET_KEY', 
    'DEPLOY_TIMESTAMP',
    'PYTHONPATH'
]