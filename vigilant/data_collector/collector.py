import shutil
from typing import Type

from vigilant import logger
from vigilant.common.driver import driver_session
from vigilant.common.values import IOResources
from vigilant.data_collector.crawler import ChileCrawler, Crawler


class DataCollector:
    crawlers: list[Type[Crawler]]

    def __init__(self) -> None:
        self.crawlers = [ChileCrawler]

    def collect(self) -> None:
        """Collect accounts data"""
        with driver_session() as driver:
            self._clear_resources()

            logger.info("Collecting transactions data ...")
            for CWL in self.crawlers:
                CWL(driver).crawl()

    def _clear_resources(self) -> None:
        """Setup resources directory for data persistence"""
        shutil.rmtree(IOResources.DATA_PATH, ignore_errors=True)
        IOResources.DATA_PATH.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    DataCollector().collect()
