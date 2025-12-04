from pathlib import Path
from unittest import mock

import pytest

from vigilant.common.values import IOResources
from vigilant.core.collector.scraper.cmr.values import Locators
from vigilant.core.collector.scraper import CMRScraper


@mock.patch("vigilant.core.collector.scraper.CMRScraper._login")
@mock.patch("vigilant.core.collector.scraper.CMRScraper._get_credit_transactions")
def test_scrap(
    _login: mock.MagicMock,
    _get_credit_transactions: mock.MagicMock,
    mock_page: mock.MagicMock,
) -> None:
    CMRScraper(mock_page).scrap()

    _login.assert_called_once()
    _get_credit_transactions.assert_called_once()


def test_login(mock_page: mock.MagicMock) -> None:
    mock_login_btn, mock_user_input, mock_password_input, mock_generic_locator = (
        mock.MagicMock(),
        mock.MagicMock(),
        mock.MagicMock(),
        mock.MagicMock(),
    )

    def mock_login_form_locators(mock_selector: str = "") -> mock.MagicMock:
        match mock_selector:
            case Locators.LOGIN_FORM_BTN_XPATH:
                return mock_login_btn
            case Locators.USER_INPUT_XPATH:
                mock_locator = mock.MagicMock()
                mock_locator.first = mock_user_input
                return mock_locator
            case Locators.PASSWORD_INPUT_XPATH:
                mock_locator = mock.MagicMock()
                mock_locator.first = mock_password_input
                return mock_locator
            case Locators.PASSWORD_INPUT_XPATH:
                return mock_password_input
            case _:
                return mock_generic_locator

    mock_page.locator = mock.MagicMock(side_effect=mock_login_form_locators)

    CMRScraper(mock_page)._login()

    mock_page.goto.assert_called_once()
    mock_page.wait_for_load_state()

    mock_login_btn.wait_for.assert_called_once()
    mock_login_btn.click.assert_called_once()

    mock_user_input.wait_for.assert_called_once()
    mock_user_input.fill.assert_called_once()

    mock_password_input.wait_for.assert_called_once()
    mock_password_input.fill.assert_called_once()

    mock_generic_locator.first.click.assert_called_once()
    mock_page.wait_for_url.assert_called_once()


def test_get_credit_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_page: mock.MagicMock
) -> None:
    (tmp_path / IOResources.TRANSACTIONS_FILENAME).write_text("Hesitation is defeat!")

    monkeypatch.setattr("vigilant.common.values.IOResources.DATA_PATH", tmp_path)

    mock_download_info = mock.MagicMock()
    mock_page.expect_download.return_value.__enter__.return_value = mock_download_info

    CMRScraper(mock_page)._get_credit_transactions()

    mock_page.locator().wait_for.assert_called_once()
    mock_page.locator().click.assert_called()
    mock_download_info.value.save_as.assert_called_once_with(
        IOResources.DATA_PATH / IOResources.TRANSACTIONS_FILENAME
    )
