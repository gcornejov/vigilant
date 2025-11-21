from contextlib import suppress

from playwright.sync_api import TimeoutError

from vigilant import logger
from vigilant.common.values import IOResources
from vigilant.core.collector.scraper.banco_chile.values import (
    Locators,
    Secrets,
)
from vigilant.core.collector.scraper import Scraper


class BancoChileScraper(Scraper):
    def navigate(self) -> None:
        self._login()
        self._get_current_amount()
        self._get_credit_transactions()

    def _login(self) -> None:
        """Login to Web portal"""
        logger.info("Logging in ...")

        self.page.goto(Secrets.LOGIN_URL)

        self.page.locator(Locators.USER_INPUT_ID).fill(Secrets.USERNAME)
        self.page.locator(Locators.PASSWORD_INPUT_ID).fill(Secrets.PASSWORD)
        self.page.locator(Locators.LOGIN_BTN_ID).click()

        self.page.wait_for_url(Secrets.HOME_URL)

    def _get_current_amount(self) -> None:
        """Collect current account amount and save it in a file"""
        BANNER_WAIT_TIMEOUT: float = 3000.0

        logger.info("Getting current amount ...")

        with suppress(TimeoutError):
            self.page.locator(Locators.PROMOTION_BANNER_CLASS).wait_for(
                timeout=BANNER_WAIT_TIMEOUT
            )
            self.page.keyboard.press("Escape")

        account_amount: str = self.page.locator(
            Locators.AMOUNT_TEXT_CLASS
        ).first.text_content()
        (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(
            account_amount.replace(".", "").replace("$", "").strip()
        )

    def _get_credit_transactions(self) -> None:
        """Collect current transactions on credit card"""
        logger.info("Getting transactions ...")

        self.page.goto(Secrets.CREDIT_TRANSACTIONS_URL)
        self.page.locator(Locators.DOWNLOAD_GROUP_BTN_XPATH).click()

        with self.page.expect_download() as download_info:
            self.page.locator(Locators.DOWNLOAD_BTN_XPATH).click()

        download_info.value.save_as(
            IOResources.DATA_PATH / IOResources.TRANSACTIONS_FILENAME
        )
