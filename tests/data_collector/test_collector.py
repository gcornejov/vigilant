from pathlib import Path
from typing import Type
from unittest import mock

import pytest

from vigilant.data_collector import DataCollector
from vigilant.data_collector.crawler import Crawler


@pytest.fixture
def mock_crawler() -> Type[Crawler]:
    class MockCrawler(Crawler):
        def crawl(self): ...

    return MockCrawler


@mock.patch("vigilant.data_collector.collector.driver_session")
@mock.patch("vigilant.data_collector.collector.DataCollector._clear_resources")
def test_collect(
    driver_session: mock.MagicMock,
    clear_resources: mock.MagicMock,
    mock_crawler: Type[Crawler],
) -> None:
    data_collector = DataCollector()
    data_collector.crawlers = [mock_crawler]
    data_collector.collect()

    driver_session.assert_called_once()
    clear_resources.assert_called_once()


def test_clear_resources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tmp_file: Path = tmp_path / "test_file.txt"
    tmp_file.write_text("Hesitation is defeat!")

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    DataCollector()._clear_resources()

    assert tmp_path.exists() and not any(tmp_path.iterdir())
