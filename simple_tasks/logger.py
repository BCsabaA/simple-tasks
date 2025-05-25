# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

class AppLogger:
    def __init__(self, name="myapp", log_file="logs/app.log", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Only set up handlers once
        if not self.logger.hasHandlers():
            self._setup(log_file, level)

    def _setup(self, log_file, level):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Console handler
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_format)

        # File handler (rotating: 1 MB max, keep 3 backups)
        file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        file_format = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
