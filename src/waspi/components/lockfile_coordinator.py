import os
import fcntl
import logging

logger = logging.getLogger("waspi.lockfile_coordinator")


class LockFileCoordinator:
    """A lock file coordinator to coordinate between the main script and google drive synchronisation."""

    def __init__(self, lock_file_path: str = "/tmp/waspi.lock"):
        """Initialize the LockFileCoordinator with the lock file path."""
        self.lock_file_path = lock_file_path
        # self.lock_file = None

    def acquire_lock(self):
        """Acquire the lock by creating a lock file."""
        try:
            self.lock_file = open(self.lock_file_path, "w")
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            self.lock_file.write(f"PID: {os.getpid()}\n")
            self.lock_file.flush()
            logger.info("Lock acquired successfully")
            return True

        except (IOError, OSError) as e:
            logger.warning(f"Failed to acquire lock: {e}")
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None
            return False

    def release_lock(self):
        """Release the lock by closing the lock file."""
        if self.lock_file:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                logger.info("Lock released successfully")
            except (IOError, OSError) as e:
                logger.error(f"Failed to release lock: {e}")
            finally:
                self.lock_file = None

    def is_sync_in_progress(self) -> bool:
        """Check if a sync is in progress by checking the existence of the lock file."""
        try:
            with open(self.lock_file_path, "r") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False  # If we can lock it, no sync is in progress
        except (FileNotFoundError, IOError):
            return False
