import imaplib
import os
import typing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from services.automation.navigation import (
    open_theme_access_download_page,
)


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver


def find_submit_button(driver: WebDriver) -> WebElement:
    """
    Find the submit button on the Shopify login page.
    :param driver: Selenium WebDriver instance
    :return: WebElement representing the submit button
    """
    return WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )


def find_app_link(driver: WebDriver) -> WebElement:
    """
    Find the app navigation button on the Shopify admin page.
    :param driver: Selenium WebDriver instance
    :return: WebElement representing the app navigation button
    """
    return WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='_Button_1g3wt_32' and span[text()='Apps']]")
        )
    )


def open_app_search_bar(driver: WebDriver):
    """
    Open the app search bar in the Shopify admin page.
    :param driver: Selenium WebDriver instance
    """
    find_app_link(driver).click()


def download_theme_access(driver: WebDriver) -> tuple[bool, str]:
    """
    Download the theme access from the Shopify admin page.
    :param driver: Selenium WebDriver instance
    """
    old_handler = open_theme_access_download_page(driver)

    install_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@id='analytics-viewItem']/form/button")
        )
    )

    install_btn.click()

    # if downloaded, just go to the new tab
    if install_btn.text.strip().lower() in ["open", "abrir"]:
        driver.switch_to.window(driver.window_handles[-1])
        return True, old_handler

    driver.switch_to.window(driver.window_handles[-1])

    # click to install
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[@class='Polaris-InlineStack']/button[2]",
            )
        )
    ).click()

    return True, old_handler


def create_theme_access_password(driver: WebDriver) -> str:
    """
    Get the theme access password from the Shopify admin page.
    :param driver: Selenium WebDriver instance
    :return: Theme access password as a string
    """
    driver.switch_to.frame(
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//iframe"))
        )
    )

    # click create token link
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@class='Polaris-InlineStack_bc7jt']/a[2]")
        )
    ).click()

    inputs = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//form//input"))
    )

    for ie in inputs:
        if ie.get_attribute("type") == "text":
            ie.send_keys("Automation Theme Access")
        elif ie.get_attribute("type") == "email":
            ie.send_keys(os.getenv("EMAIL_TO_RECEIVE_KEYS"))

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//form//div[@class='Polaris-LegacyStack__Item_yiyol']//button[@type='submit']",
            )
        )
    ).click()

    return True


def get_theme_access_password_from_email(driver: WebDriver) -> str:
    """
    Get the theme access password from the email.
    :param driver: Selenium WebDriver instance
    :return: Theme access password as a string
    """

    # TODO GET TOKEN FROM EMAIL
    mailbox = conn_gmail_imap()


def conn_gmail_imap() -> typing.Generator[imaplib.IMAP4_SSL, None, None]:
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
        yield imap
    except imaplib.IMAP4.error as e:
        # TODO: CHANGE TO LOGGER
        print(f"IMAP error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if not imap.closed:
            print("No IMAP connection to close.")
            return

        imap.logout()
        print("IMAP connection closed.")
