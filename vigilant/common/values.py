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


class Secrets(metaclass=MetaEnvironment):
    USERNAME: Final[str] = "PORTAL_USERNAME"
    PASSWORD: Final[str] = "PORTAL_PASSWORD"

    LOGIN_URL: Final[str] = "PORTAL_LOGIN_URL"
    HOME_URL: Final[str] = "PORTAL_HOME_URL"
    CREDIT_TRANSACTIONS_URL: Final[str] = "CREDIT_TRANSACTIONS_URL"


class Locators:
    USER_INPUT_ID: Final[str] = "ppriv_per-click-input-rut"
    PASSWORD_INPUT_ID: Final[str] = "ppriv_per-click-input-password"
    LOGIN_BTN_ID: Final[str] = "ppriv_per-click-ingresar-login"

    PROMOTION_BANNER_CLASS: Final[str] = "fondo"
    AMOUNT_TEXT_CLASS: Final[str] = "monto-cuenta"
    DOWNLOAD_TOAST_CLASS: Final[str] = "snackbar-text"
    LOGOUT_BTN_CLASS: Final[str] = "button-logout"

    BANNER_CLOSE_BTN_XPATH: Final[str] = (
        '//*[@id="mat-dialog-0"]/fenix-modal-zona-emergente/div/div/div/button'
    )
    DOWNLOAD_GROUP_BTN_XPATH: Final[str] = (
        '//*[@id="mat-tab-content-1-0"]/div/fenix-movimientos-no-facturados-tabla/div[1]/div[1]/div[2]/bch-button/div/button'
    )
    DOWNLOAD_BTN_XPATH: Final[str] = '//*[@id="cdk-overlay-0"]/div/div/button[1]'


class IOResources:
    APP_ROOT_PATH: Final[Path] = Path("/var", "lib", "vigilant")
    SCREENSHOTS_PATH: Final[str] = "screenshots"

    DATA_DIR: Final[str] = "data_collection"
    DATA_PATH: Final[Path] = APP_ROOT_PATH / DATA_DIR

    AMOUNT_FILENAME: Final[str] = "account_amount.txt"


class BalanceSpreadsheet:
    KEY: Final[str] = "1IKyPmWeaZ_5IRa4I4EOgVwu5oGZ9RSQqQxjRu9P4qY4"

    EXPENSES_WORKSHEET_NAME: Final[str] = "Gastos"

    AMOUNT_CELL: Final[str] = "I2"
    EXPENSES_CELL: Final[str] = "B3"


class StorageLocation:
    LOCAL: Final[str] = "local"
    GCS: Final[str] = "gcs"
