from pathlib import Path
from typing import Any
from unittest import mock

import pandas as pd
import pytest

from vigilant import update_spreadsheet
from vigilant import IOResources


@mock.patch("vigilant.update_spreadsheet.update_balance_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_amount: int = 1000
    mock_expenses_filepath = Path("/tmp/expenses.xls")
    mock_expenses: list[list[Any]] = [["store", 100]]

    monkeypatch.setattr("vigilant.update_spreadsheet.load_amount", lambda: mock_amount)
    monkeypatch.setattr("vigilant.update_spreadsheet.find_expenses_file", lambda: mock_expenses_filepath)
    monkeypatch.setattr("vigilant.update_spreadsheet.prepare_expenses", lambda _: mock_expenses)

    update_spreadsheet.main()

    update_balance_spreadsheet.assert_called_once_with(mock_amount, mock_expenses)

def test_load_amount(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_amount: str = "1000"

    monkeypatch.setattr("vigilant.constants.IOResources.DATA_PATH", tmp_path)
    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(mock_amount)

    amount: str = update_spreadsheet.load_amount()

    assert amount == mock_amount


def test_find_expenses_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_expenses_file: str = "mock.xls"

    monkeypatch.setattr("vigilant.constants.IOResources.DATA_PATH", tmp_path)
    (tmp_path / mock_expenses_file).write_text("")

    expenses_file: Path = update_spreadsheet.find_expenses_file()

    assert (
        isinstance(expenses_file, Path) and
        expenses_file.name == mock_expenses_file
    )


def test_prepare_expenses(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_data: list[list[Any]] = [
        ["1999/12/31", "Clothes", "Santiago", 25000],
        ["1999/12/04", "TEF PAGO NORMAL", "Santiago", 120000],
        ["1999/12/24", "Food", None, 40000],
    ]
    mock_data_df = pd.DataFrame(mock_data, columns=("date", "description", "location", "amount"))

    mock_expenses: list[list[Any]] = [
        ["1999/12/31", "Clothes", "Santiago", 25000],
        ["1999/12/24", "Food", "", 40000],
    ]

    monkeypatch.setattr("vigilant.update_spreadsheet.pd.read_excel", lambda *args, **kwargs: mock_data_df)

    expenses: list[list[Any]] = update_spreadsheet.prepare_expenses(Path("/"))
    
    assert expenses == mock_expenses


@mock.patch("vigilant.update_spreadsheet.google.auth")
@mock.patch("vigilant.update_spreadsheet.gspread")
def test_update_balance_spreadsheet(mock_gspread: mock.MagicMock, mock_google_auth: mock.MagicMock) -> None:
    mock_google_auth.default.return_value = ("A", "B")

    update_spreadsheet.update_balance_spreadsheet(0, [[]])

    mock_google_auth.default.assert_called_once()
    mock_gspread.authorize.assert_called_once()
    mock_gspread.authorize().open_by_key.assert_called_once()
    mock_gspread.authorize().open_by_key().worksheet.assert_called_once()
    mock_gspread.authorize().open_by_key().worksheet().update_acell.assert_called_once()
    mock_gspread.authorize().open_by_key().worksheet().update.assert_called_once()
