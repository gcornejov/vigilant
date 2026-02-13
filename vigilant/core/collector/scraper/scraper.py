import random
import string
from abc import ABC, abstractmethod
from pathlib import Path

from playwright.sync_api import Page

from vigilant.common.values import IOResources


class Scraper(ABC):
    def __init__(self, page: Page):
        self.page = page
        self.data_path: Path = IOResources.DATA_PATH / "".join(
            random.choices((string.ascii_letters + string.digits), k=7)
        )

    def scrap(self) -> None:
        self.data_path.mkdir(parents=True, exist_ok=True)

        self.navigate()

    @abstractmethod
    def navigate(self) -> None: ...
