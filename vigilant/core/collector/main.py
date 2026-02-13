from typing import Type

from vigilant import logger
from vigilant.common.browser import session
from vigilant.common.storage import clear_resources
from vigilant.core.collector.scraper import (
    BancoChileScraper,
    BancoFalabellaScraper,
    Scraper,
)

scrapers: list[Type[Scraper]] = [BancoChileScraper, BancoFalabellaScraper]


def collect() -> None:
    """Collect accounts data"""
    with session() as page:
        clear_resources()

        logger.info("Collecting transactions data ...")
        for SPR in scrapers:
            SPR(page).scrap()


if __name__ == "__main__":
    collect()
