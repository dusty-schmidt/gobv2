"""
Global logging system for the gob ecosystem.
Centralized logging that all chatbots and agents can use.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from collections import deque

# Global configuration
DEFAULT_LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FILE = os.getenv('LOG_FILE', '') or str(Path(__file__).parent.parent / 'gob.log')


class ReverseChronologicalFileHandler(logging.Handler):
    """File handler that writes newest logs at the top and auto-deletes old logs."""

    def __init__(self, filename, max_lines=1000, max_age_days=7, encoding='utf-8'):
        super().__init__()
        self.filename = filename
        self.max_lines = max_lines
        self.max_age_days = max_age_days
        self.encoding = encoding
        self._lines = deque(maxlen=max_lines)

        # Load existing logs if file exists
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    existing_lines = f.readlines()
                    # Add existing lines in reverse order (newest first becomes oldest first in deque)
                    for line in reversed(existing_lines[-max_lines:]):
                        self._lines.appendleft(line.rstrip('\n'))
            except Exception:
                # If we can't read the file, start fresh
                pass

        # Clean up old logs on initialization
        self._cleanup_old_logs()

    def _cleanup_old_logs(self):
        """Remove logs older than max_age_days"""
        import time
        from datetime import datetime

        current_time = time.time()
        max_age_seconds = self.max_age_days * 24 * 60 * 60

        # Filter out old logs
        filtered_lines = deque(maxlen=self.max_lines)
        for line in self._lines:
            try:
                # Extract timestamp from log line (format: "YYYY-MM-DD HH:MM:SS")
                if len(line) > 19 and line[4] == '-' and line[7] == '-':
                    timestamp_str = line[:19]  # "YYYY-MM-DD HH:MM:SS"
                    log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").timestamp()
                    if current_time - log_time <= max_age_seconds:
                        filtered_lines.append(line)
            except (ValueError, IndexError):
                # If we can't parse the timestamp, keep the line
                filtered_lines.append(line)

        self._lines = filtered_lines

    def emit(self, record):
        try:
            msg = self.format(record)
            self._lines.appendleft(msg)

            # Clean up old logs periodically (every 100 messages)
            if len(self._lines) % 100 == 0:
                self._cleanup_old_logs()

            # Write all lines back to file (newest first)
            with open(self.filename, 'w', encoding=self.encoding) as f:
                for line in self._lines:
                    f.write(line + '\n')

        except Exception:
            self.handleError(record)


def configure_global_logging(level: str = DEFAULT_LOG_LEVEL, log_file: str = LOG_FILE):
    """Configure root logger with console and rotating file handlers."""
    level = getattr(logging, level.upper(), logging.INFO)

    # If LOG_LEVEL is explicitly set to DEBUG, also enable debug logging for our modules
    if os.getenv('LOG_LEVEL', '').upper() == 'DEBUG':
        level = logging.DEBUG

    root = logging.getLogger()
    root.setLevel(level)

    # Console handler (stream)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch_formatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    ch.setFormatter(ch_formatter)

    # Reverse chronological file handler (newest logs at top, auto-deletes old logs after 7 days)
    fh = ReverseChronologicalFileHandler(log_file, max_lines=1000, max_age_days=7, encoding='utf-8')
    fh.setLevel(level)
    fh_formatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fh_formatter)

    # Avoid duplicate handlers if configure_global_logging is called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(ch)
    if not any(isinstance(h, ReverseChronologicalFileHandler) for h in root.handlers):
        root.addHandler(fh)


def get_logger(name: str):
    """Return a module logger configured with the global settings."""
    if not logging.getLogger().handlers:
        configure_global_logging()
    return logging.getLogger(name)


# Configure immediately using environment defaults
configure_global_logging()

# Suppress noisy third-party library logs in interactive mode
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)