from typing import Type

from vigilant import logger
from vigilant.common.browser import session
from vigilant.common.storage import clear_resources
from vigilant.core.collector.scraper import (
    BancoChileScraper,
    BancoFalabellaScraper,
    Scraper,
)
from vigilant.common.values import collector


SCRAPER_REGISTRY: dict[str, Type[Scraper]] = {
    "BancoChile": BancoChileScraper,
    "BancoFalabella": BancoFalabellaScraper,
}


def get_enabled_scrapers() -> list[Type[Scraper]]:
    enabled = collector.ENABLED_SCRAPERS
    return [
        SCRAPER_REGISTRY[name.strip()]
        for name in enabled
        if name.strip() in SCRAPER_REGISTRY
    ]


def collect() -> None:
    """Collect accounts data"""
    with session() as page:
        clear_resources()

        logger.info("Collecting transactions data ...")
        for SPR in get_enabled_scrapers():
            SPR(page).scrap()


if __name__ == "__main__":
    collect()
