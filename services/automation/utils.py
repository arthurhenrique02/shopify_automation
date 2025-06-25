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

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@id='analytics-viewItem']/form/button")
        )
    ).click()

    driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[@class='Polaris-InlineStack']/button[2]",
            )
        )
    ).click()

    return True, old_handler


def get_theme_access_password(driver: WebDriver) -> str:
    """
    Get the theme access password from the Shopify admin page.
    :param driver: Selenium WebDriver instance
    :return: Theme access password as a string
    """

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@class='Polaris-InlineStack_bc7jt']/a[2]")
        )
    ).click()

    # TODO SEND CREDENTIALS EMAIL TO GET TOKEN
