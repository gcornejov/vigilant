from itertools import cycle
from pathlib import Path
from typing import Iterator
from unittest import mock

import pytest

from vigilant.common.exceptions import DownloadTimeout
from vigilant.common.values import IOResources
from vigilant.data_collector import crawler
from vigilant.data_collector.crawler import ChileCrawler


@mock.patch("vigilant.data_collector.crawler.ChileCrawler._login")
@mock.patch("vigilant.data_collector.crawler.ChileCrawler._get_current_amount")
@mock.patch("vigilant.data_collector.crawler.ChileCrawler._get_credit_transactions")
@mock.patch("vigilant.data_collector.crawler.ChileCrawler._logout")
def test_crawl(
    _login: mock.MagicMock,
    _get_current_amount: mock.MagicMock,
    _get_credit_transactions: mock.MagicMock,
    _logout: mock.MagicMock,
    mock_driver: mock.MagicMock,
) -> None:
    ChileCrawler(mock_driver).crawl()

    _login.assert_called_once()
    _get_current_amount.assert_called_once()
    _get_credit_transactions.assert_called_once()
    _logout.assert_called_once()


def test_login(mock_driver: mock.MagicMock) -> None:
    ChileCrawler(mock_driver)._login()

    mock_driver.get.assert_called_once()
    mock_driver.find_element.assert_called()
    mock_driver.find_element().send_keys.assert_called()
    mock_driver.find_element().click.assert_called_once()


@pytest.mark.parametrize(
    "found_elements",
    (([]), (["banner"])),
)
def test_get_current_amount(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_driver: mock.MagicMock,
    found_elements: list[str],
) -> None:
    mock_formatted_amount: str = " $1.000"
    mock_amount: str = "1000"

    mock_element = mock.MagicMock()
    mock_element.text = mock_formatted_amount
    mock_driver.find_element.return_value = mock_element

    mock_driver.find_elements.return_value = found_elements

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    ChileCrawler(mock_driver)._get_current_amount()
    amount: str = (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).read_text()

    mock_driver.find_elements.assert_called_once()
    mock_driver.find_element.assert_called()
    assert amount == mock_amount


def test_get_credit_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock
) -> None:
    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)
    (tmp_path / "file.xls").write_text("Hesitation is defeat!")

    ChileCrawler(mock_driver)._get_credit_transactions()

    mock_driver.get.assert_called_once()


@mock.patch(
    "vigilant.data_collector.crawler.check_condition_timeout",
    mock.Mock(side_effect=TimeoutError),
)
def test_get_credit_transactions_exception(mock_driver: mock.MagicMock) -> None:
    with pytest.raises(DownloadTimeout):
        ChileCrawler(mock_driver)._get_credit_transactions()


def test_logout(mock_driver: mock.MagicMock) -> None:
    mock_driver.find_elements.return_value = False

    ChileCrawler(mock_driver)._logout()

    mock_driver.find_elements.assert_called()
    mock_driver.find_element.assert_called()
    mock_driver.find_element().click.assert_called()


@mock.patch("vigilant.common.values.Timeout.DEFAULT_TIMEOUT", 0.1)
def test_logout_timeout(mock_driver: mock.MagicMock) -> None:
    with pytest.raises(Exception):
        ChileCrawler(mock_driver)._logout()

    mock_driver.find_elements.assert_called()


def test_check_condition_timeout() -> None:
    binary_values: Iterator[str] = cycle((0, 1))
    mock_timeout: float = 3.0

    crawler.check_condition_timeout(lambda: next(binary_values), mock_timeout)


def test_check_condition_timeout_not_met() -> None:
    binary_values: Iterator[str] = cycle((0, 1))
    mock_timeout: float = 0.1

    with pytest.raises(TimeoutError):
        crawler.check_condition_timeout(lambda: next(binary_values), mock_timeout)
