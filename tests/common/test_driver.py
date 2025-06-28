from pathlib import Path
from unittest import mock

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ChromeOptions

from vigilant.common import driver
from vigilant.common.exceptions import DriverException
from vigilant.common.values import Timeout


@mock.patch("vigilant.common.driver.Chrome")
@pytest.mark.parametrize(
    "input_timeout, actual_timeout", ((None, Timeout.DEFAULT_TIMEOUT), (1.0, 1.0))
)
def test_driver_session(
    mock_driver_class: mock.MagicMock,
    input_timeout: float | None,
    actual_timeout: float,
) -> None:
    mock_driver_class.return_value = mock.MagicMock()

    with driver.driver_session(input_timeout) as browser_driver:
        ...

    browser_driver.implicitly_wait.assert_called_once_with(actual_timeout)
    browser_driver.set_window_size.assert_called_once_with(1920, 1080)
    browser_driver.quit.assert_called_once()


@mock.patch("vigilant.common.driver.Chrome")
@mock.patch("vigilant.common.driver._take_screenshot")
def test_driver_session_exception(
    mock_driver_class: mock.MagicMock, _take_screenshot: mock.MagicMock
) -> None:
    mock_driver_class.return_value = mock.MagicMock()

    with pytest.raises(DriverException):
        with driver.driver_session() as browser_driver:
            raise WebDriverException

    _take_screenshot.assert_called_once()
    browser_driver.quit.assert_called_once()


def test_build_driver_options(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    expected_preferences: tuple[tuple[str, (bool | str)], ...] = (
        ("download.default_directory", str(tmp_path)),
        ("download.prompt_for_download", False),
        ("download.directory_upgrade", True),
        ("safebrowsing_for_trusted_sources_enabled", False),
        ("safebrowsing.enabled", False),
    )
    expected_arguments: list[str] = [
        "--headless",
        "--no-sandbox",
        "--verbose",
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.92 Safari/537.36",
        "--disable-gpu",
        "--disable-notifications",
        "--disable-dev-shm-usage",
        "--disable-setuid-sandbox",
        "--disable-software-rasterizer",
    ]

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    options = driver._build_driver_options()
    preferences = options.experimental_options["prefs"].items()

    assert isinstance(options, ChromeOptions)
    assert all([expect_pref in preferences for expect_pref in expected_preferences])
    assert all([expect_args in options.arguments for expect_args in expected_arguments])


def test_take_screenshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock
) -> None:
    screenshot_filename: str = "test_sc.png"
    screenshot_path: Path = tmp_path / screenshot_filename
    image_data: bytes = b"Hesitation is defeat!"

    monkeypatch.setattr(
        "vigilant.common.storage.LocalStorage.save_image",
        lambda *_: screenshot_path.write_bytes(image_data),
    )

    mock_driver.get_screenshot_as_png.return_value = image_data

    driver._take_screenshot(mock_driver)
    image: bytes = screenshot_path.read_bytes()

    assert screenshot_path.exists() and image == image_data
