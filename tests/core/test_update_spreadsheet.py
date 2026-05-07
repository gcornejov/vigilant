import json
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

from vigilant.core import update_spreadsheet
from vigilant.common.values import balance_spreadsheet


@pytest.fixture
def transformed_data_output() -> dict:
    return json.loads(Path("tests/resources/transformed_bank_data.json").read_text())


@mock.patch("vigilant.core.update_spreadsheet.SpreadSheet")
@mock.patch("vigilant.core.update_spreadsheet.update_balance_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    MockSpreadSheet: mock.MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_amount: int = 1000
    mock_expenses: list[list[Any]] = [["store", 100]]

    mock_spreadsheet = mock.MagicMock()
    MockSpreadSheet.load.return_value = mock_spreadsheet

    monkeypatch.setattr(
        "vigilant.core.update_spreadsheet.load_bank_data",
        lambda: (mock_amount, mock_expenses),
    )

    update_spreadsheet.main()

    MockSpreadSheet.load.assert_called_once_with(balance_spreadsheet.KEY)
    update_balance_spreadsheet.assert_called_once_with(
        mock_spreadsheet, mock_amount, mock_expenses
    )


def test_load_bank_data(
    monkeypatch: pytest.MonkeyPatch, transformed_data_output: dict
) -> None:
    monkeypatch.setattr(
        "vigilant.common.values.IOResources.OUTPUT_PATH",
        Path("tests/resources/scraper_output"),
    )

    amount, transactions = update_spreadsheet.load_bank_data()

    assert amount == transformed_data_output["amount"]
    assert sorted(transactions) == sorted(transformed_data_output["transactions"])


@mock.patch("vigilant.core.update_spreadsheet.SpreadSheet")
def test_update_balance_spreadsheet(MockSpreadSheet: mock.MagicMock) -> None:
    mock_spreadsheet = mock.MagicMock()
    MockSpreadSheet.load.return_value = mock_spreadsheet

    initial_expenses = [["store", 100], ["restaurant", 50]]
    update_spreadsheet.update_balance_spreadsheet(
        mock_spreadsheet, 1000, initial_expenses
    )

    calls = mock_spreadsheet.write.call_args_list
    expenses_call = calls[1]
    written_expenses = expenses_call[0][2]

    assert len(written_expenses) == update_spreadsheet.TRANSACTIONS_COUNT

    mock_spreadsheet.format_currency.assert_called_once_with(
        balance_spreadsheet.EXPENSES_WORKSHEET_NAME,
        balance_spreadsheet.TRANSACTIONS_AMOUNT_RANGE,
    )
