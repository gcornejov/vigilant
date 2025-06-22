from typing import Any, Type

import pytest

from vigilant.common import exceptions
from vigilant.common.exceptions import VigilantException


@pytest.mark.parametrize(
    "ExceptionClass, exc_args, message",
    (
        (
            exceptions.DriverException,
            ("tmp.png",),
            "Error encountered while navigating through browser. Check last state screenshot in: tmp.png",
        ),
        (exceptions.DownloadTimeout, ("1",), "Download timeout reached. (1 sec)"),
    ),
)
def test_exceptions_messages(
    ExceptionClass: Type[VigilantException], exc_args: tuple[Any], message: str
):
    exception: VigilantException = ExceptionClass(*exc_args)

    assert exception.message == message and str(exception) == message
