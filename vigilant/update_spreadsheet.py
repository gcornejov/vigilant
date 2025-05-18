from pathlib import Path
from typing import Any, Final

import gspread
import google.auth
import pandas as pd
from gspread import Spreadsheet, Worksheet

from vigilant import logger
from vigilant.constants import BalanceSpreadsheet, IOResources


def main() -> None:
    """Load expenses data into a google spreadsheet"""
    current_amount: int = load_amount()
    expenses_filepath: Path = find_expenses_file()

    logger.info("Updating spreadsheet ...")
    expenses: list[list[Any]] = prepare_expenses(expenses_filepath)

    update_balance_spreadsheet(current_amount, expenses)


def load_amount() -> str:
    """Loads amount from file

    Returns:
        str: Amount
    """
    return (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).read_text()


def find_expenses_file() -> Path:
    """Find file path containing the expenses

    Returns:
        Path: Expenses file path
    """
    return next(
        IOResources.DATA_PATH.glob("*.xls")
    )


def prepare_expenses(expenses_filepath: Path) -> list[list[str]]:
    """Load expenses data from file and prepares it to load

    Args:
        expenses_filepath (Path): Expenses file path

    Returns:
        list[list[str]]: Prepared expenses data
    """
    EXPENSES_COLUMNS_INDEX: tuple[str] = (1, 4, 6, 10)
    EXPENSES_COLUMNS_KEYS: tuple[str] = ("date", "description", "location", "amount")
    CARD_PAYMENT_DESC: Final[str] = "TEF PAGO NORMAL"

    expenses: pd.DataFrame = pd.read_excel(
        expenses_filepath,
        sheet_name=0,
        header=17,
        names=EXPENSES_COLUMNS_KEYS,
        usecols=EXPENSES_COLUMNS_INDEX,
    )

    expenses = expenses[
        (~ expenses.description.str.contains(CARD_PAYMENT_DESC))
    ] \
    .fillna("")

    return expenses.values.tolist()


def update_balance_spreadsheet(account_amount: str, expenses: list[list[str]]) -> None:
    """Uploads expenses data into a google spreadsheet

    Args:
        account_amount (str): Account amount
        expenses (list[list[str]]): Expenses list
    """
    scopes: list[str] = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials, _ = google.auth.default(scopes=scopes)
    gc: gspread.Client = gspread.authorize(credentials)

    spreadsheet: Spreadsheet = gc.open_by_key(BalanceSpreadsheet.KEY)
    worksheet: Worksheet = spreadsheet.worksheet(BalanceSpreadsheet.EXPENSES_WORKSHEET_NAME)

    worksheet.update_acell(BalanceSpreadsheet.AMOUNT_CELL, account_amount)
    worksheet.update(expenses, BalanceSpreadsheet.EXPENSES_CELL)


if __name__ == "__main__":
    main()
