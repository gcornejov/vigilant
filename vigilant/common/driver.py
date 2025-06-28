from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions

from vigilant import logger
from vigilant.common.exceptions import DriverException
from vigilant.common.storage import GoogleCloudStorage, LocalStorage, Storage
from vigilant.common.values import Environment, IOResources, StorageLocation, Timeout

storage: Storage = (
    GoogleCloudStorage()
    if Environment.STORAGE_LOCATION == StorageLocation.GCS
    else LocalStorage()
)


@contextmanager
def driver_session(wait_timeout: float | None = None) -> Generator[Chrome]:
    """Creates a driver object to interact with a Chrome Browser instance.
    Closes the driver when exit the context

    Args:
        wait_timeout (float | None): Timeout in seconds for waiting on driver actions

    Raises:
        DriverException: When an error occurs during browser navigation

    Yields:
        Generator[Chrome]: Chrome driver object
    """
    options: ChromeOptions = _build_driver_options()

    driver = Chrome(options=options)
    try:
        driver.implicitly_wait(wait_timeout or Timeout.DEFAULT_TIMEOUT)
        driver.set_window_size(1920, 1080)

        yield driver
    except WebDriverException as e:
        logger.exception(e)
        screenshot_path: str = _take_screenshot(driver)

        raise DriverException(screenshot_path)
    finally:
        driver.quit()


def _build_driver_options() -> ChromeOptions:
    """Setup profile for Chrome instance

    Returns:
        ChromeOptions: Chrome profile object
    """
    options = ChromeOptions()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": IOResources.DATA_PATH.as_posix(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False,
        },
    )

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--verbose")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.92 Safari/537.36"
    )

    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-software-rasterizer")

    return options


def _take_screenshot(driver: Chrome) -> str:
    """Takes a screenshot of the browser window and saves it in storage

    Args:
        driver (Chrome): Chrome driver object

    Returns:
        str: Path where the screenshot was saved.
    """
    date_now: str = datetime.now().strftime("%Y%m%d%H%M%S")
    screenshot_path: str = f"{IOResources.SCREENSHOTS_PATH}/browser-{date_now}.png"

    image_data: bytes = driver.get_screenshot_as_png()
    saved_path: str = storage.save_image(image_data, screenshot_path)

    logger.info(f"\N{CAMERA} Browser screenshot saved at: {saved_path}")
    return saved_path
