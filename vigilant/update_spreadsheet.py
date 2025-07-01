import google.auth
import gspread

from vigilant import logger
from vigilant.common.values import BalanceSpreadsheet
from vigilant.balance import Balance
from vigilant.transactions import Transactions


def main() -> None:
    """Loads and writes balance into a google spreadsheet"""
    logger.info("Loading balance data ...")
    balance = Balance.collect()

    logger.info("Writing balance into spreadsheet ...")
    write_balance(balance)


def write_balance(balance: Balance) -> None:
    """Progressively write balance data in spread sheet following its concrete
    format. Remaining checking account amount in a cell. The transactions in a
    table separated by a blank row in order.

    1. National Credit
    2. International Credit
    3. Checking Account

    Args:
        balance (Balance): Collection of balance data
    """
    worksheet: gspread.Worksheet = get_worksheet()

    # Account amount
    worksheet.update_acell(BalanceSpreadsheet.AMOUNT_CELL, balance.account_amount)

    trx_idx: int = BalanceSpreadsheet.TRANSACTIONS_ROW
    # National Credit
    trx_idx: int = write_transactions(
        worksheet, balance.national_credit_transactions, trx_idx
    )

    # International Credit
    trx_idx: int = write_separator(worksheet, trx_idx)
    trx_idx: int = write_transactions(
        worksheet, balance.international_credit_transactions, trx_idx
    )

    # Checking
    trx_idx: int = write_separator(worksheet, trx_idx)
    write_transactions(worksheet, balance.checking_account_transactions, trx_idx)


def get_worksheet() -> gspread.Worksheet:
    """Stablish connection with Balance Worksheet

    Returns:
        Worksheet: Worksheet object
    """
    scopes: list[str] = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials, _ = google.auth.default(scopes=scopes)
    gc: gspread.Client = gspread.authorize(credentials)

    spreadsheet: gspread.Spreadsheet = gc.open_by_key(BalanceSpreadsheet.KEY)
    return spreadsheet.worksheet("GastosV2")


def write_transactions(
    worksheet: gspread.Worksheet, data: Transactions, idx: int
) -> int:
    """Writes one block of transactions and increments the row pointer.

    Args:
        worksheet (gspread.Worksheet): Worksheet object
        data (Transactions): Transactions data object
        idx (int): Current row pointer

    Returns:
        int: Updated row pointer before last written transaction
    """
    national_credit = data.to_list()
    worksheet.update(national_credit, BalanceSpreadsheet.TRANSACTIONS_COLUMN % idx)

    return idx + len(national_credit)


def write_separator(worksheet: gspread.Worksheet, idx: int) -> int:
    """Writes separator row

    Args:
        worksheet (gspread.Worksheet): Worksheet object
        idx (int): Current row pointer

    Returns:
        int: Updated row pointer before separator row
    """
    worksheet.update(
        [("", "", "", "", "", "", "")], BalanceSpreadsheet.TRANSACTIONS_COLUMN % idx
    )

    return idx + 1


if __name__ == "__main__":
    main()
