from unittest import mock

from vigilant import run

@mock.patch("vigilant.run.data_collector")
@mock.patch("vigilant.run.update_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    data_collector: mock.MagicMock,
) -> None:
    run.main()

    data_collector.main.assert_called_once()
    update_balance_spreadsheet.main.assert_called_once()
