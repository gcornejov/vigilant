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
    mock_scraper: Type[Scraper],
) -> None:
    collector.scrapers = [mock_scraper]
    collector.collect()

    driver_session.assert_called_once()
    clear_resources.assert_called_once()


def test_clear_resources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tmp_file: Path = tmp_path / "test_file.txt"
    tmp_file.write_text("Hesitation is defeat!")

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    collector.clear_resources()

    assert tmp_path.exists() and not any(tmp_path.iterdir())
