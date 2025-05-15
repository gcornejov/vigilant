import shutil
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from typing import Final

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from vigilant import Locators, Secrets, IOResources

DEFAULT_TIMEOUT: Final[float] = 25.0


def main() -> None:
    """Collect expenses data"""
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


def build_driver_options() -> ChromeOptions:
    """Setup profile for Chrome instance

    Returns:
        ChromeOptions: Chrome profile object
    """
    options = ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": IOResources.DATA_PATH.as_posix(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--verbose")

    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.92 Safari/537.36")

    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-software-rasterizer")

    return options


@contextmanager
def driver_session() -> Generator[WebDriver]:
    """Creates a driver object to interact with a Chrome Browser instance.
    Closes the driver when exit the context

    Yields:
        Generator[WebDriver]: Chrome driver object
    """
    options: ChromeOptions = build_driver_options()

    driver = Chrome(options=options)
    try:
        driver.maximize_window()

        yield driver
    finally:
        driver.quit()


def clear_resources() -> None:
    """Setup resources directory for data persistence"""
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
    """Automate login to the user web portal

    Args:
        driver (WebDriver): Chrome driver object
    """
    driver.get(Secrets.LOGIN_URL)
    driver.find_element(By.ID, Locators.USER_INPUT_ID).send_keys(Secrets.USERNAME)
    driver.find_element(By.ID, Locators.PASSWORD_INPUT_ID).send_keys(Secrets.PASSWORD)
    driver.find_element(By.ID, Locators.LOGIN_BTN_ID).click()

    check_login(driver)

@timeout_retry()
def check_login(driver: WebDriver) -> None:
    """Checks if the login completed successfully

    Args:
        driver (WebDriver): Chrome driver object

    Raises:
        Exception: Raised if the current URL doesn't match the Portal Home URL
    """
    if Secrets.HOME_URL in driver.current_url:
        return

    raise Exception


@timeout_retry()
def get_current_amount(driver: WebDriver) -> None:
    """Collect current account amount and save it in a file

    Args:
        driver (WebDriver): Chrome driver object
    """
    account_amount: str = driver.find_element(By.CLASS_NAME, Locators.AMOUNT_TEXT_CLASS).text
    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(account_amount.replace(".", "").replace("$", "").strip())


def get_credit_transactions(driver: WebDriver) -> None:
    """Collect current transactions on credit card

    Args:
        driver (WebDriver): Chrome driver object
    """
    driver.get(Secrets.CREDIT_TRANSACTIONS_URL)
    check_credit_transactions(driver)


@timeout_retry()
def check_credit_transactions(driver: WebDriver) -> None:
    """Try to download credit card transactions

    Args:
        driver (WebDriver): Chrome driver object
    """
    driver.find_element(By.XPATH, Locators.GROUP_BTN_XPATH).click()
    driver.find_element(By.XPATH, Locators.DOWNLOAD_BTN_XPATH).click()
    time.sleep(3)


@timeout_retry()
def logout(driver: WebDriver) -> None:
    """Performs logout for Web portal

    Args:
        driver (WebDriver): Chrome driver object
    """
    driver.find_element(By.CLASS_NAME, Locators.LOGOUT_BTN_CLASS).click()


if __name__ == "__main__":
    main()
