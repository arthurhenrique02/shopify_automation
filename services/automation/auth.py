import imaplib
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .handlers import check_2fa, check_google_vinculation, check_non_existent_account
from .utils import find_submit_button


def login(driver: WebDriver, username: str, password: str):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "account_email"))
    ).send_keys(username)

    find_submit_button(driver=driver).click()

    # check for possible login issues
    check_non_existent_account(driver)
    check_google_vinculation(driver)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "account_password"))
    ).send_keys(password)

    find_submit_button(driver=driver).click()
    check_2fa(driver)


def conn_gmail_imap() -> imaplib.IMAP4_SSL | None:
    """
    Connect to Gmail using IMAP.
    :return: IMAP connection object
    """
    try:
        email = os.getenv("EMAIL_TO_RECEIVE_KEYS")
        password = os.getenv("EMAIL_RECEIVER_PASS")

        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(email, password)
        imap.select("inbox")
        return imap
    except imaplib.IMAP4.error as e:
        # TODO: CHANGE TO LOGGER
        print(f"IMAP error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
