import shutil
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from typing import Final

from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from vigilant import Locators, Secrets, IOResources

DEFAULT_TIMEOUT: Final[float] = 25.0


def main() -> None:
    with driver_session() as driver:
        clear_resources()

        print("Logging in")
        login(driver)

        print("Getting current amount")
        get_current_amount(driver)

        print("Getting transactions")
        get_credit_transactions(driver)

        print("Logging out")
        logout(driver)


def build_driver_options() -> FirefoxOptions:
    options = FirefoxOptions()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", IOResources.DATA_PATH.as_posix())

    options.add_argument("--headless")

    return options


@contextmanager
def driver_session() -> Generator[WebDriver]:
    options: FirefoxOptions = build_driver_options()

    driver = Firefox(options=options)
    try:
        driver.maximize_window()

        yield driver
    finally:
        driver.quit()


def clear_resources() -> None:
    shutil.rmtree(IOResources.DATA_PATH, ignore_errors=True)
    IOResources.DATA_PATH.mkdir(parents=True, exist_ok=True)


def timeout_retry(timeout: float | None = None) -> Callable:
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs):
            remaining_time: float = timeout or DEFAULT_TIMEOUT
            while remaining_time > 0:
                start_time = time.time()
                try:
                    return function(*args, **kwargs)
                except Exception:
                    remaining_time -= time.time() - start_time
            raise TimeoutError
        return wrapper
    return decorator


def login(driver: WebDriver) -> None:
    driver.get(Secrets.LOGIN_URL)
    driver.find_element(By.ID, Locators.USER_INPUT_ID).send_keys(Secrets.USERNAME)
    driver.find_element(By.ID, Locators.PASSWORD_INPUT_ID).send_keys(Secrets.PASSWORD)
    driver.find_element(By.ID, Locators.LOGIN_BTN_ID).click()

    check_login(driver)


@timeout_retry()
def check_login(driver: WebDriver) -> None:
    if Secrets.HOME_URL in driver.current_url:
        return

    raise Exception


@timeout_retry()
def get_current_amount(driver: WebDriver) -> None:
    account_amount: str = driver.find_element(By.CLASS_NAME, Locators.AMOUNT_TEXT_CLASS).text
    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(account_amount.replace(".", "").replace("$", "").strip())


def get_credit_transactions(driver: WebDriver) -> None:
    driver.get(Secrets.CREDIT_TRANSACTIONS_URL)
    check_credit_transactions(driver)


@timeout_retry()
def check_credit_transactions(driver: WebDriver) -> None:
    driver.find_element(By.XPATH, Locators.GROUP_BTN_XPATH).click()
    driver.find_element(By.XPATH, Locators.DOWNLOAD_BTN_XPATH).click()
    time.sleep(1)


@timeout_retry()
def logout(driver: WebDriver) -> None:
    driver.find_element(By.CLASS_NAME, Locators.LOGOUT_BTN_CLASS).click()


if __name__ == "__main__":
    main()
