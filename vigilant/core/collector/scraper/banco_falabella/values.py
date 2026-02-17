from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="FALABELLA_",
        extra="ignore",
    )

    USERNAME: str
    PASSWORD: str

    LOGIN_URL: str
    HOME_URL: str


secrets = Secrets()


class Locators:
    LOGIN_SUBMIT_BTN_ID: Final[str] = "#desktop-login"

    PRODUCT_BTN_CLASS: Final[str] = ".div-product"
    DOWNLOAD_BTN_CLASS: Final[str] = ".btn-doc-export"
    CLOSE_BANNER_BTN_CLASS: Final[str] = ".close-button"

    LOGIN_FORM_BTN_XPATH: Final[str] = (
        '//*[@id="main-header__sub-content"]/div[3]/button[3]'
    )
    USER_INPUT_XPATH: Final[str] = (
        '//*[@id="auth-form"]/div[2]/div/div[2]/div[1]/div/input'
    )
    PASSWORD_INPUT_XPATH: Final[str] = (
        '//*[@id="auth-form"]/div[2]/div/div[2]/div[2]/div/input'
    )
    PROMOTION_BANNER_XPATH: Final[str] = '//*[@id="shadow-container"]'


class IOResources:
    TRANSACTIONS_FILENAME: Final[str] = "transactions.xls"
    OUTPUT_FILENAME: Final[str] = "banco_falabella.json"
