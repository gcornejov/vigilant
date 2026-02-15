from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Final

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    async_playwright,
)

from vigilant import logger
from vigilant.common.exceptions import DriverException
from vigilant.common.storage import GoogleCloudStorage, LocalStorage
from vigilant.common.values import (
    Environment,
    IOResources,
    StorageLocation,
)

WAIT_TIMEOUT: Final[float] = 20000.0

storage = (
    GoogleCloudStorage()
    if Environment.STORAGE_LOCATION == StorageLocation.GCS
    else LocalStorage()
)


@asynccontextmanager
async def session() -> AsyncGenerator[Page, None]:
    """Async context manager for Playwright browser session.

    Each call creates a new browser instance with a context and page.
    """
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(
            channel="chrome",
        )
        context: BrowserContext = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36",
        )
        page: Page = await context.new_page()
        page.set_default_timeout(WAIT_TIMEOUT)

        try:
            yield page
        except Exception as e:
            logger.exception(e)
            screenshot_path: str = await _take_screenshot(page)

            raise DriverException(screenshot_path)
        finally:
            await browser.close()


async def _take_screenshot(page: Page) -> str:
    """Takes a screenshot of the browser window and saves it in storage.

    Args:
        page (Page): Chrome page object
    """
    date_now: str = datetime.now().strftime("%Y%m%d%H%M%S")
    screenshot_path: str = f"{IOResources.SCREENSHOTS_PATH}/browser-{date_now}.png"

    image_data: bytes = await page.screenshot(full_page=True)
    saved_path: str = storage.save_image(image_data, screenshot_path)

    logger.info(f"\N{CAMERA} Browser screenshot saved at: {saved_path}")
    return saved_path
