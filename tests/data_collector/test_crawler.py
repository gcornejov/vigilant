from itertools import cycle
from pathlib import Path
from typing import Iterator
from unittest import mock

import pytest

from vigilant.common.exceptions import DownloadTimeout
from vigilant.common.values import Documents, IOResources
from vigilant.data_collector import crawler
from vigilant.data_collector.crawler import ChileCrawler


@mock.patch("vigilant.data_collector.crawler.ChileCrawler._login")
@mock.patch("vigilant.data_collector.crawler.ChileCrawler._get_current_amount")
@mock.patch(
    "vigilant.data_collector.crawler.ChileCrawler._get_national_credit_transactions"
)
@mock.patch(
    "vigilant.data_collector.crawler.ChileCrawler._get_international_credit_transactions"
)
@mock.patch("vigilant.data_collector.crawler.ChileCrawler._logout")
def test_crawl(
    _login: mock.MagicMock,
    _get_current_amount: mock.MagicMock,
    _get_national_credit_transactions: mock.MagicMock,
    _get_international_credit_transactions: mock.MagicMock,
    _logout: mock.MagicMock,
    mock_driver: mock.MagicMock,
) -> None:
    ChileCrawler(mock_driver).crawl()

    _login.assert_called_once()
    _get_current_amount.assert_called_once()
    _get_national_credit_transactions.assert_called_once()
    _get_international_credit_transactions.assert_called_once()
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


def test_get_checking_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock
) -> None:
    checking_card_path: Path = tmp_path.joinpath(Documents.CHECKING_CARD.name)
    checking_card_path.write_text("Hesitation is defeat!")

    monkeypatch.setattr(
        "vigilant.common.values.Documents.CHECKING_CARD", checking_card_path
    )

    ChileCrawler(mock_driver)._get_checking_transactions()

    mock_driver.find_element().click.assert_called()


def test_get_national_credit_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock
) -> None:
    original_file: Path = tmp_path.joinpath(Documents.CREDIT_TRANSACTIONS.name)
    renamed_file: Path = tmp_path.joinpath(Documents.NATIONAL_CREDIT.name)
    mock_test: str = "Hesitation is defeat!"
    original_file.write_text(mock_test)

    monkeypatch.setattr(
        "vigilant.common.values.Documents.CREDIT_TRANSACTIONS", original_file
    )
    monkeypatch.setattr(
        "vigilant.common.values.Documents.NATIONAL_CREDIT", renamed_file
    )

    ChileCrawler(mock_driver)._get_national_credit_transactions()

    mock_driver.get.assert_called_once()
    mock_driver.find_element().click.assert_called()

    assert renamed_file.exists() and renamed_file.read_text() == mock_test


def test_get_international_credit_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock
) -> None:
    original_file: Path = tmp_path.joinpath(Documents.CREDIT_TRANSACTIONS.name)
    renamed_file: Path = tmp_path.joinpath(Documents.INTERNATIONAL_CREDIT.name)
    mock_test: str = "Hesitation is defeat!"
    original_file.write_text(mock_test)

    monkeypatch.setattr(
        "vigilant.common.values.Documents.CREDIT_TRANSACTIONS", original_file
    )
    monkeypatch.setattr(
        "vigilant.common.values.Documents.INTERNATIONAL_CREDIT", renamed_file
    )

    ChileCrawler(mock_driver)._get_international_credit_transactions()

    mock_driver.refresh.assert_called_once()
    mock_driver.find_element().click.assert_called()

    assert renamed_file.exists() and renamed_file.read_text() == mock_test


@mock.patch(
    "vigilant.data_collector.crawler.check_condition_timeout",
    mock.Mock(side_effect=TimeoutError),
)
@pytest.mark.parametrize(
    "method",
    (
        "_get_checking_transactions",
        "_get_national_credit_transactions",
        "_get_international_credit_transactions",
    ),
)
def test_download_timeout_exception(mock_driver: mock.MagicMock, method: str) -> None:
    with pytest.raises(DownloadTimeout):
        crawler_method = getattr(ChileCrawler(mock_driver), method)
        crawler_method()


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
