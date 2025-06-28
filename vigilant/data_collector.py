import random
import shutil
import time
from collections.abc import Callable
from typing import Final

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from vigilant import logger
from vigilant.common.driver import driver_session
from vigilant.common.exceptions import DownloadTimeout
from vigilant.common.storage import GoogleCloudStorage, LocalStorage, Storage
from vigilant.common.values import (
    Environment,
    IOResources,
    Locators,
    Secrets,
    StorageLocation,
)

DEFAULT_TIMEOUT: Final[float] = 15.0
DEFAULT_DOWNLOAD_TIMEOUT: Final[float] = 3.0

storage: Storage = (
    GoogleCloudStorage()
    if Environment.STORAGE_LOCATION == StorageLocation.GCS
    else LocalStorage()
)


def main() -> None:
    """Collect account data"""
    with driver_session(DEFAULT_TIMEOUT, storage) as driver:
        clear_resources()

        logger.info("Logging in ...")
        login(driver)

        logger.info("Getting current amount ...")
        get_current_amount(driver)

        logger.info("Getting transactions ...")
        get_credit_transactions(driver)

        logger.info("Logging out ...")
        logout(driver)


def clear_resources() -> None:
    """Setup resources directory for data persistence"""
    shutil.rmtree(IOResources.DATA_PATH, ignore_errors=True)
    IOResources.DATA_PATH.mkdir(parents=True, exist_ok=True)


def login(driver: WebDriver) -> None:
    """Login to Web portal

    Args:
        driver (WebDriver): Chrome driver object
    """
    driver.get(Secrets.LOGIN_URL)
    driver.find_element(By.ID, Locators.USER_INPUT_ID).send_keys(Secrets.USERNAME)
    driver.find_element(By.ID, Locators.PASSWORD_INPUT_ID).send_keys(Secrets.PASSWORD)
    driver.find_element(By.ID, Locators.LOGIN_BTN_ID).click()


def get_current_amount(driver: WebDriver) -> None:
    """Collect current account amount and save it in a file

    Args:
        driver (WebDriver): Chrome driver object
    """
    if driver.find_elements(By.CLASS_NAME, Locators.PROMOTION_BANNER_CLASS):
        driver.find_element(By.XPATH, Locators.BANNER_CLOSE_BTN_XPATH).click()

    account_amount: str = driver.find_element(
        By.CLASS_NAME, Locators.AMOUNT_TEXT_CLASS
    ).text
    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(
        account_amount.replace(".", "").replace("$", "").strip()
    )


def get_credit_transactions(driver: WebDriver) -> None:
    """Collect current transactions on credit card

    Args:
        driver (WebDriver): Chrome driver object
    """
    driver.get(Secrets.CREDIT_TRANSACTIONS_URL)

    driver.find_element(By.XPATH, Locators.DOWNLOAD_GROUP_BTN_XPATH).click()
    driver.find_element(By.XPATH, Locators.DOWNLOAD_BTN_XPATH).click()

    try:
        check_condition_timeout(
            lambda: list(IOResources.DATA_PATH.glob("*.xls")), DEFAULT_DOWNLOAD_TIMEOUT
        )
    except TimeoutError:
        raise DownloadTimeout(DEFAULT_DOWNLOAD_TIMEOUT)


def logout(driver: WebDriver) -> None:
    """Logout from Web portal

    Args:
        driver (WebDriver): Chrome driver object
    """
    wait = WebDriverWait(driver, timeout=DEFAULT_TIMEOUT)
    wait.until_not(
        lambda _: driver.find_elements(By.CLASS_NAME, Locators.DOWNLOAD_TOAST_CLASS)
    )

    driver.find_element(By.CLASS_NAME, Locators.LOGOUT_BTN_CLASS).click()


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


if __name__ == "__main__":
    main()
