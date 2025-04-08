import os

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
workers = 1
worker_class = 'sync'
timeout = 30

# Logging
accesslog = 'logs/gunicorn-access.log'
errorlog = 'logs/gunicorn-error.log'
loglevel = 'info'

# Process naming
proc_name = 'portfolio'

# Server mechanics
daemon = False
pidfile = 'logs/gunicorn.pid' 