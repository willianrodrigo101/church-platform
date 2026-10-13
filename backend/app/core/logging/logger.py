import logging
import sys

from app.core.config.settings import settings


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("church_platform")
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))

    logger.addHandler(handler)
    return logger


logger = setup_logger()
