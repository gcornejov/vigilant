from unittest import mock

from playwright.sync_api import Page

from vigilant.collector.scraper.scraper import Scraper, SpreadsheetConfig
from vigilant.common.models import AccountData, Transaction


class DummyScraper(Scraper):
    spreadsheet_config = SpreadsheetConfig(
        WORKSHEET_NAME="Sheet1",
        AMOUNT_CELL="A1",
        TRANSACTIONS_CELL="B1",
        UPDATE_DATE_CELL="C1",
        RUN_STATUS_CELL="D1",
    )

    def navigate(self) -> None: ...

    @property
    def account_data(self) -> AccountData:
        return AccountData(
            identifier="Dummy",
            amount=42,
            transactions=[
                Transaction(
                    date="01/01/2020", description="Clothes", location="", amount=25000
                ),
                Transaction(
                    date="02/01/2020", description="Food", location="", amount=40000
                ),
            ],
        )


@mock.patch("vigilant.collector.scraper.scraper.SpreadSheet")
def test_upload_writes_account_data_to_spreadsheet(
    MockSpreadSheet: mock.MagicMock,
) -> None:
    spreadsheet = mock.MagicMock()
    MockSpreadSheet.load.return_value = spreadsheet

    mock_page = mock.MagicMock(spec=Page)
    scraper = DummyScraper(mock_page)

    scraper.upload()

    MockSpreadSheet.load.assert_called_once()
    assert spreadsheet.write.call_count == 2

    spreadsheet.write.assert_any_call(
        "Sheet1",
        "A1",
        [[42]],
    )

    _, _, transactions = spreadsheet.write.call_args_list[1][0]
    assert len(transactions) == 100
    assert transactions[0] == ["01/01/2020", "Clothes", "", 25000]
    assert transactions[1] == ["02/01/2020", "Food", "", 40000]
    assert transactions[2:] == [["", "", "", ""]] * 98
