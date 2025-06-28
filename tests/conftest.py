from collections.abc import Generator
from unittest import mock

import pytest


@pytest.fixture
def mock_driver() -> Generator[mock.MagicMock]:
    return mock.MagicMock()
