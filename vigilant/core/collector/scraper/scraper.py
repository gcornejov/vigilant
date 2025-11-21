from abc import ABC, abstractmethod

from playwright.sync_api import Page


class Scraper(ABC):
    page: Page

    def __init__(self, page: Page):
        self.page = page

    @abstractmethod
    def scrap(self) -> None: ...
