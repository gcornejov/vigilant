from pathlib import Path
from typing import Type
from unittest import mock

import pytest

from vigilant.core.collector import main as collector
from vigilant.core.collector.scraper.scraper import Scraper


@pytest.fixture
def mock_scraper() -> Type[Scraper]:
    class MockScraper(Scraper):
        async def navigate(self): ...

    return MockScraper


@pytest.mark.asyncio
@mock.patch("vigilant.core.collector.main.session")
@mock.patch("vigilant.core.collector.main.clear_resources")
async def test_collect(
    clear_resources_mock: mock.MagicMock,
    session_mock: mock.MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_scraper: Type[Scraper],
) -> None:
    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    # Create mock async context manager for session
    mock_page = mock.AsyncMock()
    session_mock.return_value.__aenter__.return_value = mock_page
    session_mock.return_value.__aexit__.return_value = None

    collector.scrapers = [mock_scraper]
    await collector.collect()

    clear_resources_mock.assert_called_once()
    session_mock.assert_called_once()
