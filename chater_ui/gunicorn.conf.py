# Gunicorn configuration file for production deployment
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
worker_class = "sync"
worker_connections = 1000
timeout = 220
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging - verbose for personal development
accesslog = "-"
errorlog = "-"
loglevel = "debug"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
capture_output = True

# Process naming
proc_name = "chater_ui"

# Server mechanics
preload_app = True
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if certificates are available)
# keyfile = None
# certfile = None 