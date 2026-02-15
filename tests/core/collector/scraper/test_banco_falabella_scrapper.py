import json
from pathlib import Path
from typing import Any
from unittest import mock

import pandas as pd
import pytest

from vigilant.core.collector.scraper.banco_falabella.values import Locators, IOResources
from vigilant.core.collector.scraper import BancoFalabellaScraper


@pytest.fixture
def mock_bank_falabella_data() -> dict:
    return json.loads(Path("tests/resources/bank_falabella.json").read_text())


@pytest.mark.asyncio
@mock.patch("vigilant.core.collector.scraper.BancoFalabellaScraper._login")
@mock.patch(
    "vigilant.core.collector.scraper.BancoFalabellaScraper._get_credit_transactions"
)
@mock.patch("vigilant.core.collector.scraper.BancoFalabellaScraper._save")
async def test_navigate(
    _save: mock.MagicMock,
    _get_credit_transactions: mock.MagicMock,
    _login: mock.MagicMock,
    mock_page: mock.MagicMock,
) -> None:
    # Configure mocks to be async
    _login.side_effect = None
    _login.return_value = None
    _get_credit_transactions.side_effect = None
    _get_credit_transactions.return_value = None
    _save.return_value = None

    await BancoFalabellaScraper(mock_page).navigate()

    _save.assert_called_once()
    _login.assert_called_once()
    _get_credit_transactions.assert_called_once()


@pytest.mark.asyncio
async def test_login(mock_page: mock.MagicMock) -> None:
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
    mock_page.goto = mock.AsyncMock()
    mock_page.wait_for_load_state = mock.AsyncMock()
    mock_page.wait_for_url = mock.AsyncMock()

    mock_login_btn.wait_for = mock.AsyncMock()
    mock_login_btn.click = mock.AsyncMock()
    mock_user_input.wait_for = mock.AsyncMock()
    mock_user_input.fill = mock.AsyncMock()
    mock_password_input.wait_for = mock.AsyncMock()
    mock_password_input.fill = mock.AsyncMock()
    mock_generic_locator.first = mock.MagicMock()
    mock_generic_locator.first.click = mock.AsyncMock()

    await BancoFalabellaScraper(mock_page)._login()

    mock_page.goto.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once()

    mock_login_btn.wait_for.assert_called_once()
    mock_login_btn.click.assert_called_once()

    mock_user_input.wait_for.assert_called_once()
    mock_user_input.fill.assert_called_once()

    mock_password_input.wait_for.assert_called_once()
    mock_password_input.fill.assert_called_once()

    mock_generic_locator.first.click.assert_called_once()
    mock_page.wait_for_url.assert_called_once()


@pytest.mark.asyncio
async def test_get_credit_transactions(
    tmp_path: Path, mock_page: mock.MagicMock
) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("Hesitation is defeat!")

    mock_download_value = mock.MagicMock()
    mock_download_value.save_as = mock.AsyncMock()

    mock_download_info = mock.MagicMock()
    mock_download_info.value = mock_download_value

    # Create an async context manager
    async def async_cm_enter():
        return mock_download_info

    async def async_cm_exit(*args):
        return None

    async_context = mock.MagicMock()
    async_context.__aenter__ = mock.AsyncMock(side_effect=async_cm_enter)
    async_context.__aexit__ = mock.AsyncMock(side_effect=async_cm_exit)

    mock_page.goto = mock.AsyncMock()

    # Create a proper mock for locator() returns that has all the necessary async methods
    def mock_locator_factory(selector=None):
        locator_mock = mock.MagicMock()
        locator_mock.wait_for = mock.AsyncMock()
        locator_mock.click = mock.AsyncMock()
        # For .first attribute
        first_mock = mock.MagicMock()
        first_mock.click = mock.AsyncMock()
        locator_mock.first = first_mock
        return locator_mock

    mock_page.locator = mock.MagicMock(side_effect=mock_locator_factory)
    mock_page.expect_download = mock.MagicMock(return_value=async_context)

    scraper = BancoFalabellaScraper(mock_page)
    scraper.data_path = tmp_path

    await scraper._get_credit_transactions()

    mock_download_value.save_as.assert_called_once_with(
        tmp_path / IOResources.TRANSACTIONS_FILENAME
    )


@mock.patch("vigilant.core.collector.scraper.banco_falabella.scraper.SpreadSheet")
@mock.patch("vigilant.core.collector.scraper.banco_falabella.scraper.pd.read_excel")
def test_save(
    mock_pd_read_excel: mock.MagicMock,
    MockSpreadSheet: mock.MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_page: mock.MagicMock,
    mock_bank_falabella_data: dict,
) -> None:
    mock_cols_keys: tuple[str] = ("date", "description", "fees", "amount")
    mock_cols_index: tuple[str] = (0, 1, 4, 5)

    mock_data: list[list[Any]] = [
        [pd.to_datetime("1999-12-31"), "Clothes", 0, 25000],
        [pd.to_datetime("1999-12-04"), "PAGO TARJETA CMR", 0, -120000],
        [pd.to_datetime("1999-12-24"), "Food", 0, 40000],
        [pd.to_datetime("1999-12-04"), "Shoes", 4, 33200],
    ]
    mock_data_df = pd.DataFrame(mock_data, columns=mock_cols_keys)

    mock_payment_description: list[list[str]] = [
        ["PAGO TARJETA CMR"],
    ]

    mock_pd_read_excel.return_value = mock_data_df

    mock_spreadsheet = mock.MagicMock()
    mock_spreadsheet.read.return_value = mock_payment_description
    MockSpreadSheet.load.return_value = mock_spreadsheet

    monkeypatch.setattr(
        "vigilant.common.values.IOResources.OUTPUT_PATH",
        tmp_path,
    )
    monkeypatch.setattr(
        "vigilant.core.collector.scraper.banco_falabella.values.IOResources.OUTPUT_FILENAME",
        "bank_data.json",
    )

    scraper = BancoFalabellaScraper(mock_page)
    scraper.data_path = Path("/")

    scraper._save()

    bank_output: dict = json.loads(Path(tmp_path / "bank_data.json").read_text())

    mock_pd_read_excel.assert_called_once_with(
        Path("/", IOResources.TRANSACTIONS_FILENAME),
        sheet_name=0,
        header=0,
        names=mock_cols_keys,
        usecols=mock_cols_index,
    )
    assert bank_output == mock_bank_falabella_data
