from pathlib import Path
from typing import Any
from unittest import mock

import pandas as pd
import pytest

from vigilant import update_spreadsheet
from vigilant.common.values import Documents, IOResources


@mock.patch("vigilant.update_spreadsheet.update_balance_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_amount: int = 1000
    mock_expenses: list[list[Any]] = [["store", 100]]

    monkeypatch.setattr("vigilant.update_spreadsheet.load_amount", lambda: mock_amount)
    monkeypatch.setattr(
        "vigilant.update_spreadsheet.prepare_expenses", lambda: mock_expenses
    )

    update_spreadsheet.main()

    update_balance_spreadsheet.assert_called_once_with(mock_amount, mock_expenses)


def test_load_amount(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_amount: str = "1000"

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)
    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(mock_amount)

    amount: str = update_spreadsheet.load_amount()

    assert amount == mock_amount


@mock.patch("vigilant.update_spreadsheet.pd.read_excel")
def test_prepare_expenses(mock_pd_read_excel: mock.MagicMock) -> None:
    mock_cols_keys: tuple[str] = ("date", "description", "location", "amount")
    mock_cols_index: tuple[str] = (1, 4, 6, 10)

    mock_data: list[list[Any]] = [
        ["1999/12/31", "Clothes", "Santiago", 25000],
        ["1999/12/04", "TEF PAGO NORMAL", "Santiago", -120000],
        ["1999/12/24", "Food", None, 40000],
        ["1999/12/04", "Pago Pesos TAR", "Santiago", -88000],
    ]
    mock_data_df = pd.DataFrame(mock_data, columns=mock_cols_keys)

    mock_expenses: list[list[Any]] = [
        ["1999/12/31", "Clothes", "Santiago", 25000],
        ["1999/12/24", "Food", "", 40000],
    ]

    mock_pd_read_excel.return_value = mock_data_df

    expenses: list[list[Any]] = update_spreadsheet.prepare_expenses()

    mock_pd_read_excel.assert_called_once_with(
        Documents.NATIONAL_CREDIT,
        sheet_name=0,
        header=17,
        names=mock_cols_keys,
        usecols=mock_cols_index,
    )
    assert expenses == mock_expenses


@mock.patch("vigilant.update_spreadsheet.google.auth")
@mock.patch("vigilant.update_spreadsheet.gspread")
def test_update_balance_spreadsheet(
    mock_gspread: mock.MagicMock, mock_google_auth: mock.MagicMock
) -> None:
    mock_google_auth.default.return_value = ("A", "B")

    update_spreadsheet.update_balance_spreadsheet(0, [[]])

    mock_google_auth.default.assert_called_once()
    mock_gspread.authorize.assert_called_once()
    mock_gspread.authorize().open_by_key.assert_called_once()
    mock_gspread.authorize().open_by_key().worksheet.assert_called_once()
    mock_gspread.authorize().open_by_key().worksheet().update_acell.assert_called_once()
    mock_gspread.authorize().open_by_key().worksheet().update.assert_called_once()
