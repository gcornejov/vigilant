from unittest import mock

import httpx
from fastapi import testclient

from vigilant.app import app
from vigilant.common.exceptions import VigilantException

client = testclient.TestClient(app)


@mock.patch("vigilant.app.run")
def test_update_expenses(run_mock: mock.Mock) -> None:
    response: httpx.Response = client.post("/update-expenses")

    run_mock.assert_called_once()
    assert response.status_code == 200
    assert response.json() == "Ok"


@mock.patch("vigilant.app.run", mock.Mock(side_effect=VigilantException))
def test_update_expenses_bad() -> None:
    response: httpx.Response = client.post("/update-expenses")

    assert response.status_code == 500
    assert "details" in response.json()
