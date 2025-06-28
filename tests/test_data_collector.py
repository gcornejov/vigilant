from itertools import cycle
from pathlib import Path
from typing import Iterator
from unittest import mock

import pytest

from vigilant import data_collector
from vigilant.common.exceptions import DownloadTimeout
from vigilant.common.values import IOResources


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


def test_clear_resources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tmp_file: Path = tmp_path / "test_file.txt"
    tmp_file.write_text("Hesitation is defeat!")

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    data_collector.clear_resources()

    assert tmp_path.exists() and not any(tmp_path.iterdir())


def test_login(mock_driver: mock.MagicMock) -> None:
    data_collector.login(mock_driver)

    mock_driver.get.assert_called_once()
    mock_driver.find_element.assert_called()
    mock_driver.find_element().send_keys.assert_called()
    mock_driver.find_element().click.assert_called_once()


@pytest.mark.parametrize(
    "found_elements",
    (([]), (["banner"])),
)
def test_get_current_amount(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_driver: mock.MagicMock,
    found_elements: list[str],
) -> None:
    mock_formatted_amount: str = " $1.000"
    mock_amount: str = "1000"

    mock_element = mock.MagicMock()
    mock_element.text = mock_formatted_amount
    mock_driver.find_element.return_value = mock_element

    mock_driver.find_elements.return_value = found_elements

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    data_collector.get_current_amount(mock_driver)
    amount: str = (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).read_text()

    mock_driver.find_elements.assert_called_once()
    mock_driver.find_element.assert_called()
    assert amount == mock_amount


def test_get_credit_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock
) -> None:
    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)
    (tmp_path / "file.xls").write_text("Heasitation is defeat!")

    data_collector.get_credit_transactions(mock_driver)

    mock_driver.get.assert_called_once()


@mock.patch(
    "vigilant.data_collector.check_condition_timeout",
    mock.Mock(side_effect=TimeoutError),
)
def test_get_credit_transactions_exception(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_driver: mock.MagicMock
) -> None:
    with pytest.raises(DownloadTimeout):
        data_collector.get_credit_transactions(mock_driver)


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
        data_collector.check_condition_timeout(
            lambda: next(binary_values), mock_timeout
        )
