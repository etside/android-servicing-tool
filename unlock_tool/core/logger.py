"""
Logger module for Android Servicing Tool

Provides centralized logging with file and console output,
rotation, and different log levels.
"""

import logging
import logging.handlers
import sys
import traceback
from pathlib import Path
from typing import Optional


class Logger:
    """
    Centralized logging system for the Android Servicing Tool.

    Features:
    - File logging with rotation in user data directory
    - Console output
    - Multiple log levels
    - Thread-safe operations
    - Crash reporting

    Usage:
        logger = Logger()
        logger.info("Operation started")
        logger.error("Error occurred")
    """

    def __init__(self, log_file: Optional[str] = None, max_bytes: int = 10*1024*1024, backup_count: int = 5):
        """
        Initialize the logger.

        Args:
            log_file: Path to log file (if None, uses user data directory)
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
        """
        if log_file is None:
            # Use user data directory for logs
            log_dir = self._get_user_log_dir()
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = str(log_dir / "unlock_tool.log")
        
        self.log_file = Path(log_file)
        self.logger = logging.getLogger("unlock_tool")
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler with rotation
        fh = logging.handlers.RotatingFileHandler(
            self.log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        # Set up crash reporting
        sys.excepthook = self._handle_crash

    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)

    def set_level(self, level: str):
        """Set logging level"""
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level.upper() in levels:
            self.logger.setLevel(levels[level.upper()])

    def get_log_path(self) -> Path:
        """Get the current log file path"""
        return self.log_file

    def _get_user_log_dir(self) -> Path:
        """Get the user data directory for logs."""
        if sys.platform == 'win32':
            base = Path.home() / 'AppData' / 'Roaming'
        elif sys.platform == 'darwin':
            base = Path.home() / 'Library' / 'Application Support'
        else:
            base = Path.home() / '.local' / 'share'
        return base / 'unlock_tool' / 'logs'

    def _handle_crash(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions by logging crash reports."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        crash_log = self._get_user_log_dir() / 'crash_report.log'
        try:
            with crash_log.open('a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Crash Report - {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
                f.write(f"{'='*50}\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
                f.write(f"{'='*50}\n\n")
        except Exception:
            # If we can't write crash log, at least log to main log
            self.critical(f"Failed to write crash report: {traceback.format_exc()}")

        # Log the crash
        self.critical(f"Uncaught exception: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Call original exception hook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def setup_logger(name: str = "unlock_tool", log_file: Optional[str] = None) -> logging.Logger:
    """Create and return a configured logger."""
    logger_instance = Logger(log_file=log_file)
    logger = logger_instance.logger
    logger.name = name
    return logger