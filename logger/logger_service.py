import logging
import os
from logging.handlers import RotatingFileHandler

class LoggingService:
    def __init__(self, log_file='app.log', log_level=logging.DEBUG, max_bytes=1000000, backup_count=3, logger_name = "LoggingService"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        self._setup_console_handler()
        self._setup_file_handler(log_file, max_bytes, backup_count)

    def _setup_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(self, log_file, max_bytes, backup_count):
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

# Usage example
if __name__ == "__main__":
    logger = LoggingService(log_file='logs/app_dropcontact.log')
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
