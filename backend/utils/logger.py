import logging
import sys
from utils.config import get_settings

settings = get_settings()

def get_logger(name: str) -> logging.Logger:
    logger=logging.getLogger(name)

    if not logger.handlers:
        handler=logging.StreamHandler(sys.stdout)
        formatter=logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    return logger