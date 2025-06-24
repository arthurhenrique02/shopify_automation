from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
