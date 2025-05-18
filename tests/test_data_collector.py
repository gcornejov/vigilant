import time
from collections.abc import Generator
from pathlib import Path
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

    with data_collector.driver_session() as driver:
        driver.maximize_window.assert_called_once()

    driver.quit.assert_called_once()


def test_clear_resources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tmp_file: Path = tmp_path / "test_file.txt"
    tmp_file.write_text("Heasitation is defeat!")

    monkeypatch.setattr("vigilant.constants.IOResources.DATA_PATH", tmp_path)

    data_collector.clear_resources()

    assert (
        tmp_path.exists()
        and not any(tmp_path.iterdir())
    )


def test_timeout_retry() -> None:
    numbers: Generator[int] = iter(range(2))

    @data_collector.timeout_retry()
    def dummy_divider() -> float:
        d: int = next(numbers)

        return 1/d

    dummy_divider()


def test_timeout_retry_exception() -> None:
    numbers: Generator[int] = iter(range(2))

    @data_collector.timeout_retry(0.1)
    def dummy_divider() -> float:
        time.sleep(0.3)
        d: int = next(numbers)

        return 1/d

    with pytest.raises(TimeoutError):
        dummy_divider()


@mock.patch("vigilant.data_collector.check_login")
def test_login(check_login: mock.MagicMock, mock_driver: mock.MagicMock) -> None:
    data_collector.login(mock_driver)

    mock_driver.get.assert_called_once()
    mock_driver.find_element.assert_called()
    mock_driver.find_element().send_keys.assert_called()
    mock_driver.find_element().click.assert_called_once()

    check_login.assert_called_once()


def test_check_login(monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock) -> None:
    mock_portal_home_url: str = "https://portal.home.com"

    monkeypatch.setenv("PORTAL_HOME_URL", mock_portal_home_url)
    mock_driver.current_url = mock_portal_home_url

    data_collector.check_login(mock_driver)


@mock.patch("vigilant.data_collector.DEFAULT_TIMEOUT", 0.3)
def test_check_login_exception(mock_driver: mock.MagicMock) -> None:
    with pytest.raises(Exception):
        data_collector.check_login(mock_driver)


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


@mock.patch("vigilant.data_collector.check_credit_transactions")
def test_get_credit_transactions(check_credit_transactions: mock.MagicMock, mock_driver: mock.MagicMock) -> None:
    data_collector.get_credit_transactions(mock_driver)

    mock_driver.get.assert_called_once()
    check_credit_transactions.assert_called_once()


def test_check_credit_transactions(mock_driver: mock.MagicMock) -> None:
    data_collector.check_credit_transactions(mock_driver)

    mock_driver.find_element.assert_called()
    mock_driver.find_element().click.assert_called()


def test_logout(mock_driver: mock.MagicMock) -> None:
    data_collector.logout(mock_driver)

    mock_driver.find_element.assert_called()
    mock_driver.find_element().click.assert_called()
