import logging
import os
from typing import Final

APP_NAME: Final[str] = "vigilant"
LOG_LEVEL: Final[str] = "LOG_LEVEL"
DEFAULT_LOG_LEVEL: Final[int] = 20


def build_logger() -> logging.Logger:
    formatter = logging.Formatter(
        "%(levelname)s - [%(asctime)s] - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(APP_NAME)
    logger.addHandler(handler)

    log_level: int = _get_loglevel()
    logger.setLevel(log_level)

    return logger


def _get_loglevel() -> int:
    log_level: str | int = os.getenv(LOG_LEVEL) or DEFAULT_LOG_LEVEL

    if isinstance(log_level, str):
        possible_levels: dict[str, int] = logging.getLevelNamesMapping()
        log_level = possible_levels.get(log_level.upper(), DEFAULT_LOG_LEVEL)

    return log_level
