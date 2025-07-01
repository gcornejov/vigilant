from __future__ import annotations

from vigilant.common.values import IOResources
from vigilant.transactions import Checking, InternationalCredit, NationalCredit


class Balance:
    account_amount: str

    checking_account_transactions: Checking
    national_credit_transactions: NationalCredit
    international_credit_transactions: InternationalCredit

    def __init__(
        self,
        account_amount: str,
        checking_account_transactions: Checking,
        national_credit_transactions: NationalCredit,
        international_credit_transactions: InternationalCredit,
    ) -> None:
        """Collection of balance data

        Args:
            account_amount (str): Remaining amount in Checking Account
            checking_account_transactions (Checking): Transactions from Checking Account
            national_credit_transactions (NationalCredit): Transactions from National Credit
            international_credit_transactions (InternationalCredit): Transactions from International Credit
        """
        self.account_amount = account_amount
        self.checking_account_transactions = checking_account_transactions
        self.national_credit_transactions = national_credit_transactions
        self.international_credit_transactions = international_credit_transactions

    @classmethod
    def collect(cls) -> Balance:
        """Loads balance data and saves in an object

        Returns:
            Balance: Object containing loaded balance data
        """
        return Balance(
            cls._load_account_amount(),
            *cls._load_transactions(),
        )

    @staticmethod
    def _load_account_amount() -> str:
        """Load Checking account amount from file

        Returns:
            str: Remaining amount on Checking account
        """
        return IOResources.DATA_PATH.joinpath(IOResources.AMOUNT_FILENAME).read_text()

    @staticmethod
    def _load_transactions() -> tuple[Checking, NationalCredit, InternationalCredit]:
        """Load account transactions

        Returns:
            tuple[Checking, NationalCredit, InternationalCredit]: Collection of transactions from each origin
        """
        checking = Checking()
        national_credit = NationalCredit()
        international_credit = InternationalCredit()

        checking.load()
        national_credit.load()
        international_credit.load()

        return checking, national_credit, international_credit
