from contextlib import suppress
from typing import Final

import pandas as pd
from playwright.sync_api import TimeoutError

from vigilant.common.models import AccountData, Transaction
from vigilant.common.spreadsheet import SpreadSheet
from vigilant.common.values import (
    balance_spreadsheet,
    IOResources as VigilantIOResources,
)
from vigilant.core.collector.scraper.banco_chile.values import (
    secrets,
    Locators,
    IOResources,
)
from vigilant.core.collector.scraper import Scraper


class BancoChileScraper(Scraper):
    amount: int
    identifier: Final[str] = "Chile"

    def navigate(self) -> None:
        self._login()
        self._get_current_amount()
        self._get_credit_transactions()
        self._save()

    def _login(self) -> None:
        """Login to Web portal"""
        self.logger.info("Logging in ...")

        self.page.goto(secrets.LOGIN_URL)

        self.page.locator(Locators.USER_INPUT_ID).fill(secrets.USERNAME)
        self.page.locator(Locators.PASSWORD_INPUT_ID).fill(secrets.PASSWORD)
        self.page.locator(Locators.LOGIN_BTN_ID).click()

        self.page.wait_for_url(secrets.HOME_URL)

    def _get_current_amount(self) -> None:
        """Collect current account amount and save it in a file"""
        BANNER_WAIT_TIMEOUT: float = 3000.0

        self.logger.info("Getting current amount ...")

        with suppress(TimeoutError):
            self.page.locator(Locators.PROMOTION_BANNER_CLASS).wait_for(
                timeout=BANNER_WAIT_TIMEOUT
            )
            self.page.keyboard.press("Escape")

        self.amount = int(
            self.page.locator(Locators.AMOUNT_TEXT_CLASS)
            .first.text_content()
            .replace(".", "")
            .replace("$", "")
            .strip()
        )

    def _get_credit_transactions(self) -> None:
        """Collect current transactions on credit card"""
        self.logger.info("Getting transactions ...")

        self.page.goto(secrets.CREDIT_TRANSACTIONS_URL)
        self.page.locator(Locators.DOWNLOAD_GROUP_BTN_XPATH).click()

        with self.page.expect_download() as download_info:
            self.page.locator(Locators.DOWNLOAD_BTN_XPATH).click()

        download_info.value.save_as(self.data_path / IOResources.TRANSACTIONS_FILENAME)

    def _save(self) -> None:
        """Structure and saves collected data in a json file"""
        self.logger.info("Saving data ...")

        EXPENSES_COLUMNS_INDEX: tuple[str] = (1, 4, 6, 10)
        EXPENSES_COLUMNS_KEYS: tuple[str] = (
            "date",
            "description",
            "location",
            "amount",
        )

        expenses: pd.DataFrame = pd.read_excel(
            self.data_path / IOResources.TRANSACTIONS_FILENAME,
            sheet_name=0,
            header=17,
            names=EXPENSES_COLUMNS_KEYS,
            usecols=EXPENSES_COLUMNS_INDEX,
        )

        spreadsheet = SpreadSheet.load(balance_spreadsheet.KEY)
        payment_descriptions: list[str] = [
            desc.pop()
            for desc in spreadsheet.read(
                balance_spreadsheet.DATA_WORKSHEET_NAME,
                balance_spreadsheet.PAYMENT_DESC_RANGE,
            )
        ]

        expenses = expenses[(~expenses.description.isin(payment_descriptions))].fillna(
            ""
        )

        account_data = AccountData(
            identifier=self.identifier,
            amount=self.amount,
            transactions=[
                Transaction(
                    **dict(zip(list(Transaction.model_fields), raw_transaction))
                )
                for raw_transaction in expenses.values.tolist()
            ],
        )

        (VigilantIOResources.OUTPUT_PATH / IOResources.OUTPUT_FILENAME).write_text(
            account_data.model_dump_json()
        )
