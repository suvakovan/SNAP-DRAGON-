"""
Logging configuration with rotating file handler and rich console logging.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from rich.logging import RichHandler
from lecturelens.config import config


def setup_logging(log_level: str = config.log_level) -> logging.Logger:
    """Configures and returns the main application logger."""
    config.logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = config.logs_dir / "lecturelens.log"

    logger = logging.getLogger("lecturelens")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console Handler (Rich)
    rich_handler = RichHandler(rich_tracebacks=True, show_time=True)
    rich_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()
