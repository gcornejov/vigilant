import random
import time
from abc import ABC, abstractmethod
from collections.abc import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Keys, ActionChains

from vigilant import logger
from vigilant.common.exceptions import DownloadTimeout
from vigilant.common.values import (
    Documents,
    IOResources,
    Locators,
    Secrets,
    Timeout,
)


class Crawler(ABC):
    driver: WebDriver

    def __init__(self, driver: WebDriver):
        self.driver = driver

    @abstractmethod
    def crawl(self) -> None: ...


class ChileCrawler(Crawler):
    def crawl(self) -> None:
        logger.info("Navigating through 'Banco de Chile' portal ...")

        self._login()
        self._get_current_amount()
        self._get_checking_transactions()
        self._get_national_credit_transactions()
        self._get_international_credit_transactions()
        self._logout()

    def _login(self) -> None:
        """Login to Web portal"""
        logger.info("Logging in ...")

        self.driver.get(Secrets.LOGIN_URL)
        self.driver.find_element(By.ID, Locators.USER_INPUT_ID).send_keys(
            Secrets.USERNAME
        )
        self.driver.find_element(By.ID, Locators.PASSWORD_INPUT_ID).send_keys(
            Secrets.PASSWORD
        )
        self.driver.find_element(By.ID, Locators.LOGIN_BTN_ID).click()

    def _get_current_amount(self) -> None:
        """Collect current account amount and save it in a file"""
        logger.info("Getting current amount ...")

        self.driver.find_element(By.CLASS_NAME, Locators.PROMOTION_BANNER_CLASS)
        ActionChains(self.driver).key_down(Keys.ESCAPE).perform()

        account_amount: str = self.driver.find_element(
            By.CLASS_NAME, Locators.AMOUNT_TEXT_CLASS
        ).text
        IOResources.DATA_PATH.joinpath(IOResources.AMOUNT_FILENAME).write_text(
            account_amount.replace(".", "").replace("$", "").strip()
        )

    def _get_checking_transactions(self) -> None:
        """Collect current transactions on checking account"""
        logger.info("Getting checking account transactions ...")

        self.driver.find_element(By.ID, Locators.CHECKING_ACCOUNT_LINK_ID).click()

        self.driver.find_element(
            By.XPATH, Locators.CHECKING_DOWNLOAD_GROUP_BTN_XPATH
        ).click()
        self.driver.find_element(By.XPATH, Locators.CHECKING_DOWNLOAD_BTN_XPATH).click()

        try:
            check_condition_timeout(
                lambda: Documents.CHECKING_CARD.exists(),
                Timeout.DEFAULT_DOWNLOAD_TIMEOUT,
            )
        except TimeoutError:
            raise DownloadTimeout(Timeout.DEFAULT_DOWNLOAD_TIMEOUT)

    def _get_national_credit_transactions(self) -> None:
        """Collect current national transactions on credit card"""
        logger.info("Getting national credit transactions ...")

        self.driver.get(Secrets.CREDIT_TRANSACTIONS_URL)

        self.driver.find_element(
            By.XPATH, Locators.NATIONAL_CREDIT_DOWNLOAD_GROUP_BTN_XPATH
        ).click()
        self.driver.find_element(By.XPATH, Locators.CREDIT_DOWNLOAD_BTN_XPATH).click()

        try:
            check_condition_timeout(
                lambda: Documents.CREDIT_TRANSACTIONS.exists(),
                Timeout.DEFAULT_DOWNLOAD_TIMEOUT,
            )
            Documents.CREDIT_TRANSACTIONS.rename(Documents.NATIONAL_CREDIT)
        except TimeoutError:
            raise DownloadTimeout(Timeout.DEFAULT_DOWNLOAD_TIMEOUT)

    def _get_international_credit_transactions(self) -> None:
        """Collect current international transactions on credit card"""
        logger.info("Getting international credit transactions ...")

        self.driver.refresh()

        self.driver.find_element(By.ID, Locators.INTERNATIONAL_CREDIT_BTN_ID).click()
        self.driver.find_element(
            By.XPATH, Locators.INTERNATIONAL_CREDIT_DOWNLOAD_GROUP_BTN_XPATH
        ).click()
        self.driver.find_element(By.XPATH, Locators.CREDIT_DOWNLOAD_BTN_XPATH).click()

        try:
            check_condition_timeout(
                lambda: Documents.CREDIT_TRANSACTIONS.exists(),
                Timeout.DEFAULT_DOWNLOAD_TIMEOUT,
            )
            Documents.CREDIT_TRANSACTIONS.rename(Documents.INTERNATIONAL_CREDIT)
        except TimeoutError:
            raise DownloadTimeout(Timeout.DEFAULT_DOWNLOAD_TIMEOUT)

    def _logout(self) -> None:
        """Logout from Web portal"""
        logger.info("Logging out ...")

        wait = WebDriverWait(self.driver, timeout=Timeout.DEFAULT_TIMEOUT)
        wait.until_not(
            lambda _: self.driver.find_elements(
                By.CLASS_NAME, Locators.DOWNLOAD_TOAST_CLASS
            )
        )

        self.driver.find_element(By.CLASS_NAME, Locators.LOGOUT_BTN_CLASS).click()


def check_condition_timeout(condition: Callable, timeout: float) -> None:
    """Evaluate until given condition is met or the timeout is exceeded

    Args:
        condition (Callable): Function which evaluates the desired condition. (Expects to return True when the condition is met)
        timeout (float): Limit time to wait (in seconds).

    Raises:
        TimeoutError: Condition wasn't met in the time frame
    """
    remaining_time: float = timeout

    while not condition():
        attempt_time = time.time()

        wait_sec: float = random.uniform(0.5, 1)
        time.sleep(wait_sec)

        remaining_time -= time.time() - attempt_time
        if remaining_time <= 0:
            raise TimeoutError
