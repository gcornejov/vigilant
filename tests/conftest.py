from unittest import mock

import pytest


@pytest.fixture
def mock_page() -> mock.MagicMock:
    return mock.MagicMock()
