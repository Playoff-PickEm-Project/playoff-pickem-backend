"""
Gunicorn configuration file for production deployment.

This ensures the APScheduler only runs in ONE worker process to avoid duplicates.
"""

import multiprocessing

# Number of worker processes
workers = 1  # Use only 1 worker to ensure scheduler runs once

# Worker class
worker_class = "sync"

# Bind address
bind = "0.0.0.0:8000"

# Timeout
timeout = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"


def post_fork(server, worker):
    """
    Called just after a worker has been forked.

    Initialize the scheduler in the first worker only.
    """
    # Only initialize scheduler in the first worker
    if worker.age == 0:  # First worker
        from app.services.game.schedulerService import SchedulerService
        try:
            SchedulerService.initialize_scheduler()
            server.log.info("APScheduler initialized in worker %s", worker.pid)
        except Exception as e:
            server.log.error("Failed to initialize scheduler: %s", e)
