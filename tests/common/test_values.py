import os
from typing import Final

from vigilant.common.values import MetaEnvironment


def test_environment_metaclass() -> None:
    os.environ["ENV_TEST"] = "test_value"

    class Environment(metaclass=MetaEnvironment):
        TEST_ENV: Final[str] = "ENV_TEST"

    assert Environment.TEST_ENV == "test_value"
