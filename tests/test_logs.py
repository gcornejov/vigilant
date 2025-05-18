import logging
from unittest import mock

import pytest

from vigilant import log


@mock.patch("vigilant.log._get_loglevel")
def test_build_logger(mock_get_loglevel: mock.MagicMock) -> None:
    mock_loglevel: int = 10
    mock_get_loglevel.return_value = mock_loglevel

    logger: logging.Logger = log.build_logger()

    mock_get_loglevel.assert_called_once()
    assert logger.hasHandlers() and logger.level == mock_loglevel

    handler: logging.Handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler) and handler.formatter is not None

    formatter: logging.Formatter = handler.formatter
    assert (
        formatter.datefmt == "%Y-%m-%d %H:%M:%S"
        and formatter._fmt == "%(levelname)s - [%(asctime)s] - %(message)s"
    )

@pytest.mark.parametrize(
    "expected_loglevel, loglevel_env",
    (
        pytest.param(20, "", id="LOG_LEVEL env not set"),
        pytest.param(10, "DEBUG", id="LOG_LEVEL env set at DEBUG"),
        pytest.param(40, "error", id="LOG_LEVEL env set at ERROR lowercase"),
        pytest.param(20, "DEGUB", id="LOG_LEVEL env set invalid value"),
    )
)
def test_log_level(monkeypatch: pytest.MonkeyPatch, expected_loglevel: int, loglevel_env: str) -> None:
    monkeypatch.setenv("LOG_LEVEL", loglevel_env)

    log_level: int = log._get_loglevel()

    assert log_level == expected_loglevel
