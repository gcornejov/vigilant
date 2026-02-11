from typing import Final

from vigilant.common.values import MetaEnvironment


class Secrets(metaclass=MetaEnvironment):
    USERNAME: Final[str] = "CMR_PORTAL_USERNAME"
    PASSWORD: Final[str] = "CMR_PORTAL_PASSWORD"

    LOGIN_URL: Final[str] = "CMR_PORTAL_LOGIN_URL"
    HOME_URL: Final[str] = "CMR_PORTAL_HOME_URL"


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
