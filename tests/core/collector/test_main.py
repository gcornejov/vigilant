from pathlib import Path
from typing import Type
from unittest import mock

import pytest

from vigilant.core.collector import main as collector
from vigilant.core.collector.scraper.scraper import Scraper


@pytest.fixture
def mock_scraper() -> Type[Scraper]:
    class MockScraper(Scraper):
        def navigate(self): ...

    return MockScraper


@mock.patch("vigilant.core.collector.main.session")
@mock.patch("vigilant.core.collector.main.clear_resources")
def test_collect(
    driver_session: mock.MagicMock,
    clear_resources: mock.MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_scraper: Type[Scraper],
) -> None:
    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    collector.scrapers = [mock_scraper]
    collector.collect()

    driver_session.assert_called_once()
    clear_resources.assert_called_once()
