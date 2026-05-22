import logging
import random
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import Page

from vigilant import logger
from vigilant.common.models import AccountData
from vigilant.common.values import IOResources
from vigilant.common.spreadsheet import SpreadSheet
from vigilant.common.values import balance_spreadsheet


@dataclass
class SpreadsheetConfig:
    WORKSHEET_NAME: str
    AMOUNT_CELL: str
    TRANSACTIONS_CELL: str

    UPDATE_DATE_CELL: str
    RUN_STATUS_CELL: str


class Scraper(ABC):
    spreadsheet_config: SpreadsheetConfig

    def __init__(self, page: Page) -> None:
        self.page = page
        self.data_path: Path = IOResources.DATA_PATH / "".join(
            random.choices((string.ascii_letters + string.digits), k=7)
        )

        scraper_name = self.__class__.__name__
        self.logger = logging.LoggerAdapter(
            logger.getChild(scraper_name), {"role": "Scraper", "entity": scraper_name}
        )

    def scrap(self) -> None:
        self.data_path.mkdir(parents=True, exist_ok=True)

        self.navigate()
        self.upload()

        spreadsheet = SpreadSheet.load(balance_spreadsheet.KEY)
        spreadsheet.write(
            self.spreadsheet_config.WORKSHEET_NAME,
            self.spreadsheet_config.UPDATE_DATE_CELL,
            [
                [
                    datetime.now(ZoneInfo("America/Santiago")).strftime(
                        "%Y/%m/%d %H:%M:%S"
                    )
                ]
            ],
        )

    @abstractmethod
    def navigate(self) -> None: ...

    @property
    @abstractmethod
    def account_data(self) -> AccountData: ...

    def upload(self) -> None:
        """Uploads collected data into a google spreadsheet"""
        self.logger.info("Uploading data to spreadsheet ...")

        spreadsheet = SpreadSheet.load(balance_spreadsheet.KEY)

        spreadsheet.write(
            self.spreadsheet_config.WORKSHEET_NAME,
            self.spreadsheet_config.AMOUNT_CELL,
            [[self.account_data.amount]],
        )

        transactions = [trx.to_list() for trx in self.account_data.transactions]
        transactions.extend([["", "", "", ""]] * (100 - len(transactions)))

        spreadsheet.write(
            self.spreadsheet_config.WORKSHEET_NAME,
            self.spreadsheet_config.TRANSACTIONS_CELL,
            transactions,
        )
