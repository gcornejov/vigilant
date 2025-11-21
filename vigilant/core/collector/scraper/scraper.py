from abc import ABC, abstractmethod

from playwright.sync_api import Page


class Scraper(ABC):
    def __init__(self, page: Page):
        self.page = page

    def scrap(self) -> None:
        self.navigate()

    @abstractmethod
    def navigate(self) -> None: ...
