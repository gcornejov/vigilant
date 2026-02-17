from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict


# TODO: Config prefix
class Secrets(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="CHILE_", extra="ignore"
    )

    USERNAME: str
    PASSWORD: str

    LOGIN_URL: str
    HOME_URL: str
    CREDIT_TRANSACTIONS_URL: str


secrets = Secrets()


class Locators:
    USER_INPUT_ID: Final[str] = "#ppriv_per-login-click-input-rut"
    PASSWORD_INPUT_ID: Final[str] = "#ppriv_per-login-click-input-password"
    LOGIN_BTN_ID: Final[str] = "#ppriv_per-login-click-ingresar-login"

    PROMOTION_BANNER_CLASS: Final[str] = ".fondo"
    AMOUNT_TEXT_CLASS: Final[str] = ".monto-cuenta"
    DOWNLOAD_TOAST_CLASS: Final[str] = ".snackbar-text"
    LOGOUT_BTN_CLASS: Final[str] = ".button-logout"

    BANNER_CLOSE_BTN_XPATH: Final[str] = (
        '//*[@id="mat-dialog-0"]/fenix-modal-zona-emergente/div/div/div/button'
    )
    DOWNLOAD_GROUP_BTN_XPATH: Final[str] = (
        '//*[@id="mat-tab-content-1-0"]/div/fenix-movimientos-no-facturados-tabla/div[1]/div[1]/div[2]/bch-button'
    )
    DOWNLOAD_BTN_XPATH: Final[str] = '//*[@id="cdk-overlay-0"]/div/div/button[1]'


class IOResources:
    TRANSACTIONS_FILENAME: Final[str] = "transactions.xls"
    OUTPUT_FILENAME: Final[str] = "banco_chile.json"
