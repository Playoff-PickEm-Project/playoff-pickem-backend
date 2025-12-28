"""
Scheduler Service for managing periodic polling tasks.

This service initializes and manages APScheduler for periodic polling
of live NFL game data. The scheduler runs independently of HTTP requests
and persists across server restarts.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.game.pollingService import PollingService
from flask import current_app
import atexit


class SchedulerService:
    """
    Service class for managing APScheduler background tasks.

    This service creates a background scheduler that polls active games
    every 2 minutes and handles graceful shutdown.
    """

    scheduler = None
    app = None

    @staticmethod
    def initialize_scheduler(app=None) -> BackgroundScheduler:
        """
        Initialize and start the background scheduler for game polling.

        Sets up a recurring job that runs every 2 minutes to poll
        all active NFL games for live updates.

        Args:
            app: Flask application instance (required for app context)

        Returns:
            BackgroundScheduler: The initialized scheduler instance.
        """
        if SchedulerService.scheduler is not None:
            print("Scheduler already initialized")
            return SchedulerService.scheduler

        if app is None:
            raise ValueError("Flask app instance is required for scheduler initialization")

        # Store the app instance
        SchedulerService.app = app

        # Create background scheduler
        scheduler = BackgroundScheduler()

        # Create wrapper function that runs polling with app context
        def poll_with_context():
            with SchedulerService.app.app_context():
                PollingService.poll_all_active_games()

        # Add polling job - runs every 2 minutes
        scheduler.add_job(
            func=poll_with_context,
            trigger=IntervalTrigger(minutes=2),
            id='poll_active_games',
            name='Poll active NFL games for live updates',
            replace_existing=True
        )

        # Start the scheduler
        scheduler.start()
        print("APScheduler initialized and started polling every 2 minutes")

        # Run one poll immediately on startup to test
        print("[SCHEDULER] Running initial poll on startup...")
        try:
            with app.app_context():
                PollingService.poll_all_active_games()
        except Exception as e:
            print(f"[SCHEDULER] Error during initial poll: {e}")
            import traceback
            print(f"[SCHEDULER] Traceback: {traceback.format_exc()}")

        # Store scheduler instance
        SchedulerService.scheduler = scheduler

        # Register shutdown hook to gracefully stop scheduler
        atexit.register(lambda: SchedulerService.shutdown_scheduler())

        return scheduler

    @staticmethod
    def shutdown_scheduler() -> None:
        """
        Gracefully shutdown the scheduler when the application stops.

        This is automatically called when the application exits via atexit.
        """
        if SchedulerService.scheduler is not None:
            SchedulerService.scheduler.shutdown()
            print("APScheduler shut down successfully")
            SchedulerService.scheduler = None

    @staticmethod
    def get_scheduler() -> BackgroundScheduler:
        """
        Get the current scheduler instance.

        Returns:
            BackgroundScheduler: The current scheduler, or None if not initialized.
        """
        return SchedulerService.scheduler

    @staticmethod
    def pause_scheduler() -> bool:
        """
        Pause the scheduler (useful for maintenance or testing).

        Returns:
            bool: True if paused successfully, False if scheduler not initialized.
        """
        if SchedulerService.scheduler is not None:
            SchedulerService.scheduler.pause()
            print("Scheduler paused")
            return True
        return False

    @staticmethod
    def resume_scheduler() -> bool:
        """
        Resume the scheduler after pausing.

        Returns:
            bool: True if resumed successfully, False if scheduler not initialized.
        """
        if SchedulerService.scheduler is not None:
            SchedulerService.scheduler.resume()
            print("Scheduler resumed")
            return True
        return False

    @staticmethod
    def get_scheduled_jobs() -> list:
        """
        Get list of all scheduled jobs.

        Returns:
            list: List of Job objects currently scheduled.
        """
        if SchedulerService.scheduler is not None:
            return SchedulerService.scheduler.get_jobs()
        return []
