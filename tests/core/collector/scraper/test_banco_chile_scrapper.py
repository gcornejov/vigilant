from pathlib import Path
from unittest import mock

import pytest

from vigilant.core.collector.scraper import BancoChileScraper
from vigilant.core.collector.scraper.banco_chile.values import IOResources


@mock.patch("vigilant.core.collector.scraper.BancoChileScraper._login")
@mock.patch("vigilant.core.collector.scraper.BancoChileScraper._get_current_amount")
@mock.patch(
    "vigilant.core.collector.scraper.BancoChileScraper._get_credit_transactions"
)
def test_navigate(
    _login: mock.MagicMock,
    _get_current_amount: mock.MagicMock,
    _get_credit_transactions: mock.MagicMock,
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
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_page: mock.MagicMock,
) -> None:
    mock_formatted_amount: str = " $1.000"
    mock_amount: str = "1000"

    mock_page.locator.return_value.first.text_content.return_value = (
        mock_formatted_amount
    )

    monkeypatch.setattr(
        "vigilant.core.collector.scraper.banco_chile.values.IOResources.AMOUNT_PATH",
        (tmp_path / "tmp_file"),
    )

    BancoChileScraper(mock_page)._get_current_amount()
    amount: str = IOResources.AMOUNT_PATH.read_text()

    assert amount == mock_amount


def test_get_credit_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_page: mock.MagicMock
) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("Hesitation is defeat!")

    monkeypatch.setattr(
        "vigilant.core.collector.scraper.banco_chile.values.IOResources.TRANSACTIONS_PATH",
        (tmp_path / "tmp_file"),
    )

    mock_download_info = mock.MagicMock()
    mock_page.expect_download.return_value.__enter__.return_value = mock_download_info

    BancoChileScraper(mock_page)._get_credit_transactions()

    mock_page.goto.assert_called_once()
    mock_page.locator().click.assert_called()
    mock_download_info.value.save_as.assert_called_once_with(
        IOResources.TRANSACTIONS_PATH
    )
