from unittest import mock

from vigilant import run


@mock.patch("vigilant.run.collector.collect")
@mock.patch("vigilant.run.update_spreadsheet")
def test_main(
    update_balance_spreadsheet: mock.MagicMock,
    collect: mock.AsyncMock,
) -> None:
    run.main()

    collect.assert_called_once()
    update_balance_spreadsheet.main.assert_called_once()
