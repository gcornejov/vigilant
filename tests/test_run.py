from unittest import mock

from vigilant import run


@mock.patch("vigilant.run.collector")
@mock.patch("vigilant.run.update_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    collector: mock.MagicMock,
) -> None:
    run.main()

    collector.collect.assert_called_once()
    update_balance_spreadsheet.main.assert_called_once()
