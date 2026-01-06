from pathlib import Path
from typing import Any
from unittest import mock

import pandas as pd
import pytest

from vigilant.core import update_spreadsheet
from vigilant.common.values import BalanceSpreadsheet
from vigilant.core.collector.scraper.banco_chile.values import IOResources


@mock.patch("vigilant.core.update_spreadsheet.SpreadSheet")
@mock.patch("vigilant.core.update_spreadsheet.update_balance_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    SpreadSheet: mock.MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_amount: int = 1000
    mock_expenses: list[list[Any]] = [["store", 100]]

    mock_spreadsheet = mock.MagicMock()
    SpreadSheet.load.return_value = mock_spreadsheet

    monkeypatch.setattr(
        "vigilant.core.update_spreadsheet.load_amount", lambda: mock_amount
    )
    monkeypatch.setattr(
        "vigilant.core.update_spreadsheet.prepare_expenses", lambda *_: mock_expenses
    )

    update_spreadsheet.main()

    SpreadSheet.load.assert_called_once_with(BalanceSpreadsheet.KEY)
    mock_spreadsheet.read.assert_called_once_with(
        BalanceSpreadsheet.DATA_WORKSHEET_NAME, BalanceSpreadsheet.PAYMENT_DESC_RANGE
    )
    update_balance_spreadsheet.assert_called_once_with(
        mock_spreadsheet, mock_amount, mock_expenses
    )


def test_load_amount(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_amount: int = 1000

    monkeypatch.setattr(
        "vigilant.core.collector.scraper.banco_chile.values.IOResources.AMOUNT_PATH",
        (tmp_path / "tmp_file"),
    )
    IOResources.AMOUNT_PATH.write_text(str(mock_amount))

    amount: str = update_spreadsheet.load_amount()

    assert amount == mock_amount


@mock.patch("vigilant.core.update_spreadsheet.pd.read_excel")
def test_prepare_expenses(
    mock_pd_read_excel: mock.MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_cols_keys: tuple[str] = ("date", "description", "location", "amount")
    mock_cols_index: tuple[str] = (1, 4, 6, 10)

    mock_data: list[list[Any]] = [
        ["1999/12/31", "Clothes", "Santiago", 25000],
        ["1999/12/04", "TEF PAGO NORMAL", "Santiago", -120000],
        ["1999/12/24", "Food", None, 40000],
        ["1999/12/04", "Pago Pesos TAR", "Santiago", -88000],
    ]
    mock_data_df = pd.DataFrame(mock_data, columns=mock_cols_keys)

    mock_payment_description: list[str] = ["TEF PAGO NORMAL", "Pago Pesos TAR"]

    mock_expenses: list[list[Any]] = [
        ["1999/12/31", "Clothes", "Santiago", 25000],
        ["1999/12/24", "Food", "", 40000],
    ]

    mock_pd_read_excel.return_value = mock_data_df

    monkeypatch.setattr(
        "vigilant.core.collector.scraper.banco_chile.values.IOResources.TRANSACTIONS_PATH",
        Path("/"),
    )

    expenses: list[list[Any]] = update_spreadsheet.prepare_expenses(
        mock_payment_description
    )

    mock_pd_read_excel.assert_called_once_with(
        Path("/"),
        sheet_name=0,
        header=17,
        names=mock_cols_keys,
        usecols=mock_cols_index,
    )
    assert expenses == mock_expenses


@mock.patch("vigilant.core.update_spreadsheet.SpreadSheet")
def test_update_balance_spreadsheet(SpreadSheet: mock.MagicMock) -> None:
    mock_spreadsheet = mock.MagicMock()
    SpreadSheet.load.return_value = mock_spreadsheet

    update_spreadsheet.update_balance_spreadsheet(mock_spreadsheet, 0, [[]])

    mock_spreadsheet.write.assert_called()
