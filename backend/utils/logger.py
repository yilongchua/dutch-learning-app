# Simple logger for Thenews backend
import logging
from ..utils.date_utils import utc_now

def get_logger(name: str = "thenews") -> logging.Logger:
    """Configure a logger with UTC timestamps."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    # Ensure timestamps are UTC
    logging.Formatter.converter = lambda *args: utc_now().timetuple()
    return logger