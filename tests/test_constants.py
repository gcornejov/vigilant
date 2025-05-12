import os
from typing import Final

from vigilant.constants import MetaSecrets

def test_secrets_metaclass() -> None:
    os.environ["ENV_TEST"] = "test_value"

    class Secrets(metaclass=MetaSecrets):
        TEST_ENV: Final[str] = "ENV_TEST"

    assert Secrets.TEST_ENV == "test_value"
