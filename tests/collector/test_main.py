from pathlib import Path
from typing import Type
from unittest import mock

import pytest

from vigilant.collector import main as collector
from vigilant.collector.scraper.scraper import Scraper, SpreadsheetConfig


@pytest.fixture
def mock_scraper() -> Type[Scraper]:
    class MockScraper(Scraper):
        spreadsheet_config = SpreadsheetConfig(
            WORKSHEET_NAME="Sheet1",
            AMOUNT_CELL="A1",
            TRANSACTIONS_CELL="B1",
            UPDATE_DATE_CELL="C1",
            RUN_STATUS_CELL="D1",
        )

        def navigate(self): ...

        @property
        def account_data(self): ...

    return MockScraper


@mock.patch("vigilant.collector.scraper.scraper.SpreadSheet.load")
@mock.patch("vigilant.collector.main.session")
@mock.patch("vigilant.collector.main.clear_resources")
@mock.patch("vigilant.collector.main.Scraper.upload")
def test_collect(
    spreadsheet_load: mock.MagicMock,
    driver_session: mock.MagicMock,
    clear_resources: mock.MagicMock,
    upload: mock.MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_scraper: Type[Scraper],
) -> None:
    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)
    monkeypatch.setattr(
        "vigilant.common.values.collector.ENABLED_SCRAPERS", ["MockScraper"]
    )

    collector.SCRAPER_REGISTRY = {"MockScraper": mock_scraper}
    collector.collect()

    spreadsheet_load.assert_called_once()
    driver_session.assert_called_once()
    clear_resources.assert_called_once()
    upload.assert_called_once()
