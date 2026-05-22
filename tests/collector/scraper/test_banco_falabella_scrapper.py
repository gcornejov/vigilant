from pathlib import Path
from unittest import mock

import pandas as pd

from vigilant.collector.scraper.banco_falabella.values import Locators, IOResources
from vigilant.collector.scraper import BancoFalabellaScraper


@mock.patch("vigilant.collector.scraper.BancoFalabellaScraper._login")
@mock.patch("vigilant.collector.scraper.BancoFalabellaScraper._get_credit_transactions")
def test_navigate(
    _get_credit_transactions: mock.MagicMock,
    _login: mock.MagicMock,
    mock_page: mock.MagicMock,
) -> None:
    BancoFalabellaScraper(mock_page).navigate()

    _login.assert_called_once()
    _get_credit_transactions.assert_called_once()


def test_login(mock_page: mock.MagicMock) -> None:
    mock_login_btn, mock_user_input, mock_password_input, mock_generic_locator = (
        mock.MagicMock(),
        mock.MagicMock(),
        mock.MagicMock(),
        mock.MagicMock(),
    )

    def mock_login_form_locators(mock_selector: str = "") -> mock.MagicMock:
        match mock_selector:
            case Locators.LOGIN_FORM_BTN_XPATH:
                return mock_login_btn
            case Locators.USER_INPUT_XPATH:
                mock_locator = mock.MagicMock()
                mock_locator.first = mock_user_input
                return mock_locator
            case Locators.PASSWORD_INPUT_XPATH:
                mock_locator = mock.MagicMock()
                mock_locator.first = mock_password_input
                return mock_locator
            case Locators.PASSWORD_INPUT_XPATH:
                return mock_password_input
            case _:
                return mock_generic_locator

    mock_page.locator = mock.MagicMock(side_effect=mock_login_form_locators)

    BancoFalabellaScraper(mock_page)._login()

    mock_page.goto.assert_called_once()
    mock_page.wait_for_load_state()

    mock_login_btn.wait_for.assert_called_once()
    mock_login_btn.click.assert_called_once()

    mock_user_input.wait_for.assert_called_once()
    mock_user_input.fill.assert_called_once()

    mock_password_input.wait_for.assert_called_once()
    mock_password_input.fill.assert_called_once()

    mock_generic_locator.first.click.assert_called_once()
    mock_page.wait_for_url.assert_called_once()


def test_get_credit_transactions(tmp_path: Path, mock_page: mock.MagicMock) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("Hesitation is defeat!")

    mock_download_info = mock.MagicMock()
    mock_page.expect_download.return_value.__enter__.return_value = mock_download_info

    scraper = BancoFalabellaScraper(mock_page)
    scraper.data_path = tmp_path

    scraper._get_credit_transactions()

    mock_page.locator().wait_for.assert_called_once()
    mock_page.locator().click.assert_called()
    mock_download_info.value.save_as.assert_called_once_with(
        tmp_path / IOResources.TRANSACTIONS_FILENAME
    )


def test_account_data_property(mock_page: mock.MagicMock) -> None:
    raw_transactions: list[list] = [
        ["31/12/1999", "Clothes", "", 25000],
        ["24/12/1999", "Food", "", 40000],
    ]

    scraper = BancoFalabellaScraper(mock_page)

    with mock.patch.object(
        BancoFalabellaScraper,
        "_load_transactions",
        return_value=raw_transactions,
    ) as load_transactions:
        account_data = scraper.account_data
        account_data_again = scraper.account_data

    load_transactions.assert_called_once()

    assert account_data.identifier == "Falabella"
    assert account_data.amount == 0
    assert len(account_data.transactions) == 2
    assert account_data.transactions[0].date == "31/12/1999"
    assert account_data.transactions[0].description == "Clothes"
    assert account_data.transactions[0].location == ""
    assert account_data.transactions[0].amount == 25000

    assert account_data_again is account_data


@mock.patch("vigilant.collector.scraper.banco_falabella.scraper.SpreadSheet")
@mock.patch("vigilant.collector.scraper.banco_falabella.scraper.pd.read_excel")
def test_load_transactions(
    mock_pd_read_excel: mock.MagicMock,
    MockSpreadSheet: mock.MagicMock,
    tmp_path: Path,
    mock_page: mock.MagicMock,
) -> None:
    mock_cols_keys: tuple[str] = ("date", "description", "fees", "amount")
    mock_cols_index: tuple[int, int, int, int] = (0, 1, 4, 5)

    mock_data: list[list] = [
        [pd.to_datetime("1999-12-31"), "Clothes", 0, 25000],
        [pd.to_datetime("1999-12-04"), "PAGO TARJETA CMR", 0, -120000],
        [pd.to_datetime("1999-12-24"), "Food", 0, 40000],
        [pd.to_datetime("1999-12-04"), "Shoes", 4, 33200],
    ]
    mock_data_df = pd.DataFrame(mock_data, columns=mock_cols_keys)

    mock_payment_description: list[list[str]] = [["PAGO TARJETA CMR"]]

    mock_pd_read_excel.return_value = mock_data_df

    mock_spreadsheet = mock.MagicMock()
    mock_spreadsheet.read.return_value = mock_payment_description
    MockSpreadSheet.load.return_value = mock_spreadsheet

    scraper = BancoFalabellaScraper(mock_page)
    scraper.data_path = tmp_path

    result = scraper._load_transactions()

    mock_pd_read_excel.assert_called_once_with(
        tmp_path / IOResources.TRANSACTIONS_FILENAME,
        sheet_name=0,
        header=0,
        names=mock_cols_keys,
        usecols=mock_cols_index,
    )

    assert result == [
        ["31/12/1999", "Clothes", "", 25000],
        ["24/12/1999", "Food", "", 40000],
    ]
