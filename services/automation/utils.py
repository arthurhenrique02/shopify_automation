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

from services.automation.auth import conn_gmail_imap
from services.automation.navigation import (
    open_create_app_page,
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

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[@class='Polaris-Layout']//div[@class='Polaris-LegacyStack__Item']//a[contains(@class, 'Polaris-Button')]",
            )
        )
    ).click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[@class='Polaris-Layout']//div[@class='Polaris-ButtonGroup__Item']//button[@type='button']",
            )
        )
    ).click()


def create_custom_app(driver: WebDriver) -> bool:
    """
    Create a custom app in the Shopify admin page. On creation, redirect to the app's page.
    :param driver: Selenium WebDriver instance
    :return: True if successful, False otherwise
    """

    # click to create a new app
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@class='Polaris-Layout']//div[@class='Polaris-InlineStack']//button[contains(@class, 'Polaris-Button') and @type='button']",
                )
            )
        ).click()
    except TimeoutException:
        # an app already exists, need to click the button to create a new one
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@class='Polaris-Page']//div[contains(@class, 'Polaris-Box')]//button[contains(@class, 'Polaris-Button') and @type='button']",
                )
            )
        ).click()
    except Exception as e:
        print(f"An error occurred while trying to create a custom app: {e}")
        return False

    # get input and type the app name and save
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[@class='Polaris-Modal-Dialog__Modal']//div[contains(@class, 'Polaris-FormLayout__Item')]//input[@class='Polaris-TextField__Input']",
            )
        )
    ).send_keys("Automation Custom App")

    # curr url to check his changes after app created and redirected to his page
    curr_url = driver.current_url

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[@class='Polaris-Modal-Dialog__Modal']//div[@class='Polaris-InlineStack']//button[contains(@class, 'Polaris-Button')][2]",
            )
        )
    ).click()

    try:
        # detect url changes
        WebDriverWait(driver, 10).until(EC.url_changes(curr_url))
    except TimeoutException:
        print("Failed to detect URL change after creating the app.")
        return False

    return True


def define_custom_app_permissions(driver: WebDriver) -> bool:
    """
    Define the permissions for the custom app in the Shopify admin page. On success, it will redirect to the app's credentials page.
    :param driver: Selenium WebDriver instance
    :return: True if successful, False otherwise
    """

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[@class='Polaris-LegacyCard']//div[contains(@class,'Polaris-LegacyCard__Section')]//a[contains(@class, 'Polaris-Button')][1]",
            )
        )
    ).click()

    checkboxes = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (
                By.XPATH,
                "//input[@type='checkbox' and contains(@class, 'Polaris-Checkbox__Input')]",
            )
        )
    )

    for checkbox in checkboxes:
        if checkbox.is_selected():
            continue

        checkbox.click()

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//div[@class='Polaris-LegacyStack__Item']//div[@class='Polaris-ButtonGroup']//button[contains(@class, 'Polaris-Button') and @type='button']",
                )
            )
        )[-1].click()
    except TimeoutException:
        print("Failed to click the save button for permissions.")
        return False

    return True


def get_custom_app_api_key(driver: WebDriver) -> str:
    """
    Get the custom app API key from the Shopify admin page.
    :param driver: Selenium WebDriver instance
    :return: Custom app API key as a string
    """

    SLEEP_TIME = 5
    SHORT_SLEEP_TIME = 1

    old_handler = open_create_app_page(driver)

    driver.switch_to.window(driver.window_handles[-1])

    try:
        enable_custom_dev_mode(driver)
    except TimeoutException:
        print("Development mode is already enabled.")
    except Exception as e:
        print(f"An error occurred while enabling development mode: {e}")
        return ""

    success = create_custom_app(driver)

    if not success:
        print("Failed to create custom app. Please check your credentials.")
        driver.quit()
        return ""

    success = define_custom_app_permissions(driver)

    if not success:
        print("Failed to define custom app permissions. Please check your credentials.")
        driver.quit()
        return ""

    cred_url = "/".join([*driver.current_url.split("/")[:-2], "api_credentials"])

    # wait to ensure the page will be correctly loaded when redirect
    # (button to install will appear)
    time.sleep(SLEEP_TIME)
    driver.get(cred_url)

    # click to install app
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                (
                    "//div[@class='Polaris-Layout']//div[@class='Polaris-LegacyStack__Item']"
                    "//button[contains(@class, 'Polaris-Button') and @type='button']"
                ),
            )
        )
    ).click()

    # confirm app installation in modal
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                (
                    "//div[@class='Polaris-Modal-Dialog__Modal']//div[@class='Polaris-InlineStack']"
                    "//button[contains(@class, 'Polaris-Button') and @type='button'][2]"
                ),
            )
        )
    ).click()

    # wait app installation
    time.sleep(SLEEP_TIME)

    api_key_section_xpath = (
        "//div[@class='Polaris-Layout']//div[@class='Polaris-LegacyStack__Item']"
        "//div[@class='Polaris-Connected']"
    )

    # reveal API key
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"{api_key_section_xpath}//button[contains(@class, 'Polaris-Button') and @type='button']",
            )
        )
    ).click()

    time.sleep(SHORT_SLEEP_TIME)

    # get the API key
    api_key = (
        WebDriverWait(driver, 10)
        .until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"{api_key_section_xpath}//input[contains(@class, 'Polaris-TextField__Input')]",
                )
            )
        )
        .get_attribute("value")
    )

    if not api_key:
        print("Failed to retrieve the API key.")
        driver.quit()
        return ""

    driver.quit()
    driver.switch_to.window(old_handler)

    return api_key
