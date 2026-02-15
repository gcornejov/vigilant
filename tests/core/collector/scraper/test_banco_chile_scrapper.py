import json
from pathlib import Path
from typing import Any
from unittest import mock

import pytest
import pandas as pd

from vigilant.core.collector.scraper import BancoChileScraper
from vigilant.core.collector.scraper.banco_chile.values import IOResources


@pytest.fixture
def mock_bank_chile_data() -> dict:
    return json.loads(Path("tests/resources/bank_chile.json").read_text())


@pytest.mark.asyncio
@mock.patch("vigilant.core.collector.scraper.BancoChileScraper._login")
@mock.patch("vigilant.core.collector.scraper.BancoChileScraper._get_current_amount")
@mock.patch(
    "vigilant.core.collector.scraper.BancoChileScraper._get_credit_transactions"
)
@mock.patch("vigilant.core.collector.scraper.BancoChileScraper._save")
async def test_navigate(
    _save: mock.MagicMock,
    _get_credit_transactions: mock.MagicMock,
    _get_current_amount: mock.MagicMock,
    _login: mock.MagicMock,
    mock_page: mock.MagicMock,
) -> None:
    # Configure mocks to be async
    _login.side_effect = None
    _login.return_value = None
    _get_current_amount.side_effect = None
    _get_current_amount.return_value = None
    _get_credit_transactions.side_effect = None
    _get_credit_transactions.return_value = None
    _save.return_value = None

    await BancoChileScraper(mock_page).navigate()

    _save.assert_called_once()
    _login.assert_called_once()
    _get_current_amount.assert_called_once()
    _get_credit_transactions.assert_called_once()


@pytest.mark.asyncio
async def test_login(mock_page: mock.MagicMock) -> None:
    mock_page.goto = mock.AsyncMock()
    mock_page.locator = mock.MagicMock()
    mock_page.locator().fill = mock.AsyncMock()
    mock_page.locator().click = mock.AsyncMock()
    mock_page.wait_for_url = mock.AsyncMock()

    await BancoChileScraper(mock_page)._login()

    mock_page.goto.assert_called_once()
    mock_page.locator().fill.assert_called()
    mock_page.locator().click.assert_called_once()
    mock_page.wait_for_url.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_amount(
    mock_page: mock.MagicMock,
) -> None:
    mock_formatted_amount: str = " $1.000"
    mock_amount: int = 1000

    # Mock the locator chain for async
    mock_locator = mock.MagicMock()
    mock_first = mock.MagicMock()

    # text_content() is an async function that we need to mock
    async def mock_text_content():
        return mock_formatted_amount

    mock_first.text_content = mock.MagicMock(side_effect=mock_text_content)
    mock_locator.first = mock_first
    mock_locator.wait_for = mock.AsyncMock()  # Mock the wait_for async method
    mock_page.locator = mock.MagicMock(return_value=mock_locator)
    mock_page.keyboard = mock.MagicMock()
    mock_page.keyboard.press = mock.AsyncMock()

    scraper = BancoChileScraper(mock_page)
    await scraper._get_current_amount()

    assert scraper.amount == mock_amount


@pytest.mark.asyncio
async def test_get_credit_transactions(
    tmp_path: Path, mock_page: mock.MagicMock
) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("Hesitation is defeat!")

    mock_download_info = mock.MagicMock()
    mock_download_value = mock.MagicMock()
    mock_download_value.save_as = mock.AsyncMock()
    mock_download_info.value = mock_download_value

    async_context = mock.MagicMock()
    async_context.__aenter__ = mock.AsyncMock(return_value=mock_download_info)
    async_context.__aexit__ = mock.AsyncMock(return_value=None)

    mock_page.goto = mock.AsyncMock()
    mock_page.locator = mock.MagicMock()
    mock_page.locator().click = mock.AsyncMock()
    mock_page.expect_download = mock.MagicMock(return_value=async_context)

    scraper = BancoChileScraper(mock_page)
    scraper.data_path = tmp_path

    await scraper._get_credit_transactions()

    mock_page.goto.assert_called_once()
    mock_page.locator().click.assert_called()
    mock_download_value.save_as.assert_called_once_with(
        tmp_path / IOResources.TRANSACTIONS_FILENAME
    )


@mock.patch("vigilant.core.collector.scraper.banco_chile.scraper.SpreadSheet")
@mock.patch("vigilant.core.collector.scraper.banco_chile.scraper.pd.read_excel")
def test_save(
    mock_pd_read_excel: mock.MagicMock,
    MockSpreadSheet: mock.MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_page: mock.MagicMock,
    mock_bank_chile_data: dict,
) -> None:
    mock_cols_keys: tuple[str] = ("date", "description", "location", "amount")
    mock_cols_index: tuple[str] = (1, 4, 6, 10)

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

    monkeypatch.setattr(
        "vigilant.common.values.IOResources.OUTPUT_PATH",
        tmp_path,
    )
    monkeypatch.setattr(
        "vigilant.core.collector.scraper.banco_chile.values.IOResources.OUTPUT_FILENAME",
        "bank_data.json",
    )

    scraper = BancoChileScraper(mock_page)
    scraper.data_path = Path("/")
    scraper.amount = 123456

    scraper._save()

    bank_output: dict = json.loads(Path(tmp_path / "bank_data.json").read_text())

    mock_pd_read_excel.assert_called_once_with(
        Path("/", IOResources.TRANSACTIONS_FILENAME),
        sheet_name=0,
        header=17,
        names=mock_cols_keys,
        usecols=mock_cols_index,
    )
    assert bank_output == mock_bank_chile_data
