from itertools import cycle
from pathlib import Path
from typing import Iterator
from unittest import mock

import pytest
from selenium.webdriver import ChromeOptions

from vigilant import data_collector
from vigilant.constants import IOResources


@pytest.fixture
def mock_driver():
    return mock.MagicMock()

@mock.patch("vigilant.data_collector.driver_session")
@mock.patch("vigilant.data_collector.clear_resources")
@mock.patch("vigilant.data_collector.login")
@mock.patch("vigilant.data_collector.get_current_amount")
@mock.patch("vigilant.data_collector.get_credit_transactions")
@mock.patch("vigilant.data_collector.logout")
def test_main(
    logout: mock.MagicMock,
    get_credit_transactions: mock.MagicMock,
    get_current_amount: mock.MagicMock,
    login: mock.MagicMock,
    clear_resources: mock.MagicMock,
    driver_session: mock.MagicMock,
) -> None:
    data_collector.main()

    driver_session.assert_called_once()
    clear_resources.assert_called_once()
    login.assert_called_once()
    get_current_amount.assert_called_once()
    get_credit_transactions.assert_called_once()
    logout.assert_called_once()


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

    monkeypatch.setattr("vigilant.constants.IOResources.DATA_PATH", tmp_path)

    options = data_collector.build_driver_options()
    preferences = options.experimental_options["prefs"].items()

    assert isinstance(options, ChromeOptions)
    assert all([expect_pref in preferences for expect_pref in expected_preferences])
    assert all([expect_args in options.arguments for expect_args in expected_arguments])


@mock.patch("vigilant.data_collector.Chrome")
def test_driver_session(mock_driver_class: mock.MagicMock) -> None:
    mock_driver_class.return_value = mock.MagicMock()

    with data_collector.driver_session() as driver: ...

    driver.implicitly_wait.assert_called_once()
    driver.set_window_size.assert_called_once_with(1920, 1080)
    driver.quit.assert_called_once()


@mock.patch("vigilant.data_collector.Chrome")
@mock.patch("vigilant.data_collector.take_screenshot")
def test_driver_session_exception(mock_driver_class: mock.MagicMock, take_screenshot: mock.MagicMock) -> None:
    mock_driver_class.return_value = mock.MagicMock()

    with pytest.raises(Exception):
        with data_collector.driver_session() as driver:
            raise Exception

    take_screenshot.assert_called_once()
    driver.quit.assert_called_once()


def test_take_screenshot(tmp_path: Path, mock_driver: mock.MagicMock):
    screenshot_filename: str = "test_sc.png"
    screenshot_path: Path = tmp_path / screenshot_filename

    mock_driver.get_screenshot_as_file = lambda _: screenshot_path.write_text("Hesitation is defeat!")

    data_collector.take_screenshot(mock_driver)

    assert screenshot_path.exists()


def test_clear_resources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tmp_file: Path = tmp_path / "test_file.txt"
    tmp_file.write_text("Hesitation is defeat!")

    monkeypatch.setattr("vigilant.constants.IOResources.DATA_PATH", tmp_path)

    data_collector.clear_resources()

    assert (
        tmp_path.exists()
        and not any(tmp_path.iterdir())
    )


def test_login(mock_driver: mock.MagicMock) -> None:
    data_collector.login(mock_driver)

    mock_driver.get.assert_called_once()
    mock_driver.find_element.assert_called()
    mock_driver.find_element().send_keys.assert_called()
    mock_driver.find_element().click.assert_called_once()


def test_get_current_amount(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock) -> None:
    mock_formatted_amount: str = " $1.000"
    mock_amount: str = "1000"

    mock_element = mock.MagicMock()
    mock_element.text = mock_formatted_amount
    mock_driver.find_element = mock.MagicMock(return_value=mock_element)

    monkeypatch.setattr("vigilant.constants.IOResources.DATA_PATH", tmp_path)

    data_collector.get_current_amount(mock_driver)
    amount: str = (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).read_text()

    mock_driver.find_element.assert_called_once()
    assert amount == mock_amount


def test_get_credit_transactions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock) -> None:
    monkeypatch.setattr("vigilant.constants.IOResources.DATA_PATH", tmp_path)
    (tmp_path / "file.xls").write_text("Heasitation is defeat!")

    data_collector.get_credit_transactions(mock_driver)

    mock_driver.get.assert_called_once()


def test_logout(mock_driver: mock.MagicMock) -> None:
    mock_driver.find_elements.return_value = False

    data_collector.logout(mock_driver)

    mock_driver.find_elements.assert_called()
    mock_driver.find_element.assert_called()
    mock_driver.find_element().click.assert_called()


@mock.patch("vigilant.data_collector.DEFAULT_TIMEOUT", 0.1)
def test_logout_timeout(mock_driver: mock.MagicMock) -> None:
    with pytest.raises(Exception):
        data_collector.logout(mock_driver)

    mock_driver.find_elements.assert_called()


def test_check_condition_timeout() -> None:
    binary_values: Iterator[str] = cycle((0, 1))
    mock_timeout: float = 3.0

    data_collector.check_condition_timeout(lambda: next(binary_values), mock_timeout)


def test_check_condition_timeout_not_met() -> None:
    binary_values: Iterator[str] = cycle((0, 1))
    mock_timeout: float = 0.1

    with pytest.raises(TimeoutError):
        data_collector.check_condition_timeout(lambda: next(binary_values), mock_timeout)
