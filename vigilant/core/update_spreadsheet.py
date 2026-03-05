import json
from pathlib import Path

from vigilant import logger
from vigilant.common.models import AccountData, AccountReport
from vigilant.common.spreadsheet import SpreadSheet
from vigilant.common.values import balance_spreadsheet, IOResources


def main() -> None:
    """Load expenses data into a google spreadsheet"""
    spreadsheet = SpreadSheet.load(balance_spreadsheet.KEY)

    update_balance_spreadsheet(spreadsheet, *load_bank_data())


def load_bank_data() -> tuple[int, list[list[str, int]]]:
    """Loads bank data from scrapers output

    Returns:
        tuple[int, list[list[str, int]]]: Accounts amount and transactions list
    """
    files = Path(IOResources.OUTPUT_PATH).glob("*.json")
    report = AccountReport(
        accounts=[AccountData(**json.loads(file.read_text())) for file in files]
    )

    return report.amount, report.transactions


def update_balance_spreadsheet(
    spreadsheet: SpreadSheet, account_amount: str, expenses: list[list[str]]
) -> None:
    """Uploads expenses data into a google spreadsheet

    Args:
        spreadsheet (SpreadSheet): spreadsheet instance
        account_amount (str): Account amount
        expenses (list[list[str]]): Expenses list
    """
    logger.info("Updating spreadsheet ...")

    spreadsheet.write(
        balance_spreadsheet.EXPENSES_WORKSHEET_NAME,
        balance_spreadsheet.AMOUNT_CELL,
        [[account_amount]],
    )
    spreadsheet.write(
        balance_spreadsheet.EXPENSES_WORKSHEET_NAME,
        balance_spreadsheet.EXPENSES_CELL,
        expenses,
    )


if __name__ == "__main__":
    main()
