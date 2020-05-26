import os

daemon = True
workers = __GUNICORN_WORKERS__

# default localhost:8000
bind = "0.0.0.0:8000"

# Pid
pids_dir = '__SEAFILE_DIR__/pids'
pidfile = os.path.join(pids_dir, 'seahub.pid')

# for file upload, we need a longer timeout value (default is only 30s, too short)
timeout = 1200

limit_request_line = 8190
