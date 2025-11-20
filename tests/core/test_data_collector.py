from pathlib import Path
from unittest import mock

import pytest

from vigilant.core import data_collector
from vigilant.common.exceptions import DriverException
from vigilant.common.values import IOResources


@pytest.fixture
def mock_page() -> mock.MagicMock:
    return mock.MagicMock()


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


@mock.patch("vigilant.core.data_collector.sync_playwright")
def test_session(
    mock_sync_playwright: mock.MagicMock, mock_page: mock.MagicMock
) -> None:
    mock_browser = mock.MagicMock()
    mock_browser.new_context.return_value.new_page.return_value = mock_page

    mock_playwright_session = mock.MagicMock()
    mock_playwright_session.chromium.launch.return_value = mock_browser

    mock_sync_playwright.return_value.__enter__.return_value = mock_playwright_session

    with data_collector.session() as session:
        assert session == mock_page

    mock_playwright_session.chromium.launch.assert_called_once_with(channel="chrome")
    mock_browser.new_context.assert_called_once_with(
        accept_downloads=True,
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36",
    )
    mock_browser.close.assert_called_once_with()
    mock_page.set_default_timeout.assert_called_once_with(data_collector.WAIT_TIMEOUT)


@mock.patch("vigilant.core.data_collector.sync_playwright")
@mock.patch("vigilant.core.data_collector.take_screenshot")
def test_session_exception(
    mock_take_screenshot: mock.MagicMock, mock_sync_playwright: mock.MagicMock
) -> None:
    mock_browser, mock_playwright_session = mock.MagicMock(), mock.MagicMock()
    mock_playwright_session.chromium.launch.return_value = mock_browser

    mock_playwright_context_manager = mock.MagicMock()
    mock_playwright_context_manager.__enter__.return_value = mock_playwright_session

    mock_sync_playwright.return_value = mock_playwright_context_manager

    with pytest.raises(DriverException):
        with data_collector.session() as _:
            raise Exception

    mock_take_screenshot.assert_called_once()
    mock_browser.close.assert_called_once()


def test_take_screenshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_page: mock.MagicMock
):
    screenshot_filename: str = "test_sc.png"
    screenshot_path: Path = tmp_path / screenshot_filename
    image_data: bytes = b"Hesitation is defeat!"

    mock_page.screenshot.return_value = image_data
    monkeypatch.setattr(
        "vigilant.common.storage.LocalStorage.save_image",
        lambda *_: screenshot_path.write_bytes(image_data),
    )

    data_collector.take_screenshot(mock_page)
    image: bytes = screenshot_path.read_bytes()

    assert screenshot_path.exists() and image == image_data


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
