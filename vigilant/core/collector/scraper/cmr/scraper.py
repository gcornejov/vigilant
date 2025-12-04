from contextlib import suppress

from playwright.sync_api import Locator, TimeoutError

from vigilant import logger
from vigilant.common.values import IOResources
from vigilant.core.collector.scraper.cmr.values import (
    Locators,
    Secrets,
)
from vigilant.core.collector.scraper import Scraper


class CMRScraper(Scraper):
    def scrap(self) -> None:
        self._login()
        self._get_credit_transactions()

    def _login(self) -> None:
        """Login to Web portal"""
        logger.info("Logging in ...")

        self.page.goto(Secrets.LOGIN_URL)
        self.page.wait_for_load_state()

        login_btn: Locator = self.page.locator(Locators.LOGIN_FORM_BTN_XPATH)
        login_btn.wait_for(state="visible")
        login_btn.click()

        user_input: Locator = self.page.locator(Locators.USER_INPUT_XPATH).first
        user_input.wait_for(state="visible")
        user_input.fill(Secrets.USERNAME)

        password_input: Locator = self.page.locator(Locators.PASSWORD_INPUT_XPATH).first
        password_input.wait_for(state="visible")
        password_input.fill(Secrets.PASSWORD)

        self.page.locator(Locators.LOGIN_SUBMIT_BTN_ID).first.click()

        self.page.wait_for_url(Secrets.HOME_URL)

    def _get_credit_transactions(self) -> None:
        """Collect current transactions on credit card"""
        BANNER_WAIT_TIMEOUT: float = 3000.0

        logger.info("Getting transactions ...")

        with suppress(TimeoutError):
            self.page.locator(Locators.PROMOTION_BANNER_XPATH).wait_for(
                timeout=BANNER_WAIT_TIMEOUT
            )
            self.page.locator(Locators.CLOSE_BANNER_BTN_CLASS).click()

        self.page.locator(Locators.PRODUCT_BTN_CLASS).click()

        with self.page.expect_download() as download_info:
            self.page.locator(Locators.DOWNLOAD_BTN_CLASS).first.click()

        download_info.value.save_as(
            IOResources.DATA_PATH / IOResources.TRANSACTIONS_FILENAME
        )
