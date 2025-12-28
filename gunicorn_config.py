"""
Gunicorn configuration file for production deployment.

This ensures the APScheduler only runs in ONE worker process to avoid duplicates.
"""

import multiprocessing
import os

# Number of worker processes
workers = 1  # Use only 1 worker to ensure scheduler runs once

# Worker class
worker_class = "sync"

# Bind address - use PORT from environment (Render sets this) or default to 8000
port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Timeout
timeout = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Track if scheduler has been initialized
scheduler_initialized = False


def post_fork(server, worker):
    """
    Called just after a worker has been forked.

    Initialize the scheduler in the first worker only.
    """
    global scheduler_initialized

    # Only initialize scheduler once across all workers
    if not scheduler_initialized:
        server.log.info("Attempting to initialize APScheduler in worker %s", worker.pid)
        from app.services.game.schedulerService import SchedulerService
        from app import create_app
        try:
            # Create app instance for the scheduler to use
            app = create_app()
            SchedulerService.initialize_scheduler(app)
            scheduler_initialized = True
            server.log.info("APScheduler successfully initialized in worker %s", worker.pid)
        except Exception as e:
            server.log.error("Failed to initialize scheduler in worker %s: %s", worker.pid, e)
            import traceback
            server.log.error("Traceback: %s", traceback.format_exc())
    else:
        server.log.info("Scheduler already initialized, skipping for worker %s", worker.pid)
