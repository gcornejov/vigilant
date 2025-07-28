from pathlib import Path
from typing import Any

import pandas as pd

from vigilant import logger
from vigilant.common.spreadsheet import SpreadSheet
from vigilant.common.values import BalanceSpreadsheet, IOResources


def main() -> None:
    """Load expenses data into a google spreadsheet"""
    current_amount: str = load_amount()
    expenses_filepath: Path = find_expenses_file()
    spreadsheet = SpreadSheet.load(BalanceSpreadsheet.KEY)

    payment_descriptions: list[str] = [
        desc.pop()
        for desc in spreadsheet.read(
            BalanceSpreadsheet.DATA_WORKSHEET_NAME,
            BalanceSpreadsheet.PAYMENT_DESC_RANGE,
        )
    ]
    expenses: list[list[Any]] = prepare_expenses(
        expenses_filepath, payment_descriptions
    )

    logger.info("Updating spreadsheet ...")
    update_balance_spreadsheet(spreadsheet, current_amount, expenses)


def load_amount() -> int:
    """Loads checking account amount from file

    Returns:
        int: Checking account amount
    """
    raw_amount: str = (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).read_text()
    return int(raw_amount)


def find_expenses_file() -> Path:
    """Find file path containing the expenses

    Returns:
        Path: Expenses file path
    """
    return next(IOResources.DATA_PATH.glob("*.xls"))


def prepare_expenses(
    expenses_filepath: Path, description_ignore: list[str]
) -> list[list[str]]:
    """Load expenses data from file and prepares it to load

    Args:
        expenses_filepath (Path): Expenses file path
        description_ignore (list[str]): List of restrictions to filter

    Returns:
        list[list[str]]: Prepared expenses data
    """
    EXPENSES_COLUMNS_INDEX: tuple[str] = (1, 4, 6, 10)
    EXPENSES_COLUMNS_KEYS: tuple[str] = ("date", "description", "location", "amount")

    expenses: pd.DataFrame = pd.read_excel(
        expenses_filepath,
        sheet_name=0,
        header=17,
        names=EXPENSES_COLUMNS_KEYS,
        usecols=EXPENSES_COLUMNS_INDEX,
    )

    expenses = expenses[(~expenses.description.isin(description_ignore))].fillna("")

    return expenses.values.tolist()


def update_balance_spreadsheet(
    spreadsheet: SpreadSheet, account_amount: str, expenses: list[list[str]]
) -> None:
    """Uploads expenses data into a google spreadsheet

    Args:
        spreadsheet (SpreadSheet): spreadsheet instance
        account_amount (str): Account amount
        expenses (list[list[str]]): Expenses list
    """
    spreadsheet.write(
        BalanceSpreadsheet.EXPENSES_WORKSHEET_NAME,
        BalanceSpreadsheet.AMOUNT_CELL,
        [[account_amount]],
    )
    spreadsheet.write(
        BalanceSpreadsheet.EXPENSES_WORKSHEET_NAME,
        BalanceSpreadsheet.EXPENSES_CELL,
        expenses,
    )


if __name__ == "__main__":
    main()
