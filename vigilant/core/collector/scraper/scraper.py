from abc import ABC, abstractmethod
from pathlib import Path

from playwright.sync_api import Page


class Scraper(ABC):
    directory: Path

    def __init__(self, page: Page):
        self.page = page

    def scrap(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        self.navigate()

    @abstractmethod
    def navigate(self) -> None: ...
