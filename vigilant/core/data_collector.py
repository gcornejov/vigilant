import shutil
from contextlib import suppress

from playwright.sync_api import (
    Page,
    TimeoutError,
)

from vigilant import logger
from vigilant.common.browser import session
from vigilant.common.values import (
    IOResources,
    Locators,
    Secrets,
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
