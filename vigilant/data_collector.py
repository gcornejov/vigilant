import shutil
import time
from contextlib import contextmanager
from collections.abc import Generator

from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from vigilant import Locators, Secrets, IOResources


def main() -> None:
    with driver_session() as driver:
        clear_resources()

        login(driver)
        account_amount: str = get_current_amount(driver)

        driver.get(Secrets.CREDIT_TRANSACTIONS_URL)
        time.sleep(7)
        driver.find_element(By.XPATH, Locators.GROUP_BTN_XPATH).click()
        driver.find_element(By.XPATH, Locators.DOWNLOAD_BTN_XPATH).click()

        time.sleep(5)
        driver.find_element(By.CLASS_NAME, Locators.LOGOUT_BTN_CLASS).click()

    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(account_amount.replace(".", "").replace("$", "").strip())



def clear_resources() -> None:
    shutil.rmtree(IOResources.DATA_PATH, ignore_errors=True)
    IOResources.DATA_PATH.mkdir(parents=True, exist_ok=True)


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


def login(driver: WebDriver) -> None:
    driver.get(Secrets.LOGIN_URL)
    driver.find_element(By.ID, Locators.USER_INPUT_ID).send_keys(Secrets.USERNAME)
    driver.find_element(By.ID, Locators.PASSWORD_INPUT_ID).send_keys(Secrets.PASSWORD)
    driver.find_element(By.ID, Locators.LOGIN_BTN_ID).click()


def get_current_amount(driver: WebDriver, timeout: int | float = 10) -> str:
    remaining_time: float = float(timeout)
    while remaining_time > 0:
        time_start = time.time()
        try:
            return driver.find_element(By.CLASS_NAME, Locators.AMOUNT_TEXT_CLASS).text
        except Exception:
            remaining_time -= time.time() - time_start
    
    raise Exception("Timeout Reached - Element took to much time to load")


if __name__ == "__main__":
    main()
