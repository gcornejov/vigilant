from contextlib import suppress
from typing import Final

import pandas as pd
from playwright.async_api import Download, Locator, TimeoutError

from vigilant.common.models import AccountData, Transaction
from vigilant.common.spreadsheet import SpreadSheet
from vigilant.common.values import (
    BalanceSpreadsheet,
    IOResources as VigilantIOResources,
)
from vigilant.core.collector.scraper.banco_falabella.values import (
    Locators,
    Secrets,
    IOResources,
)
from vigilant.core.collector.scraper import Scraper


class BancoFalabellaScraper(Scraper):
    identifier: Final[str] = "Falabella"

    async def navigate(self) -> None:
        await self._login()
        await self._get_credit_transactions()
        self._save()

    async def _login(self) -> None:
        """Login to Web portal"""
        self.logger.info("Logging in ...")

        await self.page.goto(Secrets.LOGIN_URL)
        await self.page.wait_for_load_state()

        login_btn: Locator = self.page.locator(Locators.LOGIN_FORM_BTN_XPATH)
        await login_btn.wait_for(state="visible")
        await login_btn.click()

        user_input: Locator = self.page.locator(Locators.USER_INPUT_XPATH).first
        await user_input.wait_for(state="visible")
        await user_input.fill(Secrets.USERNAME)

        password_input: Locator = self.page.locator(Locators.PASSWORD_INPUT_XPATH).first
        await password_input.wait_for(state="visible")
        await password_input.fill(Secrets.PASSWORD)

        await self.page.locator(Locators.LOGIN_SUBMIT_BTN_ID).first.click()

        await self.page.wait_for_url(Secrets.HOME_URL)

    async def _get_credit_transactions(self) -> None:
        """Collect current transactions on credit card"""
        BANNER_WAIT_TIMEOUT: float = 3000.0

        self.logger.info("Getting transactions ...")

        with suppress(TimeoutError):
            await self.page.locator(Locators.PROMOTION_BANNER_XPATH).wait_for(
                timeout=BANNER_WAIT_TIMEOUT
            )
            await self.page.locator(Locators.CLOSE_BANNER_BTN_CLASS).click()

        await self.page.locator(Locators.PRODUCT_BTN_CLASS).click()

        async with self.page.expect_download() as download_info:
            await self.page.locator(Locators.DOWNLOAD_BTN_CLASS).first.click()

        download: Download = await download_info.value
        await download.save_as(self.data_path / IOResources.TRANSACTIONS_FILENAME)

    def _save(self) -> None:
        """Structure and saves collected data in a json file"""
        self.logger.info("Saving data ...")

        EXPENSES_COLUMNS_INDEX: tuple[str] = (0, 1, 4, 5)
        EXPENSES_COLUMNS_KEYS: tuple[str] = (
            "date",
            "description",
            "fees",
            "amount",
        )

        expenses: pd.DataFrame = pd.read_excel(
            self.data_path / IOResources.TRANSACTIONS_FILENAME,
            sheet_name=0,
            header=0,
            names=EXPENSES_COLUMNS_KEYS,
            usecols=EXPENSES_COLUMNS_INDEX,
        )

        spreadsheet = SpreadSheet.load(BalanceSpreadsheet.KEY)
        payment_descriptions: list[str] = [
            desc.pop()
            for desc in spreadsheet.read(
                BalanceSpreadsheet.DATA_WORKSHEET_NAME,
                BalanceSpreadsheet.PAYMENT_DESC_RANGE,
            )
        ]

        expenses = expenses[
            (~expenses.description.isin(payment_descriptions)) & (expenses.fees == 0)
        ].drop(columns=["fees"])
        expenses.insert(loc=2, column="location", value="")
        expenses["date"] = expenses["date"].dt.strftime("%d/%m/%Y")

        account_data = AccountData(
            identifier=self.identifier,
            amount=0,
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
