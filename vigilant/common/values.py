import os
from pathlib import Path
from typing import Final


class MetaEnvironment(type):
    """
    A metaclass used to access a environment variable from a class attribute value
    """

    def __getattribute__(cls, name: str) -> str:
        env_var: str = str(object.__getattribute__(cls, name))

        return os.getenv(env_var, "")


class Environment(metaclass=MetaEnvironment):
    LOG_LEVEL: Final[str] = "LOG_LEVEL"
    STORAGE_LOCATION: Final[str] = "STORAGE_LOCATION"
    BUCKET_NAME: Final[str] = "BUCKET_NAME"


class IOResources:
    APP_ROOT_PATH: Final[Path] = Path("/var", "lib", "vigilant")
    SCREENSHOTS_PATH: Final[str] = "screenshots"

    DATA_DIR: Final[str] = "data_collection"
    DATA_PATH: Final[Path] = APP_ROOT_PATH / DATA_DIR


class BalanceSpreadsheet:
    KEY: Final[str] = "1IKyPmWeaZ_5IRa4I4EOgVwu5oGZ9RSQqQxjRu9P4qY4"

    DATA_WORKSHEET_NAME: Final[str] = "Data"

    PAYMENT_DESC_RANGE: Final[str] = "B3:B12"

    EXPENSES_WORKSHEET_NAME: Final[str] = "Gastos"

    AMOUNT_CELL: Final[str] = "I2"
    EXPENSES_CELL: Final[str] = "B3"


class StorageLocation:
    LOCAL: Final[str] = "local"
    GCS: Final[str] = "gcs"
