from unittest import mock

import vigilant

@mock.patch("vigilant.run.data_collector")
@mock.patch("vigilant.run.update_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    data_collector: mock.MagicMock,
) -> None:
    vigilant.run()

    data_collector.main.assert_called_once()
    update_balance_spreadsheet.main.assert_called_once()
