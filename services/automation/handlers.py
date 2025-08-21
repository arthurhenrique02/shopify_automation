from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from services.automation.exceptions import (
    GoogleVinculationException,
    NonExistentAccountException,
    TwoFactorAuthException,
)


def check_2fa(driver: WebDriver) -> None:
    """
    Check if two-factor authentication is required.
    :param driver: Selenium WebDriver instance
    :raises TwoFactorAuthError: If two-factor authentication is required.
    :return: None
    """

    try:
        driver.find_element(By.NAME, "tfa_code")
        raise TwoFactorAuthException()
    except NoSuchElementException:
        return


def check_non_existent_account(driver: WebDriver) -> None:
    """
    Check if the account does not exist.
    :param driver: Selenium WebDriver instance
    :return: True if account does not exist, False otherwise
    """
    try:
        driver.find_element(By.CLASS_NAME, "new_account")
        raise NonExistentAccountException()
    except NoSuchElementException:
        return


def check_google_vinculation(driver: WebDriver) -> bool:
    """
    Check if Google account linkage is required.
    :param driver: Selenium WebDriver instance
    :return: True if Google account linkage is required, False otherwise
    """
    try:
        if driver.current_url.startswith("https://accounts.google.com"):
            raise GoogleVinculationException()
    except NoSuchElementException:
        return
