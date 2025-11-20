from pathlib import Path
from unittest import mock

import pytest

from vigilant.common import browser
from vigilant.common.exceptions import DriverException


@mock.patch("vigilant.common.browser.sync_playwright")
def test_session(
    mock_sync_playwright: mock.MagicMock, mock_page: mock.MagicMock
) -> None:
    mock_browser = mock.MagicMock()
    mock_browser.new_context.return_value.new_page.return_value = mock_page

    mock_playwright_session = mock.MagicMock()
    mock_playwright_session.chromium.launch.return_value = mock_browser

    mock_sync_playwright.return_value.__enter__.return_value = mock_playwright_session

    with browser.session() as session:
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
    mock_page.set_default_timeout.assert_called_once_with(browser.WAIT_TIMEOUT)


@mock.patch("vigilant.common.browser.sync_playwright")
@mock.patch("vigilant.common.browser._take_screenshot")
def test_session_exception(
    mock_take_screenshot: mock.MagicMock, mock_sync_playwright: mock.MagicMock
) -> None:
    mock_browser, mock_playwright_session = mock.MagicMock(), mock.MagicMock()
    mock_playwright_session.chromium.launch.return_value = mock_browser

    mock_playwright_context_manager = mock.MagicMock()
    mock_playwright_context_manager.__enter__.return_value = mock_playwright_session

    mock_sync_playwright.return_value = mock_playwright_context_manager

    with pytest.raises(DriverException):
        with browser.session() as _:
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

    browser._take_screenshot(mock_page)
    image: bytes = screenshot_path.read_bytes()

    assert screenshot_path.exists() and image == image_data
