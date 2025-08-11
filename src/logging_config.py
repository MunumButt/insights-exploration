import logging
import json
import logging.handlers
import sys
from datetime import datetime, timezone
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record):
        # Create the base log structure
        log_object = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add any extra fields that were passed in
        if hasattr(record, "extra_data"):
            log_object.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_object, default=str)


def get_logger(
    name: str, level: int = logging.INFO, log_format: str = "json"
) -> logging.Logger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (usually __name__)
        level: Logging level
        log_format: "json" or "standard"

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handlers if the logger doesn't already have them
    if not logger.handlers:
        logger.setLevel(level)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Set formatter based on format preference
        if log_format == "json":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
