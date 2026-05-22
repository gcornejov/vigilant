from pathlib import Path
from typing import Any
from unittest import mock

import pandas as pd
from playwright.sync_api import TimeoutError

from vigilant.collector.scraper import BancoChileScraper
from vigilant.collector.scraper.banco_chile.values import IOResources


@mock.patch("vigilant.collector.scraper.BancoChileScraper._login")
@mock.patch("vigilant.collector.scraper.BancoChileScraper._get_current_amount")
@mock.patch("vigilant.collector.scraper.BancoChileScraper._get_credit_transactions")
def test_navigate(
    _get_credit_transactions: mock.MagicMock,
    _get_current_amount: mock.MagicMock,
    _login: mock.MagicMock,
    mock_page: mock.MagicMock,
) -> None:
    BancoChileScraper(mock_page).navigate()

    _login.assert_called_once()
    _get_current_amount.assert_called_once()
    _get_credit_transactions.assert_called_once()


def test_login(mock_page: mock.MagicMock) -> None:
    BancoChileScraper(mock_page)._login()

    mock_page.goto.assert_called_once()
    mock_page.locator().fill.assert_called()
    mock_page.locator().click.assert_called_once()
    mock_page.wait_for_url.assert_called_once()


def test_get_current_amount(
    mock_page: mock.MagicMock,
) -> None:
    mock_formatted_amount: str = " $1.000"
    mock_amount: int = 1000

    mock_page.locator.return_value.first.text_content.return_value = (
        mock_formatted_amount
    )

    scraper = BancoChileScraper(mock_page)
    scraper._get_current_amount()

    assert scraper.amount == mock_amount


def test_get_credit_transactions(tmp_path: Path, mock_page: mock.MagicMock) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("Hesitation is defeat!")

    mock_download_info = mock.MagicMock()
    mock_page.expect_download.return_value.__enter__.return_value = mock_download_info

    scraper = BancoChileScraper(mock_page)
    scraper.data_path = tmp_path

    scraper._get_credit_transactions()

    mock_page.goto.assert_called_once()
    mock_page.locator().click.assert_called()
    mock_download_info.value.save_as.assert_called_once_with(
        tmp_path / IOResources.TRANSACTIONS_FILENAME
    )


def test_get_credit_transactions_empty(mock_page: mock.MagicMock) -> None:
    mock_click = mock.MagicMock()
    mock_click.side_effect = TimeoutError("")
    mock_locator = mock.MagicMock()

    mock_locator.click = mock_click
    mock_page.locator.return_value = mock_locator

    scraper = BancoChileScraper(mock_page)

    scraper._get_credit_transactions()

    mock_page.goto.assert_called_once()
    mock_page.locator().click.assert_called_once()
    mock_page.locator().wait_for.assert_called_once()


def test_account_data_property(mock_page: mock.MagicMock) -> None:
    raw_transactions: list[list] = [
        ["31/12/1999", "Clothes", "Santiago", 25000],
        ["24/12/1999", "Food", "", 40000],
    ]

    scraper = BancoChileScraper(mock_page)
    scraper.amount = 789

    with mock.patch.object(
        BancoChileScraper,
        "_load_transactions",
        return_value=raw_transactions,
    ) as load_transactions:
        account_data = scraper.account_data
        account_data_again = scraper.account_data

    load_transactions.assert_called_once()

    assert account_data.identifier == "Chile"
    assert account_data.amount == 789
    assert len(account_data.transactions) == 2
    assert account_data.transactions[0].date == "31/12/1999"
    assert account_data.transactions[0].description == "Clothes"
    assert account_data.transactions[0].location == "Santiago"
    assert account_data.transactions[0].amount == 25000

    assert account_data_again is account_data


@mock.patch("vigilant.collector.scraper.banco_chile.scraper.SpreadSheet")
@mock.patch("vigilant.collector.scraper.banco_chile.scraper.pd.read_excel")
def test_load_transactions(
    mock_pd_read_excel: mock.MagicMock,
    MockSpreadSheet: mock.MagicMock,
    tmp_path: Path,
    mock_page: mock.MagicMock,
) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("dummy")

    mock_cols_keys: tuple[str] = ("date", "description", "location", "amount")
    mock_cols_index: tuple[int, int, int, int] = (1, 4, 6, 10)

    mock_data: list[list[Any]] = [
        ["31/12/1999", "Clothes", "Santiago", 25000],
        ["04/12/1999", "TEF PAGO NORMAL", "Santiago", -120000],
        ["24/12/1999", "Food", None, 40000],
        ["04/12/1999", "Pago Pesos TAR", "Santiago", -88000],
    ]
    mock_data_df = pd.DataFrame(mock_data, columns=mock_cols_keys)

    mock_payment_description: list[list[str]] = [
        ["TEF PAGO NORMAL"],
        ["Pago Pesos TAR"],
    ]

    mock_pd_read_excel.return_value = mock_data_df

    mock_spreadsheet = mock.MagicMock()
    mock_spreadsheet.read.return_value = mock_payment_description
    MockSpreadSheet.load.return_value = mock_spreadsheet

    scraper = BancoChileScraper(mock_page)
    scraper.data_path = tmp_path

    result = scraper._load_transactions()

    mock_pd_read_excel.assert_called_once_with(
        tmp_path / IOResources.TRANSACTIONS_FILENAME,
        sheet_name=0,
        header=17,
        names=mock_cols_keys,
        usecols=mock_cols_index,
    )

    assert result == [
        ["31/12/1999", "Clothes", "Santiago", 25000],
        ["24/12/1999", "Food", "", 40000],
    ]


@mock.patch("vigilant.collector.scraper.banco_chile.scraper.SpreadSheet")
@mock.patch("vigilant.collector.scraper.banco_chile.scraper.pd.read_excel")
def test_load_transactions_empty(
    mock_pd_read_excel: mock.MagicMock,
    MockSpreadSheet: mock.MagicMock,
    tmp_path: Path,
    mock_page: mock.MagicMock,
) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("dummy")

    mock_cols_keys: tuple[str] = ("date", "description", "location", "amount")
    mock_cols_index: tuple[int, int, int, int] = (1, 4, 6, 10)

    mock_data: list[list[Any]] = [
        ["31/12/1999", "TEF PAGO NORMAL", "Santiago", -120000],
        ["04/12/1999", "Pago Pesos TAR", "Santiago", -88000],
    ]
    mock_data_df = pd.DataFrame(mock_data, columns=mock_cols_keys)

    mock_payment_description: list[list[str]] = [
        ["TEF PAGO NORMAL"],
        ["Pago Pesos TAR"],
    ]

    mock_pd_read_excel.return_value = mock_data_df

    mock_spreadsheet = mock.MagicMock()
    mock_spreadsheet.read.return_value = mock_payment_description
    MockSpreadSheet.load.return_value = mock_spreadsheet

    scraper = BancoChileScraper(mock_page)
    scraper.data_path = tmp_path

    result = scraper._load_transactions()

    mock_pd_read_excel.assert_called_once_with(
        tmp_path / IOResources.TRANSACTIONS_FILENAME,
        sheet_name=0,
        header=17,
        names=mock_cols_keys,
        usecols=mock_cols_index,
    )

    assert result == []


@mock.patch("vigilant.collector.scraper.banco_chile.scraper.pd.read_excel")
def test_load_transactions_missing_file(
    mock_pd_read_excel: mock.MagicMock,
    tmp_path: Path,
    mock_page: mock.MagicMock,
) -> None:
    scraper = BancoChileScraper(mock_page)
    scraper.data_path = tmp_path

    result = scraper._load_transactions()

    mock_pd_read_excel.assert_not_called()
    assert result == []
