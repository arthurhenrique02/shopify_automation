import contextlib
import imaplib
import os
import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from services.automation.navigation import (
    open_theme_access_download_page,
)

LINK_TAG_RE = re.compile(r'<a href=3D"([^"]+)"[^>]*>.*Get password.*</a>', re.DOTALL)


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
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@class='Polaris-InlineStack_bc7jt']/a[2]")
            )
        ).click()
    except TimeoutException:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@class='Polaris-Box_375yx']//a")
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

    # set select value to en
    Select(driver.find_element(By.XPATH, "//form//select")).select_by_value("en")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//form//div[@class='Polaris-LegacyStack__Item_yiyol']//button[@type='submit']",
            )
        )
    ).click()

    return True


def get_theme_access_password_from_email(driver: WebDriver, store_name: str) -> str:
    """
    Get the theme access password from the email.
    :param driver: Selenium WebDriver instance
    :return: Theme access password as a string
    """

    # wait for the email to arrive
    time.sleep(15)

    mailbox = conn_gmail_imap()

    if not mailbox:
        print("Failed to connect to the mailbox.")
        return ""

    with contextlib.closing(mailbox) as imap:
        try:
            # Search for the email with the theme access password
            status, messages = imap.search(
                None,
                f'SUBJECT "{store_name}"',
            )

            if status != "OK":
                print("No messages found.")
                return ""

            latest_email_id = messages[0].split()[-1]

            # Fetch email body
            status, msg_data = imap.fetch(latest_email_id, "(RFC822)")
            if status != "OK":
                print("Failed to fetch email.")
                return ""

            email_body = msg_data[0][1].decode("utf-8")
            href_link = LINK_TAG_RE.search(email_body).group(1)

            if not href_link:
                print("No theme access link found in the email.")
                return ""

            # replace line breaks
            href_link = href_link.replace("\n", "").replace("=\r", "")

            driver.execute_script(f"window.open('{href_link}', '_blank');")

            # Wait for the new tab to open and switch to it
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

            driver.switch_to.window(driver.window_handles[-1])

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='Polaris-LegacyStack__Item_yiyol']//button[@type='button']",
                    )
                )
            ).click()

            # TODO: TEST IF WORKING & REMOVE TEST PRINTS
            # Get the theme access token from the page
            token_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class, 'Polaris-TextField_1spwi')]//input",
                    )
                )
            )
            return token_element.get_attribute("value")
        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
            return ""


def enable_custom_dev_mode(driver: WebDriver) -> bool:
    """
    Enable custom development mode in the Shopify admin page.
    :param driver: Selenium WebDriver instance
    :return: True if successful, False otherwise
    """
    try:
        # Navigate to the custom development mode page
        driver.get(
            "https://your-shopify-store.myshopify.com/admin/settings/development"
        )

        # Find and click the enable button
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(class, 'Polaris-Button')]")
                )
            ).click()
        except Exception:
            enable_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(class, 'Polaris-Button')]")
                )
            )
            href = enable_link.get_attribute("href")

        return True
    except Exception as e:
        print(f"Error enabling custom dev mode: {e}")
        return False


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
