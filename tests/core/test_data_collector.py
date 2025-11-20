from pathlib import Path
from unittest import mock

import pytest

from vigilant.core import data_collector
from vigilant.common.values import IOResources


@mock.patch("vigilant.core.data_collector.session")
@mock.patch("vigilant.core.data_collector.clear_resources")
@mock.patch("vigilant.core.data_collector.login")
@mock.patch("vigilant.core.data_collector.get_current_amount")
@mock.patch("vigilant.core.data_collector.get_credit_transactions")
def test_main(
    get_credit_transactions: mock.MagicMock,
    get_current_amount: mock.MagicMock,
    login: mock.MagicMock,
    clear_resources: mock.MagicMock,
    session: mock.MagicMock,
) -> None:
    data_collector.main()

    session.assert_called_once()
    clear_resources.assert_called_once()
    login.assert_called_once()
    get_current_amount.assert_called_once()
    get_credit_transactions.assert_called_once()


def test_clear_resources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tmp_file: Path = tmp_path / "test_file.txt"
    tmp_file.write_text("Hesitation is defeat!")

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    data_collector.clear_resources()

    assert tmp_path.exists() and not any(tmp_path.iterdir())


def test_login(mock_page: mock.MagicMock) -> None:
    data_collector.login(mock_page)

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

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    data_collector.get_current_amount(mock_page)
    amount: str = (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).read_text()

    assert amount == mock_amount


def test_get_credit_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_page: mock.MagicMock
) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("Hesitation is defeat!")

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    mock_download_info = mock.MagicMock()
    mock_page.expect_download.return_value.__enter__.return_value = mock_download_info

    data_collector.get_credit_transactions(mock_page)

    mock_page.goto.assert_called_once()
    mock_page.locator().click.assert_called()
    mock_download_info.value.save_as.assert_called_once_with(
        IOResources.DATA_PATH / IOResources.TRANSACTIONS_FILENAME
    )
