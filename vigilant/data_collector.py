import shutil
from collections.abc import Generator
from contextlib import contextmanager, suppress
from datetime import datetime
from typing import Final

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    TimeoutError,
    sync_playwright,
)

from vigilant import logger
from vigilant.common.exceptions import DriverException
from vigilant.common.storage import GoogleCloudStorage, LocalStorage
from vigilant.common.values import (
    Environment,
    IOResources,
    Locators,
    Secrets,
    StorageLocation,
)

WAIT_TIMEOUT: Final[float] = 20000.0

storage = (
    GoogleCloudStorage()
    if Environment.STORAGE_LOCATION == StorageLocation.GCS
    else LocalStorage()
)


def main() -> None:
    with session() as page:
        clear_resources()

        logger.info("Logging in ...")
        login(page)

        logger.info("Getting current amount ...")
        get_current_amount(page)

        logger.info("Getting transactions ...")
        get_credit_transactions(page)


@contextmanager
def session() -> Generator[Page]:
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(
            channel="chrome",
        )
        context: BrowserContext = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36",
        )
        page: Page = context.new_page()
        page.set_default_timeout(WAIT_TIMEOUT)

        try:
            yield page
        except Exception as e:
            logger.exception(e)
            screenshot_path: str = take_screenshot(page)

            raise DriverException(screenshot_path)
        finally:
            browser.close()


def take_screenshot(page: Page) -> str:
    """Takes a screenshot of the browser window and saves it in storage.

    Args:
        driver (Page): Chrome page object
    """
    date_now: str = datetime.now().strftime("%Y%m%d%H%M%S")
    screenshot_path: str = f"{IOResources.SCREENSHOTS_PATH}/browser-{date_now}.png"

    image_data: bytes = page.screenshot(full_page=True)
    saved_path: str = storage.save_image(image_data, screenshot_path)

    logger.info(f"\N{CAMERA} Browser screenshot saved at: {saved_path}")
    return saved_path


def clear_resources() -> None:
    """Setup resources directory for data persistence"""
    shutil.rmtree(IOResources.DATA_PATH, ignore_errors=True)
    IOResources.DATA_PATH.mkdir(parents=True, exist_ok=True)


def login(page: Page) -> None:
    """Login to Web portal

    Args:
        page (Page): Chrome page object
    """
    page.goto(Secrets.LOGIN_URL)

    page.locator(f"#{Locators.USER_INPUT_ID}").fill(Secrets.USERNAME)
    page.locator(f"#{Locators.PASSWORD_INPUT_ID}").fill(Secrets.PASSWORD)
    page.locator(f"#{Locators.LOGIN_BTN_ID}").click()

    page.wait_for_url(Secrets.HOME_URL)


def get_current_amount(page: Page) -> None:
    """Collect current account amount and save it in a file

    Args:
        driver (Page): Chrome page object
    """
    BANNER_WAIT_TIMEOUT: float = 3000.0

    with suppress(TimeoutError):
        page.locator(f".{Locators.PROMOTION_BANNER_CLASS}").wait_for(
            timeout=BANNER_WAIT_TIMEOUT
        )
        page.keyboard.press("Escape")

    account_amount: str = page.locator(
        f".{Locators.AMOUNT_TEXT_CLASS}"
    ).first.text_content()
    (IOResources.DATA_PATH / IOResources.AMOUNT_FILENAME).write_text(
        account_amount.replace(".", "").replace("$", "").strip()
    )


def get_credit_transactions(page: Page) -> None:
    """Collect current transactions on credit card

    Args:
        driver (Page): Chrome page object
    """
    page.goto(Secrets.CREDIT_TRANSACTIONS_URL)
    page.locator(Locators.DOWNLOAD_GROUP_BTN_XPATH).click()

    with page.expect_download() as download_info:
        page.locator(Locators.DOWNLOAD_BTN_XPATH).click()

    download_info.value.save_as(
        IOResources.DATA_PATH / IOResources.TRANSACTIONS_FILENAME
    )


if __name__ == "__main__":
    main()
