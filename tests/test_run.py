from unittest import mock

from vigilant import run


@mock.patch("vigilant.run.collector")
def test_main(
    collector: mock.MagicMock,
) -> None:
    run.main()

    collector.collect.assert_called_once()
