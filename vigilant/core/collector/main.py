import asyncio
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


async def collect() -> None:
    """Collect accounts data in parallel"""
    clear_resources()

    logger.info("Collecting transactions data ...")

    # Create async tasks for each scraper
    tasks = []
    for SPR in scrapers:
        tasks.append(_run_scraper(SPR))

    # Run all scrapers concurrently
    await asyncio.gather(*tasks)


async def _run_scraper(scraper_class: Type[Scraper]) -> None:
    """Run a single scraper with its own browser session"""
    async with session() as page:
        await scraper_class(page).scrap()


if __name__ == "__main__":
    asyncio.run(collect())
