import logging
from typing import Final

from vigilant.common.values import settings

APP_NAME: Final[str] = "Vigilant"
LOG_LEVEL: Final[str] = "LOG_LEVEL"
DEFAULT_LOG_LEVEL: Final[int] = 20


class _DefaultContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "role"):
            record.role = "App"
        if not hasattr(record, "entity"):
            record.entity = APP_NAME
        return True


def build_logger() -> logging.Logger:
    formatter = logging.Formatter(
        "%(levelname)s - [%(asctime)s] - %(role)s - %(entity)s - %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(_DefaultContextFilter())

    logger = logging.getLogger()
    logger.addHandler(handler)

    log_level: int = _get_loglevel()
    logger.setLevel(log_level)

    return logger


def _get_loglevel() -> int:
    log_level: str | int = settings.LOG_LEVEL or DEFAULT_LOG_LEVEL

    if isinstance(log_level, str):
        possible_levels: dict[str, int] = logging.getLevelNamesMapping()
        log_level = possible_levels.get(log_level.upper(), DEFAULT_LOG_LEVEL)

    return log_level
