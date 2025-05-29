import random
import shutil
import tempfile
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Final

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from vigilant import logger
from vigilant.constants import Locators, Secrets, IOResources

DEFAULT_TIMEOUT: Final[float] = 15.0
DEFAULT_DOWNLOAD_TIMEOUT: Final[float] = 3.0


def main() -> None:
    """Collect account data"""
    with driver_session() as driver:
        clear_resources()

        logger.info("Logging in ...")
        login(driver)

        logger.info("Getting current amount ...")
        get_current_amount(driver)

        logger.info("Getting transactions ...")
        get_credit_transactions(driver)

        logger.info("Logging out ...")
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
        driver.implicitly_wait(DEFAULT_TIMEOUT)
        driver.maximize_window()

        yield driver
    except Exception as e:
        logger.error(e)
        logger.error(type(e))

        take_screenshot(driver)

        raise Exception
    finally:
        driver.quit()


def take_screenshot(driver: Chrome) -> None:
    """Takes a screenshot of the browser window and saves it in a tmp file.

    Args:
        driver (Chrome): Chrome driver object
    """
    screenshot_path: str = tempfile.mktemp(suffix=".png")
    driver.get_screenshot_as_file(screenshot_path)

    logger.info(f"\N{camera} Browser screenshot saved at: {screenshot_path}")

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
    account_amount: str = driver.find_element(By.CLASS_NAME, Locators.AMOUNT_TEXT_CLASS).text
    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(account_amount.replace(".", "").replace("$", "").strip())


def get_credit_transactions(driver: WebDriver) -> None:
    """Collect current transactions on credit card

    Args:
        driver (WebDriver): Chrome driver object
    """
    driver.get(Secrets.CREDIT_TRANSACTIONS_URL)

    driver.find_element(By.XPATH, Locators.GROUP_BTN_XPATH).click()
    driver.find_element(By.XPATH, Locators.DOWNLOAD_BTN_XPATH).click()

    check_condition_timeout(lambda: list(IOResources.DATA_PATH.glob("*.xls")), DEFAULT_DOWNLOAD_TIMEOUT)


def logout(driver: WebDriver) -> None:
    """Logout from Web portal

    Args:
        driver (WebDriver): Chrome driver object
    """
    wait = WebDriverWait(driver, timeout=DEFAULT_TIMEOUT)
    wait.until(lambda _: not driver.find_elements(By.CLASS_NAME, "snackbar-text"))

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
